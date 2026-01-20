from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def print_hello():
    print("Hello from Daily Seongsu Crawler!")

default_args = {
    'owner': 'daily_seongsu',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_seongsu_hello_world',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
)

t1 = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)
