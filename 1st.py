from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from google.cloud import storage, bigquery
from datetime import datetime, timedelta
import requests
import json
import os

# DAG default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# API & GCS Details
API_URL = "https://api.joinrise.io/api/v1/jobs/public?page=1&limit=100&sort=desc&sortedBy=createdAt"
BUCKET_NAME = "bucket-job_data"  
RAW_FILE_NAME = f"raw/job_data_{datetime.now().strftime('%Y%m%d')}.json"
LOCAL_FILE_PATH = f"/tmp/{RAW_FILE_NAME}"

# BigQuery Details
PROJECT_ID = "trans-envoy-314612"
DATASET_NAME = "job_data"
TABLE_NAME = "staging_jobs"

# Function to extract job data
def extract_job_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        job_data = response.json()
        with open(LOCAL_FILE_PATH, "w") as f:
            json.dump(job_data, f)
    else:
        raise Exception("Failed to fetch job data")

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

    extract_task >> upload_task >> load_to_bq_task
