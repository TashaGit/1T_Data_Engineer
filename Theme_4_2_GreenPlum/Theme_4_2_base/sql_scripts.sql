CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    price NUMERIC(10, 2)
)
DISTRIBUTED BY (product_id);

INSERT INTO products (product_id, product_name, price)
VALUES (1, 'Ноутбук HONOR MagicBook X 15 i5 8+512GB Space Grey (BDR-WDH)', 51999),
       (2, 'Мышь Acer OMR031', 699),
       (3, 'Ноутбук ASUS M1502IA-BQ093', 46999),
       (4, 'Игровой ноутбук Thunderobot 911 Air Wave D (JT009CE09RU)', 64999),
       (5, 'Программное обеспечение Microsoft Office Для дома и учёбы 2021 & VPN на 1 месяц', 13999),
       (6, 'Ноутбук Haier i1510SD (JB0B1BE00RU)', 34999),
       (7, 'Игровой ноутбук ASUS TUF F15 FX506HCB-US51', 73999),
       (8, 'Игровая мышь Logitech G502 X Hero Lightspeed', 15290),
       (9, 'Антивирус Kaspersky Internet Security 1ПК/1Г + Think Free Office', 3999),
       (10, 'Операционная система Microsoft Windows 11 Home 32-bit/64-bit & VPN на 1 месяц', 13999),
       (11, 'Ноутбук ASUS Ноутбук 15 M1502I (90NB0Y52-M002R0)', 44999),
       (12, 'Ноутбук Xiaomi RedmiBook 15 JYU4525RU', 39999),
       (13, 'Ноутбук Apple MacBook Air 13 M1/8/256GB Space Gray (MGN63)', 91999);
      
CREATE TABLE sales (
    order_id INT NOT NULL,
    order_time TIMESTAMP NOT NULL,
	personal_acc_id INT NOT NULL, 
	product_id INT NOT NULL REFERENCES products(product_id),
	brand_id INT NOT NULL, 
	model_id INT NOT NULL, 
	prod_category_id INT NOT NULL, 
	amount INT NOT NULL
)
DISTRIBUTED BY (order_id)
PARTITION BY RANGE(order_time)
(
    START ('2023-01-01 00:00:00') INCLUSIVE
    END ('2024-01-01 00:00:00') EXCLUSIVE
    EVERY (INTERVAL '1 month')
);

INSERT INTO sales
(order_id, order_time, personal_acc_id, product_id, brand_id, model_id, prod_category_id, amount)
VALUES
(1, '2023-06-01', 1, 3, 3, 6, 3, 2),
(2, '2023-06-01', 1, 10, 8, 12, 4, 2),
(3, '2023-06-02', 2, 6, 4, 4, 3, 1),
(4, '2023-06-02', 2, 5, 8, 8, 2, 1),
(5, '2023-06-03', 3, 11, 3, 1, 3, 1),
(6, '2023-06-03', 3, 2, 2, 9, 1, 1),
(7, '2023-06-04', 4, 13, 1, 7, 3, 1),
(8, '2023-06-04', 4, 8, 7, 3, 1, 1),
(9, '2023-06-05', 5, 9, 6, 5, 2, 1),
(10, '2023-06-05', 6, 4, 9, 2, 3, 3),
(11, '2023-06-06', 7, 1, 5, 13, 3, 1),
(12, '2023-06-07', 8, 12, 10, 10, 3, 1),
(13, '2023-06-08', 10, 2, 2, 9, 1, 10),
(14, '2023-06-09', 9, 7, 3, 11, 3, 1),
(15, '2023-06-10', 4, 5, 8, 8, 2, 1),
(16, '2023-06-11', 6, 11, 3, 1, 3, 1),
(17, '2023-06-12', 3, 2, 2, 9, 1, 1),
(18, '2023-06-13', 6, 13, 1, 7, 3, 1),
(19, '2023-06-14', 8, 8, 7, 3, 1, 1),
(20, '2023-06-15', 3, 13, 1, 7, 3, 1),
(21, '2023-06-16', 2, 8, 7, 3, 1, 1),
(22, '2023-06-17', 4, 9, 6, 5, 2, 1),
(23, '2023-06-18', 7, 3, 3, 6, 3, 2),
(24, '2023-06-19', 1, 10, 8, 12, 4, 2),
(25, '2023-06-20', 10, 6, 4, 4, 3, 1),
(26, '2023-06-21', 6, 1, 5, 13, 3, 1),
(27, '2023-06-22', 6, 12, 10, 10, 3, 1),
(28, '2023-06-23', 5, 2, 2, 9, 1, 10),
(29, '2023-06-24', 6, 7, 3, 11, 3, 1),
(30, '2023-06-25', 8, 5, 8, 8, 2, 1),
(31, '2023-06-26', 2, 11, 3, 1, 3, 1),
(32, '2023-06-27', 7, 2, 2, 9, 1, 1),
(33, '2023-06-28', 5, 13, 1, 7, 3, 1),
(34, '2023-06-29', 1, 8, 7, 3, 1, 1),
(35, '2023-06-30', 10, 9, 6, 5, 2, 1);
      
SET optimizer = ON;

SELECT 
   product_name,
   sum(price * amount) AS total_sales
FROM 
   sales 
   JOIN products USING (product_id)
WHERE 
   product_id = 13 AND order_time BETWEEN '2023-06-01' AND '2023-06-20'
GROUP BY product_name;

EXPLAIN SELECT 
   product_name,
   sum(price * amount) AS total_sales
FROM 
   sales 
   JOIN products USING (product_id)
WHERE 
   product_id = 13 AND order_time BETWEEN '2023-06-01' AND '2023-06-20'
GROUP BY product_name
ORDER BY product_name;


