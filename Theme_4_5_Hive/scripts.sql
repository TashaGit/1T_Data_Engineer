-- Создание таблицы people

CREATE TEMPORARY TABLE IF NOT EXISTS people_temp (
  index INT,
  user_id STRING,
  first_name STRING,
  last_name STRING,
  sex STRING,
  email STRING,
  phone STRING,
  date_of_birth DATE,
  job_title STRING,
  group_col STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");


LOAD DATA INPATH '/user/marinaz/people.csv' OVERWRITE INTO TABLE people_temp;


CREATE TABLE people (
  index INT,
  user_id STRING,
  first_name STRING,
  last_name STRING,
  sex STRING,
  email STRING,
  phone STRING,
  date_of_birth DATE,
  job_title STRING,
  group_col INT,
  age_group STRING
)
CLUSTERED BY (first_name, last_name, email, age_group) INTO 10 BUCKETS
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS PARQUET;


INSERT INTO people 
SELECT index, user_id, first_name, last_name, sex, email, phone, date_of_birth, job_title, group_col,  
  CASE
    WHEN YEAR(CURRENT_DATE) - YEAR(date_of_birth) <= 18 THEN '0 - 18 лет'
    WHEN YEAR(CURRENT_DATE) - YEAR(date_of_birth) <= 25 THEN '19 - 25 лет'
    WHEN YEAR(CURRENT_DATE) - YEAR(date_of_birth) <= 35 THEN '26 - 35 лет'
    WHEN YEAR(CURRENT_DATE) - YEAR(date_of_birth) <= 45 THEN '36 - 45 лет'
    WHEN YEAR(CURRENT_DATE) - YEAR(date_of_birth) <= 55 THEN '46 - 55 лет'
    ELSE '56 и старше'
  END AS age_group
FROM people_temp;


DROP TABLE people_temp;


CREATE TEMPORARY TABLE customers_tmp (
  index INT,
  customer_id STRING,
  first_name STRING,
  last_name STRING,
  company STRING,
  city STRING,
  country STRING,
  phone_1 STRING,
  phone_2 STRING,
  email STRING,
  subscription_date DATE,
  website STRING,
  subscription_year INT,
  group_col STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");


LOAD DATA INPATH '/user/marinaz/customers.csv' OVERWRITE INTO TABLE customers_tmp;


CREATE TABLE customers (
  index INT,
  customer_id STRING,
  first_name STRING,
  last_name STRING,
  company STRING,
  city STRING,
  country STRING,
  phone_1 STRING,
  phone_2 STRING,
  email STRING,
  subscription_date DATE,
  website STRING,
  group_col STRING
)
PARTITIONED BY (subscription_year int)
CLUSTERED BY(first_name, last_name, email) INTO 10 BUCKETS
STORED AS PARQUET;


INSERT INTO TABLE customers PARTITION(subscription_year=2020)
SELECT index, customer_id, first_name, last_name,
       company, city, country, phone_1,
       phone_2, email, subscription_date, website,
       group_col
FROM customers_tmp WHERE subscription_year=2020;


INSERT INTO TABLE customers PARTITION(subscription_year=2021)
SELECT index, customer_id, first_name, last_name,
       company, city, country, phone_1,
       phone_2, email, subscription_date, website,
       group_col
FROM customers_tmp WHERE subscription_year=2021;


INSERT INTO TABLE customers PARTITION(subscription_year=2022)
SELECT index, customer_id, first_name, last_name,
       company, city, country, phone_1,
       phone_2, email, subscription_date, website,
       group_col
FROM customers_tmp WHERE subscription_year=2022;


DROP TABLE customers_tmp


-- Создание таблицы organizations

CREATE TEMPORARY TABLE organizations_tmp (
    index INT,
    organization_id STRING,
    name STRING,
    website STRING,
    country STRING,
    description STRING,
    founded INT,
    industry STRING,
    number_of_employees INT,
    group_col STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");


LOAD DATA INPATH '/user/marinaz/organizations.csv' OVERWRITE INTO TABLE organizations_tmp;


CREATE TABLE organizations (
    index INT,
    organization_id STRING,
    name STRING,
    website STRING,
    country STRING,
    description STRING,
    founded INT,
    industry STRING,
    number_of_employees INT,
    group_col STRING
)
CLUSTERED BY(name, website) INTO 10 BUCKETS
STORED AS PARQUET;


INSERT INTO TABLE organizations
SELECT * 
FROM organizations_tmp;


DROP TABLE organizations_tmp;


-- Создание витрины данных data_mart:

-- Запрос:

WITH customers_union AS (
					SELECT first_name, last_name, email, company, subscription_year
					FROM customers
					WHERE subscription_year = 2020
					UNION ALL
					SELECT first_name, last_name, email, company, subscription_year
					FROM customers
					WHERE subscription_year = 2021
					UNION ALL
					SELECT first_name, last_name, email, company, subscription_year
					FROM customers
					WHERE subscription_year = 2022
					),
	subscribers_count AS (
					SELECT company, subscription_year, age_group, COUNT(*) as count
					FROM customers_union c
					JOIN organizations o
						ON c.company = o.name
					JOIN people p
						ON p.first_name = c.first_name
						AND p.last_name = c.last_name
						AND p.email = c.email
					GROUP BY company, subscription_year, age_group),
	max_subscribers_count AS (
					SELECT company, subscription_year, MAX(count) as max_count
					FROM subscribers_count
					GROUP BY company, subscription_year)
SELECT s.company, s.subscription_year, s.age_group, s.count as subscribers_count
FROM subscribers_count s
JOIN max_subscribers_count m
ON s.company = m.company
AND s.subscription_year = m.subscription_year
AND s.count = m.max_count
ORDER BY s.company, s.subscription_year;


-- Формирование таблицы

CREATE TEMPORARY TABLE customers_union (
first_name STRING,
last_name STRING, 
email STRING, 
company STRING, 
subscription_year INT
);


INSERT INTO TABLE customers_union
(SELECT first_name, last_name, email, company, subscription_year
	FROM customers
	WHERE subscription_year = 2020
	UNION ALL
	SELECT first_name, last_name, email, company, subscription_year
	FROM customers
	WHERE subscription_year = 2021
	UNION ALL
	SELECT first_name, last_name, email, company, subscription_year
	FROM customers
	WHERE subscription_year = 2022
);
	
	
CREATE TEMPORARY TABLE subscribers_count (
company STRING,
subscription_year INT,
age_group STRING, 
count INT
);	


INSERT INTO TABLE subscribers_count (
SELECT company, subscription_year, age_group, COUNT(*) as count
FROM customers_union c
JOIN organizations o
	ON c.company = o.name
JOIN people p
	ON p.first_name = c.first_name
	AND p.last_name = c.last_name
	AND p.email = c.email
GROUP BY company, subscription_year, age_group
);


CREATE TEMPORARY TABLE max_subscribers_count (
company STRING, 
subscription_year INT, 
max_count INT
);

INSERT INTO TABLE max_subscribers_count (
SELECT company, subscription_year, MAX(count) as max_count
FROM subscribers_count
GROUP BY company, subscription_year
);


CREATE TABLE IF NOT EXISTS data_mart (
  company STRING,
  subscription_year INT,
  age_group STRING,
  subscribers_count INT
);

INSERT INTO data_mart (
SELECT s.company, s.subscription_year, s.age_group, s.count as subscribers_count
FROM subscribers_count s
JOIN max_subscribers_count m
	ON s.company = m.company
	AND s.subscription_year = m.subscription_year
	AND s.count = m.max_count
ORDER BY s.company, s.subscription_year
);


DROP TABLE IF EXISTS customers_union;
DROP TABLE IF EXISTS subscribers_count;
DROP TABLE IF EXISTS max_subscribers_count;