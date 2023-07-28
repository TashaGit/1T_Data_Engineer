from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.hooks.base import BaseHook
from airflow.sensors.python import PythonSensor

from datetime import datetime, timedelta
import requests, io
import psycopg2
import pandas as pd


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


# variables = Variable.set(key='currency_load_variables',
#                             value={'url': 'https://api.exchangerate.host/latest',
#                                 'connection_name': 'my_db_conn',
#                                 'base_BTC': 'BTC',
#                                 'base_EUR': 'EUR',
#                                 'base_GBR': 'GBR',
#                                 'base_JPY': 'JPY',
#                                 'base_CNY': 'CNY',
#                                 'bases': ['BTC', 'EUR', 'GBR', 'JPY', 'CNY'],
#                                 'symbols': 'RUB',
#                                 'format': 'CSV'},
#                                 serialize_json=True
#                                 )

dag_variables = Variable.get('currency_load_variables', deserialize_json=True)



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


bases = dag_variables.get('bases')


def count_rows(**kwargs):
    cur = conn.cursor()
    for base in bases:
        table_name = f'exchange_rates_{base}'
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

        sql_query = f"""SELECT COUNT(*) FROM {table_name}"""
        cur.execute(sql_query)      
        row_count = cur.fetchone()[0] 
        print(f'Количество строк в таблице {table_name} = {row_count}')
        task_instance = kwargs['ti']
        task_instance.xcom_push(key=f'count_row_{base}', value={'val':row_count})
        conn.commit()


def fetch_exchange_rates(**kwargs):
    for base in bases:
        response = requests.get(dag_variables.get('url'),
                                params={'base': dag_variables.get(f'base_{base}'),
                                        'symbols': dag_variables.get('symbols'),
                                        'format': dag_variables.get('format')
                                        })
        csv_data = io.StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_data, decimal=',', index_col=False)
        if len(df) >= 1:
            df['time_value'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ti = kwargs['ti']
            ti.xcom_push(key=f'results_{base}', value={'code':df['code'][0], 
                                                       'rate':df['rate'][0], 
                                                       'base':df['base'][0], 
                                                       'date':df['date'][0], 
                                                       'time_value':df['time_value'][0]})



def insert_values(**kwargs):
    cur = conn.cursor()
    for base in bases:
        task_instance = kwargs['ti']
        results = task_instance.xcom_pull(key=f'results_{base}')
        table_name = f'exchange_rates_{base}'

        insert_values = f""" 
        INSERT INTO {table_name} 
            (exchange_id, exchange_rate, base_exchange, date, time_value) 
            VALUES ('{results['code']}', 
                    '{results['rate']}',
                    '{results['base']}',
                    '{results['date']}',
                    '{results['time_value']}')
                    """
        cur.execute(insert_values)
        conn.commit()
        print(f'Insert values into table exchange_latest_{base}')
    conn.commit()
    cur.close()


def compliance_check(**kwargs):
    count = 0
    for base in bases:
        cur = conn.cursor()
        task_instance = kwargs['ti']
        results = task_instance.xcom_pull(key=f'count_row_{base}')
        result = results['val']
        table_name = f'exchange_rates_{base}'
        sql_query = f"""SELECT COUNT(*) FROM {table_name}"""
        cur.execute(sql_query)      
        new_count = cur.fetchone()[0]
        conn.commit()
        print(f'old_count = {result}, new_count={new_count}')
        if int(new_count) - int(result) > 0:
            count += 1
        else:
            count          
    conn.commit()
    cur.close()
    if count == len(bases):
        return True
    else:
        return False


def create_total_table():
    for base in bases:
        cur = conn.cursor()
        table_name = f'calc_agg_func_{base}'
        from_table = f'exchange_rates_{base}'
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            max_rate DECIMAL,
            min_rate DECIMAL,
            avg_rate DECIMAL,
            calc_time TIMESTAMP);
        """
        cur.execute(create_table_query)
        conn.commit()        

        insert_values = f""" 
        INSERT INTO {table_name}
        SELECT MAX(exchange_rate) max_rate, 
                MIN(exchange_rate) min_rate, 
                AVG(exchange_rate) avg_rate,
                now() AS calc_time
        FROM {from_table}
        """
        cur.execute(insert_values)
        conn.commit()
    conn.close()


hello_bash_task = BashOperator(task_id='bash_task',
                               bash_command='echo "Good morning my diggers!"')

count_rows_task = PythonOperator(task_id='count_rows',
                                 python_callable=count_rows,
                                 provide_context=True,
                                 dag=dag)

fetch_exchange_rates_task = PythonOperator(task_id='fetch_exchange_rates_task',
                                           python_callable=fetch_exchange_rates,
                                           provide_context=True,
                                           dag=dag)

insert_values = PythonOperator(task_id='insert_values',
                                python_callable=insert_values,
                                provide_context=True,
                                dag=dag)


chek_sensor = PythonSensor(task_id='chek_sensor',
                           python_callable=compliance_check,
                           op_kwargs={'key': 'value'},
                           soft_fail=True,
                           poke_interval=30,
                           mode="poke",
                           timeout=5,    
                            )


create_total_table = PythonOperator(task_id = 'create_total_table',
                                    python_callable=create_total_table,
                                    dag=dag)


hello_bash_task >> count_rows_task >> fetch_exchange_rates_task >> insert_values >> chek_sensor >> create_total_table