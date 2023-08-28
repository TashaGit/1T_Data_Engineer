import decimal

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.hooks.base import BaseHook

from datetime import datetime, timedelta
import requests, csv
from urllib.parse import urlencode
import psycopg2
import pandas as pd


default_args = {
    "owner": "marina_z",
    'start_date': days_ago(1)
}


dag = DAG(dag_id='sample_superstore',
          tags=['marina_z'],
          start_date=datetime(2023, 7, 30),
          schedule_interval=None,
          default_args=default_args
)


variables = Variable.set(key='sales_variable',
                            value={'path': '/opt/airflow/raw_data',
                                   'csv_file_path': './raw_data/supermarket_1/sample_superstore.csv',
                                   'base_url': 'https://cloud-api.yandex.net/v1/disk/public/resources/download?',
                                   'public_key': 'https://disk.yandex.com.am/d/wMKRLK7gNL09Dg',
                                   'csv_github_path': 'https://raw.githubusercontent.com/mazavlia/1T_Data_Engineer/main/Theme_3_3_csv/Sample_Superstore.csv',
                                   'psql_raw_path': '/docker-entrypoint-initdb.d/raw_data/supermarket_1/sample_superstore.csv',
                                   'table_name_raw_layer': 'raw_layer',
                                   'sql_ddl_path': './sql_scripts/ddl/ddl.sql',
                                   'sql_dml_path': './sql_scripts/dml/dml.sql',
                                   'connection_name': 'my_db_conn'},
                                   serialize_json=True
                                   )

dag_variables = Variable.get('sales_variable', deserialize_json=True)



def get_conn_credentials(conn_id) -> BaseHook.get_connection:
    """
    Function returns dictionary with connection credentials

    :param conn_id: str with airflow connection id
    :return: Connection
    """
    conn = BaseHook.get_connection(conn_id)
    return conn

pg_conn = get_conn_credentials(dag_variables.get('connection_name'))
pg_hostname, pg_port, pg_username, pg_pass, pg_db = pg_conn.host, pg_conn.port, pg_conn.login, pg_conn.password, pg_conn.schema
conn = psycopg2.connect(host=pg_hostname, port=pg_port, user=pg_username, password=pg_pass, database=pg_db, options=dag_variables.get('options'))



def get_conn_credentials(conn_id) -> BaseHook.get_connection:
    """
    Function returns dictionary with connection credentials

    :param conn_id: str with airflow connection id
    :return: Connection
    """
    conn = BaseHook.get_connection(conn_id)
    return conn

pg_conn = get_conn_credentials(dag_variables.get('connection_name'))
pg_hostname, pg_port, pg_username, pg_pass, pg_db = pg_conn.host, pg_conn.port, pg_conn.login, pg_conn.password, pg_conn.schema
conn = psycopg2.connect(host=pg_hostname, port=pg_port, user=pg_username, password=pg_pass, database=pg_db)


folder_path = dag_variables.get('path')
csv_file_path = dag_variables.get('csv_file_path')

def download_csv():
    base_url = dag_variables.get('base_url')
    public_key = dag_variables.get('public_key')
    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']

    # Загружаем файл и сохраняем его
    download_response = requests.get(download_url)
    with open(csv_file_path, 'wb') as f:
        f.write(download_response.content)

def load_table_from_csv():
    cur = conn.cursor()
    table_name = dag_variables.get('table_name_raw_layer')
    psql_raw_path = dag_variables.get('psql_raw_path')
    with open(csv_file_path, encoding='ISO-8859-1') as f:
        reader = csv.reader(f)
        header_list = next(reader)
        header_list = [header.replace(' ', '_').replace('-', '_').lower() for header in header_list]

    columns = []
    for i, col_name in enumerate(header_list):
        columns.append(f"{col_name} VARCHAR")

    sql_query = f"""
        DROP TABLE IF EXISTS {table_name};
        CREATE TABLE {table_name}
        (
            {", ".join(columns)}
        )
    """
    try:
        cur.execute(sql_query)
        conn.commit()
        print("Таблица создана!")

    except Exception as e:
        print("Ошибка создания таблицы:", str(e))
        conn.rollback()

    copy_query = f"""
                    COPY {table_name}
                    FROM '{psql_raw_path}'
                    WITH (FORMAT CSV,
                          DELIMITER ',',
                          HEADER,
                          ENCODING 'ISO-8859-1');
                """
    try:
        cur.execute(copy_query)
        conn.commit()
        print(f"Данные в таблицу загружены из csv: '{psql_raw_path}'!")
    except Exception as e:
        print("Ошибка заполнения таблицы:", str(e))
        conn.rollback()


