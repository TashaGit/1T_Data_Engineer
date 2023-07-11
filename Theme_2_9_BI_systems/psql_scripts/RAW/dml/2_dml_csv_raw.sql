COPY raw_sales
FROM '/docker-entrypoint-initdb.d/base_csv/raw_sales.csv'
DELIMITER ';'
ENCODING 'UTF8'
CSV HEADER;

COPY raw_personal_account
FROM '/docker-entrypoint-initdb.d/base_csv/raw_personal_account.csv'
DELIMITER ';'
ENCODING 'UTF8'
CSV HEADER;

COPY raw_promo_action
FROM '/docker-entrypoint-initdb.d/base_csv/raw_promo_action.csv'
DELIMITER ';'
ENCODING 'UTF8'
CSV HEADER;

COPY raw_banners
FROM '/docker-entrypoint-initdb.d/base_csv/raw_banners.csv'
DELIMITER ';'
ENCODING 'UTF8'
CSV HEADER;