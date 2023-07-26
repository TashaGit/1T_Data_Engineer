"""
### DAG documntation
This is a simple ETL data pipeline example which extract rates data from API
 and load it into postgresql.
"""

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
          start_date=datetime(2023, 7, 25),
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
        df.to_csv(f'./csv_files/exchange_latest_{base}.csv', index=False)
        print(f'Save a new file exchange_latest_{base}.csv')

        table_name = f"exchange_rates_{base}"
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            exchange_id VARCHAR,
            exchange_rate DECIMAL,
            base_exchange VARCHAR,
            date DATE)
        """
        print(f'Create a new table exchange_latest_{base}')
        cur.execute(create_table_query)
        conn.commit()

        table_name = f"exchange_rates_{base}"
        copy_query = f"""
            TRUNCATE {table_name};
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


def create_total_exchange_rates_table():
    cur = conn.cursor()
    
    create_table_query = """DROP TABLE IF EXISTS total_exchange_rates;
        CREATE TABLE total_exchange_rates AS
        SELECT * FROM (
            SELECT * FROM exchange_rates_{}""".format(bases[0])
    
    for base in bases[1:]:
        create_table_query += """
            UNION ALL
            SELECT * FROM exchange_rates_{}""".format(base)
    
    create_table_query += """
        ) AS union_result;"""
    
    save_csv = """COPY total_exchange_rates 
                  TO '/docker-entrypoint-initdb.d/csv_files/total_exchange_rates.csv' 
                  DELIMITER ',' 
                  CSV HEADER;"""
    
    print('The table total_exchange_rates is created and saved')
    cur.execute(create_table_query)
    cur.execute(save_csv)
    cur.close()
    conn.commit()
    conn.close()


def print_csv_table():
    file_path = "./csv_files/total_exchange_rates.csv"
    df = pd.read_csv(file_path)
    pd.set_option('display.float_format', '{:.2f}'.format)
    print(df)


hello_bash_task = BashOperator(task_id = 'bash_task',
                               bash_command = 'echo "Good morning my diggers!"')

fetch_exchange_rates_task = PythonOperator(task_id='fetch_exchange_rates_task',
                                           python_callable=fetch_exchange_rates,
                                           dag=dag)

create_table_total = PythonOperator(task_id='create_total_exchange_rates_table',
                                    python_callable=create_total_exchange_rates_table,
                                    dag=dag)


print_table = PythonOperator(task_id='print_csv_table',
                             python_callable=print_csv_table,
                             dag=dag)

hello_bash_task >> fetch_exchange_rates_task >> create_table_total >> print_table