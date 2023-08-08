|QUERY PLAN|
|----------|
|Gather Motion 4:1  (slice3; segments: 4)  (cost=0.00..437.00 rows=1 width=16)|
|  Merge Key: products.product_name|
|  ->  Sort  (cost=0.00..437.00 rows=1 width=16)|
|        Sort Key: products.product_name|
|        ->  GroupAggregate  (cost=0.00..437.00 rows=1 width=16)|
|              Group Key: products.product_name|
|              ->  Sort  (cost=0.00..437.00 rows=1 width=16)|
|                    Sort Key: products.product_name|
|                    ->  Redistribute Motion 4:4  (slice2; segments: 4)  (cost=0.00..437.00 rows=1 width=16)|
|                          Hash Key: products.product_name|
|                          ->  Result  (cost=0.00..437.00 rows=1 width=16)|
|                                ->  GroupAggregate  (cost=0.00..437.00 rows=1 width=16)|
|                                      Group Key: products.product_name|
|                                      ->  Sort  (cost=0.00..437.00 rows=1 width=73)|
|                                            Sort Key: products.product_name|
|                                            ->  Nested Loop  (cost=0.00..437.00 rows=1 width=73)|
|                                                  Join Filter: true|
|                                                  ->  Redistribute Motion 4:4  (slice1; segments: 4)  (cost=0.00..431.00 rows=1 width=8)|
|                                                        Hash Key: sales.product_id|
|                                                        ->  Result  (cost=0.00..431.00 rows=1 width=8)|
|                                                              ->  Sequence  (cost=0.00..431.00 rows=1 width=16)|
|                                                                    ->  Partition Selector for sales (dynamic scan id: 1)  (cost=10.00..100.00 rows=25 width=4)|
|                                                                          Partitions selected: 1 (out of 12)|
|                                                                    ->  Dynamic Seq Scan on sales (dynamic scan id: 1)  (cost=0.00..431.00 rows=1 width=16)|
|                                                                          Filter: ((product_id = 13) AND (order_time >= '2023-06-01 00:00:00'::timestamp without time zone) AND (order_time <= '2023-06-20 00:00:00'::timestamp without time zone))|
|                                                  ->  Index Scan using products_pkey on products  (cost=0.00..6.00 rows=1 width=69)|
|                                                        Index Cond: ((product_id = sales.product_id) AND (product_id = 13))|
|Optimizer: Pivotal Optimizer (GPORCA)|
