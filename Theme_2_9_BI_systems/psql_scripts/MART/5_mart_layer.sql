WITH age_cat AS (SELECT personal_acc_id, 
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
 	  price_with_discount AS (SELECT order_id,
	   								 product_id, 
	   								 price,
	   								 (SELECT CASE 
	   								  WHEN order_time >= date_start_promo AND order_time <= date_end_promo THEN ROUND(price * (100 - discount) / 100, 0)
	   								  ELSE price
	   								  END) price_with_discount,
	   								 order_time,
	   								 date_start_promo, 
	   								 date_end_promo, 
	   								 discount,
	   								 amount,
	   								 (SELECT CASE 
	   								  WHEN order_time >= date_start_promo AND order_time <= date_end_promo THEN ROUND(price * (100 - discount) / 100, 0)
	   								  ELSE price
	   								  END) * amount total_check
							  FROM sales
							  LEFT JOIN promo_action using(product_id)
							  ORDER BY order_id, product_id),	
	 promo_check AS (SELECT order_id,
	   						product_id,
	   						total_check total_promo
	   				 FROM price_with_discount
	   				 WHERE price != price_with_discount
	   				 ORDER BY order_id)
SELECT age_category,
	   gender_value gender,
	   sum(total_check) sum_total_check,
	   sum(total_promo) sum_total_check_promo
FROM sales s
JOIN buyers b ON s.personal_acc_id = b.personal_acc_id
JOIN genders g ON b.gender_id = g.gender_id
JOIN age_cat ac ON ac.personal_acc_id = b.personal_acc_id
JOIN count_prod cp ON ac.personal_acc_id = cp.personal_acc_id
JOIN price_with_discount pws ON pws.order_id = s.order_id AND pws.product_id = s.product_id
LEFT JOIN promo_check pc ON pc.order_id = s.order_id AND pc.product_id = s.product_id
GROUP BY age_category, gender_value, count_buy
ORDER BY age_category, gender_value
