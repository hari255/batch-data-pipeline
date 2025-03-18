from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.operators.bash import BashOperator
from google.cloud import storage
from datetime import datetime, timedelta
import json
import os
import shutil

# DAG default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# File Paths
DAGS_FOLDER = "/Users/harinath/MyFolder/Projects/dataengineering-project/airflow/dags"
JOB_DATA_FILE = f"{DAGS_FOLDER}/job_data.json"  # Local job data file
BUCKET_NAME = "bucket-job_data"  # Change this to your GCS bucket
RAW_FILE_NAME = f"raw/job_data_{datetime.now().strftime('%Y%m%d')}.json"
LOCAL_FILE_PATH = f"/tmp/{RAW_FILE_NAME}"
PROCESSED_FILE_PATH = f"/tmp/processed_{RAW_FILE_NAME}"

# BigQuery Details
PROJECT_ID = "trans-envoy-314612"
DATASET_NAME = "job_data"
TABLE_NAME = "staging_jobs"

# Function to read job data from local file and preprocess it
def extract_and_preprocess_job_data():
    if not os.path.exists(JOB_DATA_FILE):
        raise FileNotFoundError(f"Job data file not found: {JOB_DATA_FILE}")

    # Load job data
    with open(JOB_DATA_FILE, 'r') as f:
        job_data = json.load(f)

    # Preprocess the job data
    processed_jobs = []
    for job in job_data.get('result', {}).get('jobs', []):
        # Initialize the processed job dictionary
        processed_job = {
            "id": job.get("_id"),
            "title": job.get("title"),
            "url": job.get("url"),
            "seniority": job.get("seniority"),
            "type": job.get("type"),
            "location": "",  # Default to empty string
            "company_name": job.get("owner", {}).get("companyName", ""),
            "company_location": job.get("owner", {}).get("location", ""),
            "company_type": job.get("owner", {}).get("type", ""),
            "created_at": job.get("createdAt"),
            "updated_at": job.get("updatedAt"),
            "expires_in": job.get("expiresIn"),
            "description": job.get("descriptionBreakdown", {}),
        }

        # Check if location is a dictionary, then extract the address if it exists
        location = job.get("location")
        if isinstance(location, dict):
            processed_job["location"] = location.get("address", "")

        # Append the processed job
        processed_jobs.append(processed_job)

    # Save processed data to a new file
    os.makedirs(os.path.dirname(PROCESSED_FILE_PATH), exist_ok=True)
    with open(PROCESSED_FILE_PATH, 'w') as f:
        json.dump({"jobs": processed_jobs}, f)
    
    print(f"Preprocessed job data saved to {PROCESSED_FILE_PATH}")


# Function to upload preprocessed data to GCS
def upload_to_gcs():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(RAW_FILE_NAME)
    blob.upload_from_filename(PROCESSED_FILE_PATH)
    print(f"Uploaded preprocessed data: {RAW_FILE_NAME} to {BUCKET_NAME}")

# Define DAG
with DAG('job_data_local_pipeline',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    extract_and_preprocess_task = PythonOperator(
        task_id='extract_and_preprocess_job_data',
        python_callable=extract_and_preprocess_job_data
    )

    upload_task = PythonOperator(
        task_id='upload_to_gcs',
        python_callable=upload_to_gcs
    )

    load_to_bq_task = GCSToBigQueryOperator(
        task_id='load_to_bigquery',
        bucket=BUCKET_NAME,
        source_objects=[RAW_FILE_NAME],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}",
        source_format="NEWLINE_DELIMITED_JSON",
        write_disposition="WRITE_TRUNCATE",
    )

    # Run dbt transformations
    dbt_run = BashOperator(
        task_id='run_dbt_models',
        bash_command='cd /Users/harinath/MyFolder/Projects/dataengineering-project/job_data_dbt && /Users/harinath/MyFolder/Projects/dataengineering-project/job_pipeline_env/bin/dbt run'
    )

    # Run dbt data quality tests

    # Define task dependencies
    extract_and_preprocess_task >> upload_task >> load_to_bq_task >> dbt_run
