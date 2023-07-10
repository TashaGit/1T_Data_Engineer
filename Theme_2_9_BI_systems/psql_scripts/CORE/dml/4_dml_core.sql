INSERT INTO products (product_name)
	(SELECT DISTINCT product_name FROM raw_sales);

INSERT INTO brands (brand_name)
	(SELECT DISTINCT brand FROM raw_sales ORDER BY brand);

INSERT INTO models (model_name)
	(SELECT DISTINCT product_model FROM raw_sales ORDER BY product_model);

INSERT INTO product_categories (category_name)
	(SELECT DISTINCT category FROM raw_sales);

INSERT INTO genders (gender_value)
	(SELECT DISTINCT gender FROM raw_personal_account);

INSERT INTO platforms (platform_name)
	(SELECT DISTINCT platform FROM raw_banners ORDER BY platform);

INSERT INTO types_actions (action_name)
	(SELECT DISTINCT type_action FROM raw_banners ORDER BY type_action);

INSERT INTO promo_action (product_id, date_start_promo, date_end_promo, discount)
	(SELECT product_id, date_start_promo, date_end_promo, discount FROM raw_promo_action 
	 JOIN products USING(product_name)
	 ORDER BY date_start_promo);

-- INSERT INTO age_categories (personal_acc_id, age_bracket)
-- 	(SELECT personal_acc_id,
-- 			CASE 
-- 			WHEN date_part('year', age(current_date, birthdate))::integer <= 18 THEN '18 and younger'
-- 			WHEN date_part('year', age(current_date, birthdate))::integer BETWEEN 18 AND 25 THEN '19 - 24'
-- 			WHEN date_part('year', age(current_date, birthdate))::integer BETWEEN 24 AND 35 THEN '25 - 34'
-- 			WHEN date_part('year', age(current_date, birthdate))::integer BETWEEN 34 AND 45 THEN '35 - 44'
-- 			WHEN date_part('year', age(current_date, birthdate))::integer > 44 THEN '45 and older'
-- 			ELSE '0'
-- 			END 
-- 	 FROM raw_personal_account);

INSERT INTO buyers (personal_acc_id, buyers_cookies, full_name, gender_id, birthdate, e_mail, telephone)
	(SELECT rp.personal_acc_id, 
			rp.buyers_cookies, 
			rp.full_name, 
			gender_id, 
			birthdate, 
	     	rp.e_mail, 
	     	rp.telephone 
	 FROM raw_personal_account rp
	 JOIN genders g ON rp.gender = g.gender_value
);

INSERT INTO banners (product_id, platform_id, personal_acc_id, type_action_id, date_action, time_interval)
	(SELECT product_id, 
			platform_id, 
			personal_acc_id, 
			type_action_id, 
			time_start_act::DATE date_action,
	     	(time_end_act - time_start_act)::TIME time_interval 
	 FROM raw_banners b
	 JOIN products USING (product_name)
	 JOIN platforms p ON p.platform_name = b.platform 
	 JOIN buyers USING (buyers_cookies)
	 JOIN types_actions t ON b.type_action = t.action_name
	 ORDER BY date_action
);

INSERT INTO sales (order_id, order_time, personal_acc_id, product_id, price, brand_id, model_id, prod_category_id, amount)
	(SELECT order_id, 
			order_time, 
			personal_acc_id, 
			product_id, 
			price, 
			brand_id, 
			model_id, 
			prod_category_id, 
			amount
	 FROM raw_sales s
	 JOIN buyers USING (buyers_cookies)
	 JOIN products USING (product_name)
	 JOIN brands b ON s.brand = b.brand_name 
	 JOIN models m ON m.model_name = s.product_model 
	 JOIN product_categories pc ON pc.category_name = s.category 
	 ORDER BY order_time, order_id, personal_acc_id
);