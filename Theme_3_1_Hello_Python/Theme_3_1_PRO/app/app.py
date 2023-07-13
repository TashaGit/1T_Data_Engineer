# Импортируем необходимые библиотеки.
import random
import requests
from bs4 import BeautifulSoup
from faker import Faker
import pandas as pd
import csv

# Запишем ссылку на сайт в переменную lnk.
lnk = 'https://books.toscrape.com/'

# Формируем GET request.
r = requests.get(lnk)
r.text

# Упорядочим код.
soup = BeautifulSoup(r.text, 'lxml')

# Выведем теги, относящиеся к каждой книге.
books_full = soup.findAll("li" , class_= "col-xs-6 col-sm-4 col-md-3 col-lg-3")

# Напишем функцию для скрапинга названия книги и цены.
# Создадим пустой список.
data = []

# на сайте 50 страниц с перечнем книг.
for num in range(1, 51):
    url = f"https://books.toscrape.com/catalogue/page-{num}.html"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')   
    for book in books_full:
        book_title = book.h3.a["title"]
        book_price = book.findAll("p", class_= "price_color")
        price = book_price[0].text.strip()
        data.append([book_title, price[2:]])

books = pd.DataFrame(data)
books.columns = ['title', 'price']

# С помощью random.randint создадим случайные значения autor_id
from random import randint
autor_id = [randint(1, 10) for i in range(1000)]
autor_id = pd.Series(autor_id)

# Создадим случайные значения public_year
public_year = [randint(1950, 2023) for i in range(1000)]
public_year = pd.Series(public_year)

# Создадим случайные значения amount_pages
amount_pages = [randint(96, 460) for i in range(1000)]
amount_pages = pd.Series(amount_pages)

# Создадим случайные значения amount
amount = [randint(1, 5) for i in range(1000)]
amount = pd.Series(amount)

# Создадим случайные значения publ_house_id
publ_house_id = [randint(1, 3) for i in range(1000)]
publ_house_id = pd.Series(publ_house_id)

# Объединим полученные значения в общую таблицу
autor_id = pd.Series(autor_id, name='autor_id')
public_year = pd.Series(public_year, name='public_year')
amount_pages = pd.Series(amount_pages, name='amount_pages')
amount = pd.Series(amount, name='amount')
publ_house_id = pd.Series(publ_house_id, name='publ_house_id')
books = pd.concat([books, autor_id, public_year, amount_pages, amount, publ_house_id], axis=1)

# Поменяем столбцы местами, чтобы столбцы были как в базе данных library, отношение books
books = books[['title', 'autor_id', 'public_year', 'amount_pages', 'price', 'amount',
       'publ_house_id']]
# Индексацию строк начнем с 1
books.index += 1

# Сохраним в файл *.csv
books.to_csv('books.csv', encoding="utf-8")

# Обновим таблицу readers (читатели)
# Импортируем библиотеку Faker и установим локацию Россия.
from faker import Faker
fake = Faker(locale="ru_RU")

# Сгенерируем 20 случайных имен
full_name = []
for _ in range(20):
   full_name.append(fake.name())

# Сгенерируем 20 случайных адресов
adress = []
for _ in range(20):
   adress.append(fake.address())

# Сгенерируем 20 случайных номеров телефонов
telephone = []
for _ in range(20):
   telephone.append(fake.phone_number())

# Импортируем Pandas и объединим значения full_name, adress и telephone в одну таблицу
full_name = pd.Series(full_name, name='full_name')
adress = pd.Series(adress, name='adress')
telephone = pd.Series(telephone, name='telephone')
readers = pd.concat([full_name, adress, telephone], axis=1)
# Индексацию строк начнем с 1
readers.index += 1

# Сохраним фейковые данные в файл *.csv
readers.to_csv('readers.csv', encoding="utf-8")