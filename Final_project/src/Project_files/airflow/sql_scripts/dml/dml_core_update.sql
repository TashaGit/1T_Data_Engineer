CREATE TEMPORARY TABLE temp_update AS
SELECT open_val, close_val, high,
	   low, value, volume,
	   start_time::date AS date_stock,
	   start_time::time AS start_time,
	   end_time::time AS end_time,
	   EXTRACT(YEAR FROM start_time) AS year_val,
	   EXTRACT(MONTH FROM start_time) AS month_val,
	   (EXTRACT(DOW FROM start_time) + 6) % 7 + 1 AS day_of_week,
	   ticker, company
FROM temp_delta
ORDER BY start_time, ticker;

INSERT INTO years (year_val)
SELECT date_part('year', date_stock) as year_val
FROM temp_update tu
WHERE NOT EXISTS (SELECT 1 FROM years WHERE year_val = date_part('year', date_stock))
GROUP BY date_part('year', date_stock)
ON CONFLICT DO NOTHING;

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
FROM temp_update tu
JOIN years y USING (year_val)
JOIN months m USING (month_val)
JOIN dows d USING (day_of_week)
JOIN tickers t USING (ticker)
WHERE NOT EXISTS (
SELECT 1
FROM core_layer_stock_prices cst
WHERE cst.date_stock = tu.date_stock
AND cst.start_time = tu.start_time
AND cst.end_time = tu.end_time
AND cst.ticker = tu.ticker
)
ORDER BY date_stock , start_time, ticker);