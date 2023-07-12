# Импортируем необходимые библиотеки.
import requests
from bs4 import BeautifulSoup
import csv

# Запишем ссылку на сайт в переменную lnk.
lnk = 'https://books.toscrape.com/'

# Формируем GET request.
r = requests.get(lnk)
r.text

# Упорядочим код.
soup = BeautifulSoup(r.text, 'lxml')
soup

# Выведем теги, относящиеся к каждой книге.
books_full = soup.findAll("li" , class_= "col-xs-6 col-sm-4 col-md-3 col-lg-3")
books_full

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
data

# Сохраним данные в формат *.csv для дальнейшего использования.
columns_name = ['title', 'price']
   
with open('books_scrap.csv', 'w') as f:
    write = csv.writer(f)
    write.writerow(columns_name)
    write.writerows(data)