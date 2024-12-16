from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Basit bir Python fonksiyonu
def hello_world():
    print("Hello, World!")

# DAG'ı tanımla
dag = DAG(
    'hello_world_dag',  # DAG adı
    description='Simple Hello World DAG',  # Açıklama
    schedule_interval=None,  # Manuel çalıştırılacak
    start_date=datetime(2024, 12, 15),  # Başlangıç tarihi
    catchup=False,  # Geçmiş tarihleri çalıştırma
)

# PythonOperator ile hello_world fonksiyonunu çalıştıran görev
hello_task = PythonOperator(
    task_id='hello_task',  # Görev adı
    python_callable=hello_world,  # Çalıştırılacak fonksiyon
    dag=dag,  # DAG ile ilişkilendir
)

hello_task  # Görevi başlat
