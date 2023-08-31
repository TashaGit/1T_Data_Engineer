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


one_time_start_dag = DAG(dag_id='one_time_start_dag',
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
                                   'column_names': 'open_val, close_val, high, low, value, volume, start_time, end_time, ticker, company',
                                   'connection_name': 'my_db_conn',
                                   'GAZP': 'Газпром',
                                   'SBER': 'Сбербанк России',
                                   'GMKN': 'Норильский никель',
                                   'LKOH': 'ЛУКОЙЛ',
                                   'ROSN': 'Роснефть'
                                   },
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
column_names = dag_variables.get('column_names')

securities = ['GAZP', 'SBER', 'GMKN', 'LKOH', 'ROSN']
def create_csv_files():
    for security in securities:
        interval = 60
        start_date = "2000-01-01"
        end_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?interval={interval}&from={start_date}&till={end_date}"
        response = requests.get(url)
        result = json.loads(response.text)
        resp_date = result["candles"]["data"]
        columns = result["candles"]["columns"]
        data_shares = pd.DataFrame(resp_date, columns=columns)
        data_shares = data_shares.assign(ticker=security, company=dag_variables.get(security))
        len_df = len(resp_date)
        last_received_date = data_shares.iloc[-1]["begin"]

        while len_df != 0:
            start_date = (pd.to_datetime(last_received_date) + pd.Timedelta(minutes=interval)).strftime("%Y-%m-%d %H:%M:%S")
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?interval={interval}&from={start_date}&till={end_date}"
            response = requests.get(url)
            result = json.loads(response.text)
            resp_date = result["candles"]["data"]
            len_df = len(resp_date)
            if len_df == 0:
                break
            data_next_page = pd.DataFrame(resp_date, columns=columns)
            data_next_page = data_next_page.assign(ticker=security, company=dag_variables.get(security))
            data_shares = pd.concat([data_shares, data_next_page], ignore_index=True) # Объединяем данные
            last_received_date = data_shares.iloc[-1]["begin"] # записываем последнее значение даты

        data_shares.to_csv(f'./raw_data/raw_{security}.csv', index=False)
        print(f'Файл raw_{security}.csv сохранен.')

