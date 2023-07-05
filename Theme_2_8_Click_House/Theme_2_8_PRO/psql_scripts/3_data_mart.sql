DO $$
BEGIN
  RAISE INFO '
Задание 2. Аналитикам нужно оценить, насколько отдел планирования хорошо делает свою работу. Для этого необходимо разработать SQL-скрипт, который формирует таблицу со следующим набором атрибутов:
- shop_name — название магазина,
- product_name — название товара,
- sales_fact — количество фактических продаж на конец месяца,
- sales_plan — количество запланированных продаж на конец месяца,
- sales_fact/sales_plan — отношение количества фактических продаже к запланированному,
- income_fact — фактический доход,
- income_plan — планируемый доход,
- income_fact/income_plan — отношение фактического дохода к запланированному.';
END;
$$;
WITH union_shops_tabl AS (SELECT * FROM shop_citilink
						  UNION SELECT * FROM shop_dns
						  UNION SELECT * FROM shop_mvideo
						  ORDER BY sale_date, shop_id, product_id)	  
SELECT DATE_PART('MONTH',  sale_date) AS sale_month,
	   shop_name, 
	   product_name, 
	   SUM(sales_cnt) sales_fact,
	   SUM(plan_cnt) sales_plan,
	   ROUND(SUM(sales_cnt)::NUMERIC / SUM(plan_cnt), 2) "sales_fact/sales_plan",
	   SUM(price * sales_cnt) income_fact,
	   SUM(price * plan_cnt) income_plan,
	   ROUND((SUM(price * sales_cnt)::NUMERIC / SUM(price * plan_cnt)), 2) "income_fact/income_plan"
FROM union_shops_tabl us
JOIN shops sh ON us.shop_id = sh.shop_id
JOIN products pr ON us.product_id = pr.product_id 
JOIN plan p ON us.product_id = p.product_id AND us.shop_id = p.shop_id AND us.sale_date = p.plan_date 
WHERE DATE_PART('MONTH',  sale_date) = 5
GROUP BY sale_month, shop_name, product_name
ORDER BY shop_name, product_name