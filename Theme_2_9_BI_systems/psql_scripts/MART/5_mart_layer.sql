CREATE TABLE data_mart AS (WITH age_cat AS (SELECT personal_acc_id, 
						CASE 
 	   		  			WHEN date_part('year', age(current_date, birthdate))::integer <= 18 THEN '18 and younger'
 			  			WHEN date_part('year', age(current_date, birthdate))::integer BETWEEN 18 AND 25 THEN '19 - 24'
 			  			WHEN date_part('year', age(current_date, birthdate))::integer BETWEEN 24 AND 35 THEN '25 - 34'
 			  			WHEN date_part('year', age(current_date, birthdate))::integer BETWEEN 34 AND 45 THEN '35 - 44'
 			  			WHEN date_part('year', age(current_date, birthdate))::integer > 44 THEN '45 and older'
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
	 promo_check AS (SELECT pwd.order_id,
	   					   pwd.product_id,
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
WHERE date_part('MONTH', s.order_time) = 6 
GROUP BY age_category, gender_value
ORDER BY age_category, gender_value)