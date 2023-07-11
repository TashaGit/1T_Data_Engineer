CREATE TABLE IF NOT EXISTS products(
   product_id Int32,
   product_name String,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'products', 'postgres', 'password');


CREATE TABLE IF NOT EXISTS brands(
   brand_id Int32,
   brand_name String,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'brands', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS models(
   model_id Int32,
   model_name String,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'models', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS product_categories(
   prod_category_id Int32,
   category_name String,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'product_categories', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS genders(
   gender_id Int32,
   gender_value String,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'genders', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS platforms(
   platform_id Int32,
   platform_name String,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'platforms', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS types_actions(
   type_action_id Int32,
   action_name String,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'types_actions', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS promo_action(
   promo_id Int32,
   product_id Int32,
   date_start_promo Date,
   date_end_promo Date,
   discount Float32,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'promo_action', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS buyers(
   personal_acc_id Int32,
   buyers_cookies String,
   full_name String,
   gender_id Int32,
   birthdate Date,
   e_mail String,
   telephone String,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'buyers', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS banners(
   banner_id Int32,
   product_id Int32,
   platform_id Int32,
   personal_acc_id Int32,
   type_action_id Int32,
   date_action Date,
   time_interval String,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'banners', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS sales(
   order_id Int32,
   order_time Date,
   personal_acc_id Int32,
   product_id Int32,
   price Float64,
   brand_id Int32,
   model_id Int32,
   prod_category_id Int32,
   amount Int32,
) ENGINE = PostgreSQL('postgres:5432', 'sales', 'sales', 'postgres', 'password');

CREATE TABLE IF NOT EXISTS data_mart(
   age_category String, 
   gender String,
   sum_total_check Float64,
   sum_total_check_promo Float64,
) ENGINE = TinyLog AS (
WITH age_cat AS (SELECT personal_acc_id, 
						CASE 
 	   		  		WHEN age('year', birthdate, now())::integer <= 18 THEN '18 and younger'
 			  			WHEN age('year', birthdate, now())::integer BETWEEN 18 AND 25 THEN '19 - 24'
 			  			WHEN age('year', birthdate, now())::integer BETWEEN 24 AND 35 THEN '25 - 34'
 			  			WHEN age('year', birthdate, now())::integer BETWEEN 34 AND 45 THEN '35 - 44'
 			  			WHEN age('year', birthdate, now())::integer > 44 THEN '45 and older'
 			  			ELSE '0'
 			  			END age_category
 	    		     FROM buyers),
	  count_prod AS (SELECT personal_acc_id, sum(amount) count_buy
 					     FROM sales
 					     GROUP BY personal_acc_id
 					     ORDER BY personal_acc_id),
 	  new_price_with_discount AS (SELECT order_id, product_id,
 									      CASE 
	   								   WHEN order_time >= date_start_promo AND order_time <= date_end_promo THEN ROUND(price * (100 - discount) / 100, 0)
	   								   ELSE price
	   								   END total_check   
								         FROM sales 
								         LEFT JOIN promo_action using(product_id)
								         ORDER BY order_id, product_id),
	  promo_check AS (SELECT order_id,
	   					       product_id,
	   					       total_check * amount total_promo
	   				   FROM new_price_with_discount pwd
	   				   JOIN sales s ON s.order_id = pwd.order_id AND s.product_id = pwd.product_id
	   				   WHERE price != total_check
	   				   ORDER BY order_id)
SELECT age_category,
	    gender_value gender,
	    SUM(total_check) sum_total_check,
	    SUM(total_promo) sum_total_check_promo
FROM sales s
JOIN buyers b ON s.personal_acc_id = b.personal_acc_id
JOIN genders g ON b.gender_id = g.gender_id
JOIN age_cat ac ON ac.personal_acc_id = b.personal_acc_id
JOIN count_prod cp ON ac.personal_acc_id = cp.personal_acc_id
JOIN new_price_with_discount pws ON pws.order_id = s.order_id AND pws.product_id = s.product_id
LEFT JOIN promo_check pc ON pc.order_id = s.order_id AND pc.product_id = s.product_id
WHERE toMonth(s.order_time) = 6 
GROUP BY age_category, gender_value
ORDER BY age_category, gender_value);