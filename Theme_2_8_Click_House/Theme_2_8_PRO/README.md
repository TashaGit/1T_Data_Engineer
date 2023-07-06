# Тема 2.8 "Введение в колоночные СУБД. Clickhouse".
# Задание PRO. 

```
Скрипт миграции витрины данных из СУБД Postgres в СУБД Clickhouse

Цель задания: Написать скрипт миграции, который позволит перенести уже собранную витрину данных из СУБД 
Postgres в СУБД Clickhouse, основываясь на задании 2.5.

Примечания:

Чтобы справиться с данным заданием:

   - Ознакомьтесь с разделами документации 

   - Предоставьте SQL-скрипт миграции в удобном формате (например, текстовый файл с расширением .sql).

Результат выполнения задания необходимо выложить в github/gitlab и указать ссылку на Ваш репозиторий (не 
забудьте — репозиторий должен быть публичным).

```
### База данных из PostgreSQL в ClickHouse загружается автоматически при исполнении файла [Docker-compose](docker-compose.yml).

### 1. SQL-скрипт переноса таблиц из PostgreSQL в ClickHouse:
Файл: [Create tables ClickHouse](clickhouse_scripts/click_create_table.sql)

### 2. Таблица data_mart в ClickHouse создается автоматически скриптом [Create tables ClickHouse](clickhouse_scripts/click_create_table.sql).
SQL-скрипт создания витрины данных в ClickHouse:
Файл: [Data Mart ClickHouse](clickhouse_scripts/click_data_mart.sql)

### 3. Файл Docker-compose:
Файл: [Docker-compose](docker-compose.yml)


### Для развертывания базы "Планирование продаж" необходимо:
1. Скачать архив из репозитория;
2. Распаковать в нужную папку;
3. В терминале перейти в папку с базой данных и выполнить команду ***docker-compose up -d***;
4. Запустить базу данных ClickHouse:
    - port: "8123",
    - логин: "default".
5. База данных автоматически загружена в ClickHouse.
   При необходимости работы с DB Postgres:
    - port: "5434", 
    - наименование базы данных: "sales_planning", 
    - логин: "postgres", 
    - пароль: "password";
6. Посмотреть автоматически сформированную витрину данных в терминале можно командой: ***docker logs clickhouse_server***.