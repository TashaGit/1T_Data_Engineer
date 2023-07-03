-- 1. Определить, сколько книг прочитал каждый читатель в текущем году. 
-- Вывести рейтинг читателей по убыванию.
DO $$
BEGIN
  RAISE INFO '1. Определить, сколько книг прочитал каждый читатель в текущем году. Вывести рейтинг читателей по убыванию.';
END;
$$;
-- В текущем 2023 году:
DO $$
BEGIN
  RAISE INFO '- В текущем 2023 году:';
END;
$$;
SELECT full_name, count(DISTINCT book_id) total_books
FROM book_rentals
JOIN readers 
	USING (readers_ticket_id)
JOIN books
	USING (book_id)
WHERE date_part('year', start_rental) = 2023
	OR date_part('year', stop_rental) = 2023
	AND stop_rental IS NOT NULL 
GROUP BY full_name
ORDER BY total_books DESC;

-- Общий рейтинг (2022 - 2023):
DO $$
BEGIN
  RAISE INFO '- Общий рейтинг (2022 - 2023):';
END;
$$;
SELECT full_name, count(DISTINCT book_id) total_books
FROM book_rentals
JOIN readers 
    USING (readers_ticket_id)
JOIN books
    USING (book_id)
GROUP BY full_name
ORDER BY total_books DESC; 

-- 2. Определить, сколько книг у читателей на руках на текущую дату.
DO $$
BEGIN
  RAISE INFO '2. Определить, сколько книг у читателей на руках на текущую дату.';
END;
$$;
SELECT count(DISTINCT book_id) count_rent_books
FROM book_rentals
JOIN books 
	USING (book_id)
WHERE stop_rental IS NULL;

-- 3. Определить читателей, у которых на руках определенная книга.
DO $$
BEGIN
  RAISE INFO '3. Определить читателей, у которых на руках определенная книга.';
END;
$$;
SELECT title, author_name, full_name reader_name
FROM book_rentals
JOIN books 
	USING (book_id)
JOIN readers
	USING (readers_ticket_id)
JOIN authors
	USING (author_id)
WHERE title = 'Каштанка'
	AND stop_rental IS NULL 
ORDER BY full_name;

-- 4.  Определите, какие книги на руках читателей.
DO $$
BEGIN
  RAISE INFO '4.  Определите, какие книги на руках читателей.';
END;
$$;
SELECT full_name reader_name, title book_title, author_name
FROM book_rentals
JOIN books 
	USING (book_id)
JOIN authors
	USING (author_id)
JOIN readers
	USING (readers_ticket_id)
WHERE stop_rental IS NULL
ORDER BY full_name;

-- 5. Вывести количество должников на текущую дату. 
DO $$
BEGIN
  RAISE INFO '5. Вывести количество должников на текущую дату.';
END;
$$;
SELECT count(rent_id) total_debtors
FROM book_rentals
JOIN books 
	USING (book_id)
JOIN readers
	USING (readers_ticket_id)
WHERE stop_rental IS NULL 
	AND start_rental + 14 < current_date; 

-- 6. Книги какого издательства были самыми востребованными у читателей? 
-- Отсортируйте издательства по убыванию востребованности книг.
DO $$
BEGIN
  RAISE INFO '6. Книги какого издательства были самыми востребованными у читателей? Отсортируйте издательства по убыванию востребованности книг.';
END;
$$;
SELECT house_name popular_publish_house, count(book_id) total
FROM book_rentals
JOIN books 
    USING (book_id)
JOIN publish_houses
	using(publ_house_id)
GROUP BY popular_publish_house
ORDER BY total DESC; 

-- 7. Определить самого издаваемого автора.
DO $$
BEGIN
  RAISE INFO '7. Определить самого издаваемого автора.';
END;
$$;
SELECT author_name most_publish_author
FROM books
JOIN authors
	USING (author_id)
GROUP BY author_name
ORDER BY sum(amount) DESC 
LIMIT 1;

-- 8. Определить среднее количество прочитанных страниц читателем за день
DO $$
BEGIN
  RAISE INFO '8. Определить среднее количество прочитанных страниц читателем за день
';
END;
$$;

-- Среднее количество прочитанных страниц за день по всем читателям
DO $$
BEGIN
  RAISE INFO '- Среднее количество прочитанных страниц за день по всем читателям';
END;
$$;
SELECT DISTINCT round(avg(amount_pages / (stop_rental - start_rental)), 0) avg_count_pages
FROM book_rentals
JOIN books
	USING (book_id)
JOIN readers
	USING (readers_ticket_id)
WHERE stop_rental IS NOT NULL;

-- Среднее количество прочитанных страниц в разрезе каждого читателя 
DO $$
BEGIN
  RAISE INFO '- Среднее количество прочитанных страниц в разрезе каждого читателя';
END;
$$;
SELECT DISTINCT full_name, round(avg(amount_pages / (stop_rental - start_rental)), 0) avg_count_pages
FROM book_rentals
JOIN books
	USING (book_id)
JOIN readers
	USING (readers_ticket_id)
WHERE stop_rental IS NOT NULL
GROUP BY full_name
ORDER BY avg_count_pages DESC; 