### Импортируем библиотеки
import requests
import pandas as pd
import psycopg2


### Создадим подключение к базе Postgres, которую мы развернули в docker-compose:
conn = psycopg2.connect(database='exchange',
                        user='postgres',
                        password='password',
                        host='exchange',
                        port='5432')
cur = conn.cursor()


### C помощью цикла FOREACH и динамического SQL в PostgreSQL создадим сразу несколько таблиц:
    # - rate_june2023_btc;
    # - rate_june2023_eur;
    # - rate_june2023_gbr;
    # - rate_june2023_jpy;
    # - rate_june2023_cny.
cur.execute("""
DO $$
DECLARE
  value TEXT;
  values_arr TEXT[] := ARRAY['rate_june2023_btc', 'rate_june2023_eur', 'rate_june2023_gbr', 'rate_june2023_jpy', 'rate_june2023_cny'];
BEGIN
  FOREACH value IN ARRAY values_arr LOOP
    EXECUTE format('
        CREATE TABLE %I (
        date DATE PRIMARY KEY,
        exchange_id VARCHAR,
        exchange_rate DECIMAL,
        base_exchange VARCHAR,
        start_date DATE,
        end_date DATE)', value);
  END LOOP;
END $$;
""")
conn.commit();


### Создадим 2 списка - array_val и array_path, туда мы поместим названия таблиц и пути к файлам *.csv,
# чтобы заполнить наши таблицы данными из файлов. Далее пройдемся циклом и автоматически заполним наши
# таблицы значениями.
cur.execute("""DO $$
DECLARE
  value TEXT;
  path TEXT;
  array_val TEXT[] := ARRAY['rate_june2023_btc',
 							'rate_june2023_eur',
 							'rate_june2023_gbr',
 							'rate_june2023_jpy',
 							'rate_june2023_cny'];
  array_path TEXT[] := ARRAY['/docker-entrypoint-initdb.d/csv_files/exchange_june2023_BTC.csv',
 							 '/docker-entrypoint-initdb.d/csv_files/exchange_june2023_EUR.csv',
 							 '/docker-entrypoint-initdb.d/csv_files/exchange_june2023_GBR.csv',
 							 '/docker-entrypoint-initdb.d/csv_files/exchange_june2023_JPY.csv',
 							 '/docker-entrypoint-initdb.d/csv_files/exchange_june2023_CNY.csv'];
BEGIN
  FOR i IN 1..array_length(array_val, 1) LOOP
    value := array_val[i];
    path := array_path[i];
    EXECUTE format('COPY %I FROM %L DELIMITER %L CSV HEADER', value, path, ',');
  END LOOP;
END $$;
""")
conn.commit()


### Создадим временные таблицы для вычисления значений по каждому виду валюты.
cur.execute("""
DO $$
DECLARE
  table_name text;
  temp_table_name text;
  table_names TEXT[] := ARRAY['rate_june2023_btc',
 							  'rate_june2023_eur',
 							  'rate_june2023_gbr',
 							  'rate_june2023_jpy',
 							  'rate_june2023_cny'];
  temp_table_names TEXT[] := ARRAY['temp_rate_june2023_btc',
 							  	   'temp_rate_june2023_eur',
 							       'temp_rate_june2023_gbr',
 							       'temp_rate_june2023_jpy',
 							       'temp_rate_june2023_cny'];
BEGIN
  -- Цикл по списку table_names и temp_table_names
  FOR i IN 1..array_length(table_names, 1) LOOP
    table_name := table_names[i];
    temp_table_name := temp_table_names[i];
    -- Создание временной таблицы
    EXECUTE format('CREATE TEMPORARY TABLE %I AS
      SELECT * FROM (
        SELECT base_exchange, TO_CHAR("date", ''Month'') AS "Month", "date" date_max_rate, MAX(exchange_rate) AS max_val_rate
        FROM %I
        WHERE exchange_rate = (SELECT MAX(exchange_rate) FROM %I)
        GROUP BY "date"
      ) AS max_rate
      CROSS JOIN (
        SELECT "date" AS date_min_rate, MIN(exchange_rate) AS min_val_rate
        FROM %I
        WHERE exchange_rate = (SELECT MIN(exchange_rate) FROM %I)
        GROUP BY "date"
      ) AS min_rate
      CROSS JOIN (
        SELECT AVG(exchange_rate) AS avg_rate
        FROM %I
      ) AS avg_rate
      CROSS JOIN (
        SELECT exchange_rate AS last_date_rate
        FROM %I
        WHERE "date" = ''2023-06-30''
      ) AS last_date_rate;', temp_table_name, table_name, table_name, table_name, table_name, table_name, table_name);
  END LOOP;
END $$;
""")
conn.commit()


### Создадим итоговую таблицу total_exchange_rates, в которой выведены значения:
   # - валюта значений (base_exchange);
   # - месяц выводимых данных (Month);
   # - дата максимального значения валюты (date_max_rate);
   # - максимальное значение валюты (max_val_rate);
   # - дата минимального значения валюты (date_min_rate);
   # - минимальное значение валюты (min_val_rate);
   # - среднее значение за месяц (avg_rate);
   # - курс BTC на последний день месяца (last_date_rate).
cur.execute("""
CREATE TABLE total_exchange_rates AS
SELECT * FROM (
  SELECT * FROM temp_rate_june2023_btc
  UNION ALL
  SELECT * FROM temp_rate_june2023_eur
  UNION ALL
  SELECT * FROM temp_rate_june2023_gbr
  UNION ALL
  SELECT * FROM temp_rate_june2023_jpy
  UNION ALL
  SELECT * FROM temp_rate_june2023_cny
) AS union_result;
""")
conn.commit()


### Удалим временные таблицы.
cur.execute("""
DO $$
DECLARE
  temp_table_name text;
  temp_table_names TEXT[] := ARRAY['temp_rate_june2023_btc',
						  	   	   'temp_rate_june2023_eur',
						           'temp_rate_june2023_gbr',
						       	   'temp_rate_june2023_jpy',
						       	   'temp_rate_june2023_cny'];
BEGIN
  FOREACH temp_table_name IN ARRAY temp_table_names LOOP
    EXECUTE format('DROP TABLE IF EXISTS %I;', temp_table_name);
  END LOOP;
END $$;
""")
conn.commit()

cur.close()
conn.close()