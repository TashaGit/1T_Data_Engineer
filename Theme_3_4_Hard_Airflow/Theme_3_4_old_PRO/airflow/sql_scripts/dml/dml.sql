INSERT INTO cities (city_name)
SELECT DISTINCT city FROM raw_layer;

INSERT INTO states (state_name)
SELECT DISTINCT state FROM raw_layer;

INSERT INTO countries (country_name)
SELECT DISTINCT country FROM raw_layer;

INSERT INTO regions (region_name)
SELECT DISTINCT region FROM raw_layer;

INSERT INTO categories (category_name)
SELECT DISTINCT category FROM raw_layer;

INSERT INTO sub_categories (sub_category_name)
SELECT DISTINCT sub_category FROM raw_layer;

INSERT INTO ship_modes (ship_mode_name)
SELECT DISTINCT ship_mode FROM raw_layer;

INSERT INTO postal_codes (postal_code_value)
SELECT DISTINCT postal_code FROM raw_layer;

INSERT INTO products (product_id_raw, product_name, category_id, sub_category_id)
        SELECT DISTINCT rl.product_id, rl.product_name, cat.category_id, sc.sub_category_id
        FROM raw_layer rl
        JOIN categories cat ON rl.category = cat.category_name
        JOIN sub_categories sc ON rl.sub_category = sc.sub_category_name
        ORDER BY product_id;

INSERT INTO customers (customer_id_raw, customer_name)
        SELECT DISTINCT customer_id, customer_name
		FROM raw_layer
        WHERE segment = 'Corporate'
		ORDER BY customer_id;

INSERT INTO orders
(row_id, order_id, order_date, ship_date, ship_mode_id, customer_id, segment, country_id, city_id, state_id, postal_code_id, region_id, product_id, sales, quantity, discount, profit)
        SELECT row_id::INT,
			   order_id,
			   order_date::DATE,
			   ship_date::DATE,
			   ship_mode_id,
			   c.customer_id,
			   segment,
			   country_id,
			   city_id,
			   state_id,
			   postal_code_id,
			   region_id,
			   p.product_id,
			   sales::NUMERIC,
			   quantity::INT,
			   discount::NUMERIC,
			   profit::NUMERIC
		FROM raw_layer rl
		JOIN ship_modes sm ON rl.ship_mode = sm.ship_mode_name
		JOIN customers c ON rl.customer_id = c.customer_id_raw AND rl.customer_name = c.customer_name
		JOIN countries c2 ON rl.country = c2.country_name
		JOIN cities c3 ON rl.city = c3.city_name
		JOIN states s ON rl.state = s.state_name
		JOIN postal_codes pc ON rl.postal_code = pc.postal_code_value
		JOIN regions r ON rl.region = r.region_name
		JOIN products p ON rl.product_id = p.product_id_raw AND rl.product_name = p.product_name
		WHERE segment = 'Corporate'
		ORDER BY row_id, order_id;