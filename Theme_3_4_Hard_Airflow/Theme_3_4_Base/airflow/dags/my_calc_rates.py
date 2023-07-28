from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
# from airflow.operators.python import BranchPythonOperator
# from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
# from airflow.models import Variable
# from airflow.hooks.base import BaseHook
from airflow.models.connection import Connection

import decimal
from time import localtime, strftime
from datetime import datetime, timedelta
import requests
import psycopg2
import pandas as pd


bases = ['BTC', 'EUR', 'GBR', 'JPY', 'CNY']


conn = psycopg2.connect(database='test',
                            user='postgres',
                            password='password',
                            host='host.docker.internal',
                            port='5430')


my_db_conn = Connection(
     conn_id="my_db_conn",
     conn_type="postgres",
     host="host.docker.internal",
     schema="test",
     port="5430",
     login="postgres",
     password="password"
)


default_args = {
    "owner": "marina_z",
    'start_date': days_ago(1)
}


dag = DAG(dag_id='fetch_exchange_rates_dag',
          tags=['marina_z'],
          start_date=datetime(2023, 7, 26),
          schedule_interval=timedelta(minutes=10),
          default_args=default_args
)


def fetch_exchange_rates():
    cur = conn.cursor()
    symbols = 'RUB'
    format = 'CSV'
    for base in bases:
        response = requests.get('https://api.exchangerate.host/latest',
                                params={'base': base,
                                        'symbols': symbols,
                                        'format': format
                                        })
        with open(f'./csv_files/exchange_latest_{base}.csv', 'wb') as f:
            f.write(response.content)

        df = pd.read_csv(f'./csv_files/exchange_latest_{base}.csv', decimal=',', index_col=False)
        df = pd.DataFrame(df)
        df['time_value'] = datetime.now().astimezone()
        # df['time_value'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df.to_csv(f'./csv_files/exchange_latest_{base}.csv', index=False)
        print(f'Save a new file exchange_latest_{base}.csv')

        table_name = f"exchange_rates_{base}"
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            exchange_id VARCHAR,
            exchange_rate DECIMAL,
            base_exchange VARCHAR,
            date DATE,
            time_value TIMESTAMP);
        """
        print(f'Create a new table exchange_latest_{base}')
        cur.execute(create_table_query)
        conn.commit()

        table_name = f"exchange_rates_{base}"
        copy_query = f"""
            COPY {table_name}
            FROM '/docker-entrypoint-initdb.d/csv_files/exchange_latest_{base}.csv'
            DELIMITER ','
            CSV HEADER;
        """
        print(f'Insert into table exchange_latest_{base}')
        cur.execute(copy_query)
        conn.commit()
    conn.commit()
    cur.close()
    conn.close()


def print_csv_all_rates():
    cur = conn.cursor()
    for base in bases:
        table_name = f"exchange_rates_{base}"
        save_csv = f"""COPY (SELECT * FROM {table_name} ORDER BY time_value DESC LIMIT 5)
        TO '/docker-entrypoint-initdb.d/csv_files/last_values_{base}.csv' 
        DELIMITER ',' 
        CSV HEADER;"""
        cur.execute(save_csv)
        conn.commit()
        print(f'last_values_{base}.csv saved')
        file_path = f"./csv_files/last_values_{base}.csv"
        df = pd.read_csv(file_path)
        pd.set_option('display.float_format', '{:.2f}'.format)
        with pd.option_context('display.expand_frame_repr', False):
            print(df)
    conn.commit()
    cur.close()
    conn.close()


hello_bash_task = BashOperator(task_id = 'bash_task',
                               bash_command = 'echo "Good morning my diggers!"')

fetch_exchange_rates_task = PythonOperator(task_id='fetch_exchange_rates_task',
                                           python_callable=fetch_exchange_rates,
                                           dag=dag)

print_csv_all_rates = PythonOperator(task_id='print_csv_all_rates',
                             python_callable=print_csv_all_rates,
                             dag=dag)

hello_bash_task >> fetch_exchange_rates_task >> print_csv_all_rates