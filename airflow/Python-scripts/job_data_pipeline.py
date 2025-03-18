############################# What this File does ##########################

############# Extracts job data from API → saves locally               ############# 
############# Uploads to Google Cloud Storage (GCS) in the raw/ folder ############# 
############# Loads JSON data from GCS → BigQuery staging_jobs         #############  

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.operators.bash import BashOperator
from google.cloud import storage
from datetime import datetime, timedelta
import requests
import json
import os
import time

# DAG default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# API & GCS Details
API_URL = "https://api.joinrise.io/api/v1/jobs/public?page=1&limit=100&sort=desc&sortedBy=createdAt"
BUCKET_NAME = "bucket-job_data"  # Change this to your GCS bucket
RAW_FILE_NAME = f"raw/job_data_{datetime.now().strftime('%Y%m%d')}.json"
LOCAL_FILE_PATH = f"/tmp/{RAW_FILE_NAME}"

# BigQuery Details
PROJECT_ID = "trans-envoy-314612"
DATASET_NAME = "job_data"
TABLE_NAME = "staging_jobs"

# Function to extract job data with retries
def extract_job_data():
    max_retries = 3
    retry_delay = 10  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(API_URL, timeout=30)
            response.raise_for_status()
            job_data = response.json()
            with open(LOCAL_FILE_PATH, "w") as f:
                json.dump(job_data, f)
            print(f"Successfully fetched job data on attempt {attempt + 1}")
            return
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise Exception("Failed to fetch job data after multiple attempts")

# Function to upload data to GCS
def upload_to_gcs():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(RAW_FILE_NAME)
    blob.upload_from_filename(LOCAL_FILE_PATH)
    print(f"Uploaded raw data: {RAW_FILE_NAME} to {BUCKET_NAME}")

# Define DAG
with DAG('job_data_pipeline',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    extract_task = PythonOperator(
        task_id='extract_job_data',
        python_callable=extract_job_data
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
    dbt_test = BashOperator(
        task_id='run_dbt_tests',
        bash_command='cd /Users/harinath/MyFolder/Projects/dataengineering-project/job_data_dbt && /Users/harinath/MyFolder/Projects/dataengineering-project/job_pipeline_env/bin/dbt test'
    )

    # Define task dependencies
    extract_task >> upload_task >> load_to_bq_task >> dbt_run >> dbt_test
