CREATE TEMP TABLE readers_temp 
(
    full_name character varying(100),
    adress character varying(400),
    telephone character varying(20)
); 

COPY readers_temp 
FROM '/docker-entrypoint-initdb.d/readers.csv';
DELIMITER ','
ENCODING 'UTF8'
CSV HEADER;

UPDATE readers
SET    full_name = readers_temp.full_name
FROM   readers_temp

-- DROP TABLE readers_temp; 