def load_table_from_csv():
    for security in securities:
        cur = conn.cursor()
        table_name = f'raw_{security}'
        psql_raw_path = f'{dag_variables.get("psql_raw_path")}raw_{security}.csv'
        with open(f'{csv_file_path}raw_{security}.csv', encoding='UTF-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            print(f'Файл raw_{security}.csv прочитан')

        # Заранее определенные столбцы с типами данных
        columns = """
            id INTEGER PRIMARY KEY NOT NULL GENERATED BY DEFAULT AS IDENTITY ( INCREMENT 1 ),
            open_val DECIMAL,
            close_val DECIMAL,
            high DECIMAL,
            low DECIMAL,
            value DECIMAL,
            volume INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            ticker VARCHAR, 
            company VARCHAR
        """

        sql_query = f"""
            DROP TABLE IF EXISTS {table_name};
            CREATE TABLE {table_name}
            (
                {columns}
            )
        """
        try:
            cur.execute(sql_query)
            conn.commit()
            print("Таблица создана!")

        except Exception as e:
            print(f"Ошибка создания таблицы {table_name}:", str(e))
            conn.rollback()

        copy_query = f"""
                        COPY {table_name} ({column_names})
                        FROM '{psql_raw_path}'
                        WITH (FORMAT CSV,
                              DELIMITER ',',
                              HEADER,
                              ENCODING 'UTF-8');
                    """
        try:
            cur.execute(copy_query)
            conn.commit()
            print(f"Данные в таблицу загружены из csv: '{psql_raw_path}'!")
        except Exception as e:
            print(f"Ошибка заполнения таблицы {table_name}:", str(e))
            conn.rollback()


create_csv_task = PythonOperator(
    task_id='create_csv_files',
    python_callable=create_csv_files,
    dag=one_time_start_dag
)

load_table_from_csv_task = PythonOperator(
    task_id='load_table_from_csv',
    python_callable=load_table_from_csv,
    dag=one_time_start_dag
)


create_csv_task >> load_table_from_csv_task


daily_update_dag = DAG(dag_id='daily_update_dag',
                       tags=['daily_update'],
                       start_date=datetime(2023, 8, 30),
                       schedule_interval='30 10 * * *',
                       default_args=default_args)


def update_table_from_csv(security):
    table_name = f'raw_{security}'
    psql_raw_path = f'{dag_variables.get("psql_raw_path")}last_day_{security}.csv'
    cur = conn.cursor()

    # Получить список столбцов без колонки id
    copy_query = f"""
                    COPY {table_name} ({column_names})
                    FROM '{psql_raw_path}'
                    WITH (FORMAT CSV,
                          DELIMITER ',',
                          HEADER,
                          ENCODING 'UTF-8');
                """

    try:
        cur.execute(copy_query)
        conn.commit()
        print(f"Дополнительные данные загружены из csv: '{psql_raw_path}' в таблицу {table_name}!")
    except Exception as e:
        print(f"Ошибка дополнения таблицы {table_name}:", str(e))
        conn.rollback()


def downl_raw_last_day():
    for security in securities:
        interval = 60
        end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        with conn.cursor() as cur:
            # Запрос на получение максимального времени начала
            cur.execute(f"SELECT MAX(start_time) FROM raw_{security};")
            last_begin = cur.fetchone()[0]

        start_date = (last_begin.date() + timedelta(days=1)).strftime("%Y-%m-%d")
        if last_begin.date() < datetime.strptime(end_date, "%Y-%m-%d").date():
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security}/candles.json?interval={interval}&from={start_date}&till={end_date}"
            response = requests.get(url)
            result = json.loads(response.text)
            resp_date = result["candles"]["data"]
            columns = result["candles"]["columns"]
            data_shares = pd.DataFrame(resp_date, columns=columns)
            data_shares = data_shares.assign(ticker=security, company=dag_variables.get(security))
            if data_shares.shape[0] >= 2:
                data_shares.to_csv(f'./raw_data/last_day_{security}.csv', index=False)
                print(f'Файл last_day_{security}.csv сохранен')
                update_table_from_csv(security) # Обновление таблицы после сохранения файла
            else:
                print('Данных для записи нет.')


def create_core_tables():
    for security in securities:
        table_name = f'core_{security}'
        raw_table_name = f'raw_{security}'
        cur = conn.cursor()

        # Заранее определенные столбцы с типами данных
        columns = """
            id INTEGER PRIMARY KEY,
            open_val DECIMAL,
            close_val DECIMAL,
            high DECIMAL,
            low DECIMAL,
            value DECIMAL,
            volume INTEGER,
            date_stock DATE,
            start_time TIME,
            end_time TIME,
            year INTEGER,
            month INTEGER,
            day_of_week INTEGER,
            ticker VARCHAR,
            company VARCHAR
        """

        sql_query = f"""
        DROP TABLE IF EXISTS {table_name};
        CREATE TABLE {table_name}
        (
           {columns}
        );
        """

        try:
            cur.execute(sql_query)
            conn.commit()
            print(f"Таблица {table_name} создана!")

        except Exception as e:
            print(f"Ошибка создания таблицы {table_name}:", str(e))
            conn.rollback()

        transform_query = f"""
        INSERT INTO {table_name}
        SELECT id, 
               open_val, 
               close_val, 
               high, 
               low, 
               value, 
               volume, 
               start_time::date AS date_stock, 
               start_time::time AS start_time, 
               end_time::time AS end_time,
               EXTRACT(YEAR FROM start_time) AS year, 
               EXTRACT(MONTH FROM start_time) AS month,
               EXTRACT(DOW FROM start_time) AS day_of_week,
               ticker, 
               company
        FROM {raw_table_name};
        """

        try:
            cur.execute(transform_query)
            conn.commit()
            print(f"Данные из таблицы {raw_table_name} в {table_name} трансформированы!")

        except Exception as e:
            print(f"Ошибка трансформации данных таблицы {raw_table_name}:", str(e))
            conn.rollback()

