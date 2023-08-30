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
import requests, csv, json
from urllib.parse import urlencode
import psycopg2
import pandas as pd


default_args = {
    "owner": "marina_z",
    'start_date': days_ago(1)
}


dag = DAG(dag_id='shares_company',
          tags=['marina_z'],
          start_date=datetime(2023, 8, 28),
          schedule_interval=None,
          default_args=default_args
)


variables = Variable.set(key='shares_variable',
                            value={'path': '/opt/airflow/raw_data',
                                   'base_url': 'http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities.json',
                                   'csv_file_path': './raw_data/',
                                   'psql_raw_path': '/docker-entrypoint-initdb.d/raw_data/',
                                   'sql_ddl_path': './sql_scripts/ddl/ddl.sql',
                                   'sql_dml_path': './sql_scripts/dml/dml.sql',
                                   'connection_name': 'my_db_conn'},
                                   serialize_json=True
                                   )

dag_variables = Variable.get('shares_variable', deserialize_json=True)

tickers = ['GAZP', 'SBER', 'GMKN', 'LKOH', 'ROSN']

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

securities = ['GAZP', 'SBER', 'GMKN', 'LKOH', 'ROSN']
def create_csv_files():
    for security in securities:
        interval = 10
        start_date = "2010-01-01"
        end_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?interval={interval}&from={start_date}&till={end_date}"
        response = requests.get(url)
        result = json.loads(response.text)
        resp_date = result["candles"]["data"]
        columns = result["candles"]["columns"]
        data_shares = pd.DataFrame(resp_date, columns=columns)
        len_df = len(resp_date)
        last_received_date = data_shares.iloc[-1]["begin"] # код для хранения значения последней даты и времени

        while len_df != 0:
            start_date = (pd.to_datetime(last_received_date) + pd.Timedelta(minutes=interval)).strftime("%Y-%m-%d %H:%M:%S")
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?interval={interval}&from={start_date}&till={end_date}"
            response = requests.get(url)
            result = json.loads(response.text)
            resp_date = result["candles"]["data"]
            len_df = len(resp_date)
            print(len_df)
            if len_df == 0:
                break
            data_next_page = pd.DataFrame(resp_date, columns=columns)
            data_shares = pd.concat([data_shares, data_next_page], ignore_index=True) # Объединяем данные
            last_received_date = data_shares.iloc[-1]["begin"] # записываем последнее значение даты

        data_shares.to_csv(f'./raw_data/raw_{security}.csv')


create_csv_task = PythonOperator(
    task_id='create_csv_files',
    python_callable=create_csv_files,
    dag=dag
)

create_csv_task