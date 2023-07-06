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

CREATE TABLE IF NOT EXISTS data_mart(
   sale_month UInt8, 
   shop_name String,
   product_name String,
   sales_fact Int32,
   sales_plan Int32,
   "sales_fact/sales_plan" Float64,
   income_fact Float64,
   income_plan Float64,
   "income_fact/income_plan" Float64,
) ENGINE = TinyLog AS (SELECT * FROM (WITH union_shops_tabl AS (SELECT * FROM shop_citilink
						                              UNION ALL SELECT * FROM shop_dns
						                              UNION ALL SELECT * FROM shop_mvideo
						                              ORDER BY sale_date, shop_id, product_id)	  
                      SELECT toMonth(sale_date) AS sale_month,
	   shop_name, 
	   product_name, 
	   SUM(sales_cnt) sales_fact,
	   SUM(plan_cnt) sales_plan,
	   ROUND(SUM(sales_cnt)::FLOAT / SUM(plan_cnt), 2) "sales_fact/sales_plan",
	   SUM(price * sales_cnt) income_fact,
	   SUM(price * plan_cnt) income_plan,
	   ROUND((SUM(price * sales_cnt)::FLOAT / SUM(price * plan_cnt)), 2) "income_fact/income_plan"
                      FROM union_shops_tabl us
                      JOIN shops sh ON us.shop_id = sh.shop_id
                      JOIN products pr ON us.product_id = pr.product_id 
                      JOIN plan p ON us.product_id = p.product_id AND us.shop_id = p.shop_id AND us.sale_date = p.plan_date 
                      WHERE toMonth(sale_date) = 5
                      GROUP BY sale_month, shop_name, product_name
                      ORDER BY shop_name, product_name))