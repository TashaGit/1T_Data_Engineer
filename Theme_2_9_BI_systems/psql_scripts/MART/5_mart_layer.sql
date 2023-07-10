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
 	  pop_product AS (SELECT product_id, sum(amount) count_buy
 						FROM sales
 						GROUP BY product_id)
SELECT personal_acc_id, 
	   gender_value gender,
	   age_category,
 	   e_mail,
 	   telephone
FROM buyers b
JOIN genders g ON b.gender_id = g.gender_id
JOIN age_cat USING(personal_acc_id)