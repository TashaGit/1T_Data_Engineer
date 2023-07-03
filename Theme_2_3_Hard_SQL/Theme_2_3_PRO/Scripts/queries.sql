--    1. Доработать структуру БД «Библиотека» на предмет хранения дополнительной информации о книгах, которые были утеряны. Информация о потерянных книгах должна содержать:
--    книга, которая была утеряна
--    дата потери
--    читатель, который потерял книгу.
DO $$
BEGIN
  RAISE INFO '
1. Доработать структуру БД «Библиотека» на предмет хранения дополнительной информации о книгах, которые были утеряны. Информация о потерянных книгах должна содержать:
--    книга, которая была утеряна
--    дата потери
--    читатель, который потерял книгу.';
END;
$$;
CREATE TABLE loss_books as
(SELECT book_id, 
		title,
		rent_id, 
		start_rental + 14 date_loss, 
		readers_ticket_id
FROM book_rentals
JOIN books USING (book_id)
JOIN readers USING (readers_ticket_id)
WHERE stop_rental IS NULL 
	AND start_rental + 14 < current_date
ORDER BY date_loss);

-- 2. Напишите sql запрос, который определяет, терял ли определенный читатель книги.
DO $$
BEGIN
  RAISE INFO '
2. Напишите sql запрос, который определяет, терял ли определенный читатель книги.';
END;
$$;
SELECT book_id, title, readers_ticket_id, full_name
FROM loss_books
JOIN readers USING (readers_ticket_id)
WHERE readers_ticket_id = 4
OR full_name LIKE '%Кукушкин Семен Игнатьевич%';


-- 3. При потере книг количество доступных книг фонда меняется. 
-- Напишите sql запрос на обновление соответствующей информации.
DO $$
BEGIN
  RAISE INFO '
3. При потере книг количество доступных книг фонда меняется. 
Напишите sql запрос на обновление соответствующей информации.';
END;
$$;
UPDATE books
SET amount = amount - count_loss_books
FROM (SELECT book_id, count(book_id) count_loss_books 
      FROM loss_books 
      GROUP BY book_id) count_loss
WHERE books.book_id = count_loss.book_id;

-- 4. Определить сумму потерянных книг по каждому кварталу в течение года.
DO $$
BEGIN
  RAISE INFO '
4. Определить сумму потерянных книг по каждому кварталу в течение года.';
END;
$$;
SELECT sum(price) book_price, 
	   date_part('QUARTER', start_rental) quarter_creds, 
	   date_part('YEAR', start_rental) year_creds
FROM book_rentals
JOIN books
	USING (book_id)
WHERE stop_rental IS NULL 
	AND start_rental + 14 < current_date
GROUP BY quarter_creds, year_creds
ORDER BY year_creds, quarter_creds;