def create_data_mart():
    data_mart_table = "data_mart"
    cur = conn.cursor()

    sql_query = f"""
        DROP TABLE IF EXISTS {data_mart_table};
        CREATE TABLE {data_mart_table}
        (
            surrogate_key VARCHAR,
            company VARCHAR,
            date_stock DATE,
            total_share DECIMAL,
            open_val DECIMAL,
            close_val DECIMAL,
            percentage_difference DECIMAL,
            max_volume_interval VARCHAR,
            max_price_interval VARCHAR,
            min_price_interval VARCHAR
        );
    """
    try:
        cur.execute(sql_query)
        conn.commit()
        print(f"Таблица {data_mart_table} создана!")

    except Exception as e:
        print(f"Ошибка создания таблицы {data_mart_table}:", str(e))
        conn.rollback()

    for security in securities:
        core_table_name = f'core_{security}'
        cur.execute(f"""
        INSERT INTO {data_mart_table} (surrogate_key, company, date_stock, total_share, 
                               open_val, close_val, percentage_difference, 
                               max_volume_interval, max_price_interval, min_price_interval)
        SELECT MAX(ticker), company, date_stock,
               ROUND(SUM(value), 2) AS total_share, 
       (SELECT open_val 
            FROM {core_table_name} 
            WHERE date_stock = (SELECT MAX(date_stock) FROM {core_table_name}) 
            AND start_time = (SELECT MIN(start_time) FROM {core_table_name} WHERE date_stock =
                (SELECT MAX(date_stock) FROM {core_table_name}))),
       (SELECT close_val 
            FROM {core_table_name} 
            WHERE date_stock = (SELECT MAX(date_stock) FROM {core_table_name}) 
            AND end_time = (SELECT MAX(end_time) FROM {core_table_name} WHERE date_stock =
                (SELECT MAX(date_stock) FROM {core_table_name}))),
       ROUND((((SELECT open_val 
                FROM {core_table_name} 
                WHERE date_stock = (SELECT MAX(date_stock) FROM {core_table_name}) 
                AND start_time = (SELECT MIN(start_time) FROM {core_table_name} WHERE date_stock =
                    (SELECT MAX(date_stock) FROM {core_table_name}))) / 
       (SELECT close_val 
            FROM {core_table_name} 
            WHERE date_stock = (SELECT MAX(date_stock) FROM {core_table_name}) 
            AND end_time = (SELECT MAX(end_time) FROM {core_table_name} WHERE date_stock =
                (SELECT MAX(date_stock) FROM {core_table_name}))) * 100 - 100)), 4) AS percentage_difference,
       (SELECT (start_time, end_time)::VARCHAR
            FROM {core_table_name}
            WHERE volume = (SELECT MAX(volume) FROM {core_table_name} WHERE date_stock =
                (SELECT MAX(date_stock) FROM {core_table_name}))LIMIT 1) AS max_volume_interval,
       (SELECT (start_time, end_time)::VARCHAR
            FROM {core_table_name}
            WHERE high = (SELECT MAX(high) FROM {core_table_name} WHERE date_stock =
                (SELECT MAX(date_stock) FROM {core_table_name})) LIMIT 1) AS max_price_interval,
       (SELECT (start_time, end_time)::VARCHAR
            FROM {core_table_name}
            WHERE low = (SELECT MIN(low) FROM {core_table_name} WHERE date_stock =
                (SELECT MAX(date_stock) FROM {core_table_name})) LIMIT 1) AS min_price_interval
        FROM {core_table_name}
        WHERE date_stock = (SELECT MAX(date_stock) FROM {core_table_name}) 
        GROUP BY company, date_stock;
        """)
        conn.commit()
        print(f"Данные по акции {security} добавлены в таблицу {data_mart_table}.")


downl_raw_last_day_task = PythonOperator(
    task_id='downl_raw_last_day',
    python_callable=downl_raw_last_day,
    dag=daily_update_dag
)

create_core_tables_task = PythonOperator(
    task_id='create_core_tables',
    python_callable=create_core_tables,
    dag=daily_update_dag
)

create_data_mart_task = PythonOperator(
    task_id='create_data_mart',
    python_callable=create_data_mart,
    dag=daily_update_dag
)


downl_raw_last_day_task >> create_core_tables_task >> create_data_mart_task