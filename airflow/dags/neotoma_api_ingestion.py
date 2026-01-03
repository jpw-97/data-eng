from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from datetime import datetime, timedelta
import requests
from google.cloud import storage
import json
import io
import os

PROJECT_ID = "neotoma-data-eng"
BUCKET = f"{PROJECT_ID}-epd-pollen-datasets"
BQ_DATASET = "raw"
BQ_TABLE = "raw-epd-pollen-datasets"


def fetch_epd_pollen_datasets():
    all_records = []
    offset = 0
    limit = 100

    # TODO: limited to EPD
    while True:
        params = {
            "database": "European Pollen Database",
            "datasettype": "pollen",
            "limit": 100,
            "offset": offset
        }

        response = requests.get(
            url="https://api.neotomadb.org/v2.0/data/datasets",
            headers={"Accept": "application/json"},
            params=params,
            timeout=30
        )
        response.raise_for_status()

        payload = response.json()
        batch = payload.get("data", [])

        if not batch:
            break

        all_records.extend(batch)
        offset += limit
    
    # upload raw JSON data to GCS -- overwrite TODO: review whether this update pattern is appropriate
    client = storage.Client()
    bucket = client.bucket(BUCKET)
    blob = bucket.blob("neotoma/epd_datasets/raw.json")

    ndjson_content = "\n".join([json.dumps(record) for record in all_records])
    
    blob.upload_from_string(
        ndjson_content,
        content_type="application/json"
    )

    print(f"Uploaded {len(all_records)} of EPD datasets to GCS")


with DAG(
    # TODO: refine general scheduling / deployment
    dag_id="epd-pollen-dataset-ingestion",
    catchup=False,
    tags=["epd-pollen-datasets"]
) as dag:

    fetch_epd_datasets_task = PythonOperator(
        task_id="fetch_epd_pollen_datasets",
        python_callable=fetch_epd_pollen_datasets
    )

    load_to_bq = GCSToBigQueryOperator(
        task_id="load_epd_pollen_datasets_bq",
        bucket=BUCKET,
        source_objects=["neotoma/epd_datasets/raw.json"],
        destination_project_dataset_table=f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}",
        source_format="NEWLINE_DELIMITED_JSON",
        autodetect=True,
        write_disposition="WRITE_TRUNCATE",
    )

    fetch_epd_datasets_task >> load_to_bq