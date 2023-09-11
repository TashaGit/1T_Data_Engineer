DROP TABLE IF EXISTS core_temp;


CREATE TEMPORARY TABLE core_temp AS
SELECT open_val, close_val, high,
	   low, value, volume,
	   start_time::date AS date_stock,
	   start_time::time AS start_time,
	   end_time::time AS end_time,
	   EXTRACT(YEAR FROM start_time) AS year_val,
	   EXTRACT(MONTH FROM start_time) AS month_val,
	   (EXTRACT(DOW FROM start_time) + 6) % 7 + 1 AS day_of_week,
	   ticker, company
FROM raw_gazp
UNION ALL
SELECT open_val, close_val, high,
	   low, value, volume,
	   start_time::date AS date_stock,
	   start_time::time AS start_time,
	   end_time::time AS end_time,
	   EXTRACT(YEAR FROM start_time) AS year_val,
	   EXTRACT(MONTH FROM start_time) AS month_val,
	   (EXTRACT(DOW FROM start_time) + 6) % 7 + 1 AS day_of_week,
	   ticker, company
FROM raw_gmkn
UNION ALL
SELECT open_val, close_val, high,
	   low, value, volume,
	   start_time::date AS date_stock,
	   start_time::time AS start_time,
	   end_time::time AS end_time,
	   EXTRACT(YEAR FROM start_time) AS year_val,
	   EXTRACT(MONTH FROM start_time) AS month_val,
	   (EXTRACT(DOW FROM start_time) + 6) % 7 + 1 AS day_of_week,
	   ticker, company
FROM raw_sber
UNION ALL
SELECT open_val, close_val, high,
	   low, value, volume,
	   start_time::date AS date_stock,
	   start_time::time AS start_time,
	   end_time::time AS end_time,
	   EXTRACT(YEAR FROM start_time) AS year_val,
	   EXTRACT(MONTH FROM start_time) AS month_val,
	   (EXTRACT(DOW FROM start_time) + 6) % 7 + 1 AS day_of_week,
	   ticker, company
FROM raw_vtbr
UNION ALL
SELECT open_val, close_val, high,
	   low, value, volume,
	   start_time::date AS date_stock,
	   start_time::time AS start_time,
	   end_time::time AS end_time,
	   EXTRACT(YEAR FROM start_time) AS year_val,
	   EXTRACT(MONTH FROM start_time) AS month_val,
	   (EXTRACT(DOW FROM start_time) + 6) % 7 + 1 AS day_of_week,
	   ticker, company
FROM raw_yndx
ORDER BY start_time, ticker;


INSERT INTO tickers (ticker, company)
SELECT DISTINCT ticker, company FROM core_temp
ORDER BY ticker;


INSERT INTO years (year_val)
SELECT DISTINCT year_val FROM core_temp
ORDER BY year_val;


INSERT INTO months (month_val)
SELECT DISTINCT month_val FROM core_temp
ORDER BY month_val;


INSERT INTO dows (day_of_week)
SELECT DISTINCT day_of_week FROM core_temp
ORDER BY day_of_week;


INSERT INTO core_layer_stock_prices
	  (open_val, close_val, high,
	   low, value, volume,
	   date_stock, start_time, end_time,
	   year_id, month_id, dow_id,
	   ticker)
(SELECT open_val, close_val, high,
	   low, value, volume,
	   date_stock, start_time, end_time,
	   y.id, m.id, d.id,
	   t.ticker
FROM core_temp ct
JOIN years y USING (year_val)
JOIN months m USING (month_val)
JOIN dows d USING (day_of_week)
JOIN tickers t USING (ticker)
ORDER BY date_stock , start_time, ticker);


DROP TABLE IF EXISTS core_temp;