def update_date_column():
    cur = conn.cursor()
    sql_query = """
        UPDATE raw_layer 
        SET order_date = TO_DATE(order_date, 'MM/DD/YYYY'), 
            ship_date = TO_DATE(ship_date, 'MM/DD/YYYY')
    """
    cur.execute(sql_query)
    conn.commit()

def execute_ddl():
    cur = conn.cursor()
    with open('./sql_scripts/ddl/ddl.sql', 'r') as f:
        script = f.read()
    cur.execute(script)
    conn.commit()

def execute_dml():
    cur = conn.cursor()
    with open('./sql_scripts/dml/dml.sql', 'r') as f:
        script = f.read()
    cur.execute(script)
    conn.commit()


def create_mart_1():
    cur = conn.cursor()
    sql_query = """
        DROP TABLE IF EXISTS mart_1 CASCADE;
        CREATE TABLE mart_1 AS
            SELECT EXTRACT(YEAR FROM order_date) AS year_sale,
                   category_name,
                   SUM(sales * quantity) total_order_amount
            FROM orders o
            JOIN products p ON p.product_id = o.product_id 
            JOIN categories c ON p.category_id = c.category_id 
            WHERE segment = 'Corporate'
            GROUP BY year_sale, category_name
            ORDER BY year_sale, category_name;
    """
    cur.execute(sql_query)
    conn.commit()


def get_random_category(**kwargs):
    cur = conn.cursor()
    cur.execute("""SELECT category_name FROM categories ORDER BY RANDOM() LIMIT 1;""")
    random_category_id = cur.fetchone()[0]
    print(f'Случайная выбранная категория: {random_category_id}')
    kwargs['ti'].xcom_push(key='random_category_id', value=random_category_id)


def create_mart_2(**kwargs):
    cur = conn.cursor()
    random_category_id = kwargs['ti'].xcom_pull(key='random_category_id')
    sql_query = """
            DROP TABLE IF EXISTS mart_2 CASCADE;
            CREATE TABLE mart_2 AS
                SELECT EXTRACT(YEAR FROM order_date) year_sale, category_name, sub_category_name, SUM(sales * quantity) total_order_amount 
                FROM orders o 
                JOIN products p ON o.product_id = p.product_id 
                JOIN sub_categories sc ON sc.sub_category_id = p.sub_category_id 
                JOIN categories c ON c.category_id = p.category_id 
                WHERE EXTRACT(YEAR FROM order_date)=2015 AND c.category_name = '{}'
                GROUP BY EXTRACT(YEAR FROM order_date), category_name, sub_category_name;
     """.format(random_category_id)
    cur.execute(sql_query)
    conn.commit()
    cur.close()
    conn.close()


start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

create_folder_task = BashOperator(
    task_id='create_folder',
    bash_command=f'mkdir {folder_path}/supermarket_1/',
    dag=dag,
)

yandex_task = PythonOperator(
    task_id='yandex_task',
    python_callable=download_csv,
    dag=dag
)

wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath=csv_file_path,
    poke_interval=10,
    timeout=60,
    mode="poke",
    trigger_rule='none_failed',
    fs_conn_id = 'fs_default',
    dag=dag
)

load_raw_task = PythonOperator(
    task_id='load_raw_task',
    python_callable=load_table_from_csv,
    dag=dag
)

update_date_column = PythonOperator(
   task_id='update_date_column',
   python_callable=update_date_column,
   dag=dag,
)

execute_ddl = PythonOperator(
	task_id='execute_ddl',
	python_callable=execute_ddl,
	dag=dag
)

execute_dml = PythonOperator(
	task_id='execute_dml',
	python_callable=execute_dml,
	dag=dag
)

create_mart_1 = PythonOperator(
     task_id='create_mart_1',
     python_callable=create_mart_1,
     dag=dag,
)

get_random_category = PythonOperator(
     task_id='get_random_category',
     python_callable=get_random_category,
     provide_context=True,
     dag=dag
)

create_mart_2 = BranchPythonOperator(
    task_id='create_mart_2',
    python_callable=create_mart_2,
    provide_context=True,
    retries=3,
    retry_delay=timedelta(seconds=10),
    dag=dag
)

end_task = DummyOperator(
    task_id='end',
    dag=dag
)

start_task >> create_folder_task >> yandex_task >> wait_for_file >> load_raw_task >> update_date_column >> \
execute_ddl >> execute_dml >> create_mart_1 >> get_random_category >> create_mart_2 >> end_task