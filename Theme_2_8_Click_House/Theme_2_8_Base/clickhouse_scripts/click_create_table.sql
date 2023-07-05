CREATE TABLE IF NOT EXISTS products(
   product_id Int32,
   product_name String,
   price Float64,
) ENGINE = PostgreSQL('postgres:5432', 'sales_planning', 'products', 'postgres', 'password');


CREATE TABLE IF NOT EXISTS shops(
   shop_id Int32,
   shop_name String,
) ENGINE = PostgreSQL('postgres:5432', 'sales_planning', 'shops', 'postgres', 'password');


CREATE TABLE IF NOT EXISTS plan(
   product_id Int32,
   shop_id Int32,
   plan_cnt Int32,
   plan_date Date,
) ENGINE = PostgreSQL('postgres:5432', 'sales_planning', 'plan', 'postgres', 'password');


CREATE TABLE IF NOT EXISTS shop_citilink(
   shop_id Int32,
   product_id Int32,
   sale_date Date,
   sales_cnt Int32,
) ENGINE = PostgreSQL('postgres:5432', 'sales_planning', 'shop_citilink', 'postgres', 'password');


CREATE TABLE IF NOT EXISTS shop_dns(
   shop_id Int32,
   product_id Int32,
   sale_date Date,
   sales_cnt Int32,
) ENGINE = PostgreSQL('postgres:5432', 'sales_planning', 'shop_dns', 'postgres', 'password');


CREATE TABLE IF NOT EXISTS shop_mvideo(
   shop_id Int32,
   product_id Int32,
   sale_date Date,
   sales_cnt Int32,
) ENGINE = PostgreSQL('postgres:5432', 'sales_planning', 'shop_mvideo', 'postgres', 'password');