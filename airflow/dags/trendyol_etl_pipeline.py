import sys
sys.setrecursionlimit(10000)


from airflow import DAG
from airflow.operators.python import PythonOperator
from src.scraper import TrendyolScraper
from src.aws_s3 import S3Client
from src.cleaner import DataCleaner
from datetime import datetime, timedelta

FILE_PATH = "data/raw_data.csv"
OUTPUT_PATH = "data/cleaned_data.csv"

# Set default_args for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

# Define the DAG for extracting, transforming, and loading data
with DAG(
    'trendyol_etl_pipeline', 
    default_args=default_args,
    description='ETL pipeline for Trendyol data',
    schedule=None,  
    start_date=datetime(2024, 12, 13),
    catchup=False,
) as etl_dag:
    
    def extract_data():
        print("works")
        scraper = TrendyolScraper(output_file=FILE_PATH)
        scraper.run()

    def transform_data():
        cleaner = DataCleaner(file_path=FILE_PATH, output_path=OUTPUT_PATH)
        cleaner.clean()

    def load_data_to_s3():
        s3_client = S3Client()
        s3_client.upload_file(file_path=OUTPUT_PATH, bucket_name="s3-e-commerce-data")

    # Define the tasks
    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load_task = PythonOperator(
        task_id='load_data_to_s3',
        python_callable=load_data_to_s3,
    )

    # Set the task dependencies
    extract_task >> transform_task >> load_task
