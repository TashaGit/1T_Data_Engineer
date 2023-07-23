### Импортируем библиотеки
import requests
import pandas as pd
import psycopg2


### Зададим переменные для парсинга курса валют.
#### Выберем для выполнения задания следующие валюты:
    # - Биткоин ('BTC')
    # - Евро ('EUR')
    # - Британскй фунт стерлингов ('GBR')
    # - Японская йена ('JPY')
    # - Китайсий юань ('CNY')
start_date = '2023-06-01'
end_date = '2023-06-30'
bases = ['BTC', 'EUR', 'GBR', 'JPY', 'CNY']
symbols = 'RUB'
format = 'CSV'


### Создадим цикл и пройдемся по списку валют, значение курса которых нам необходимо спарсить. Сохраним результат парсинга по каждой валюте в формате *.csv.
#### Полученные файлы:
    # - exchange_june2023_BTC.csv
    # - exchange_june2023_EUR.csv
    # - exchange_june2023_GBR.csv
    # - exchange_june2023_JPY.csv
    # - exchange_june2023_CNY.csv
for base in bases:
    response = requests.get('https://api.exchangerate.host/timeseries?',
                                params={'base': base,
                                        'start_date': start_date,
                                        'end_date': end_date,
                                        'symbols': symbols,
                                        'format': format
                                })

    with open(f'./csv_files/exchange_june2023_{base}.csv', 'wb') as f:
        f.write(response.content)


### Напишем цикл, в котором прочитаем каждый полученный файл по каждой валюте *.csv средствами
# Pandas для замены разделителя десятичных знаков с "," на ".", чтобы данные таблицы корректно
# загрузились в базу данных. Выведем на печать первые 5 строк таблицы по каждой валюте.
for base in bases:
    df = pd.read_csv(f'./csv_files/exchange_june2023_{base}.csv', decimal=',', index_col=False)
    df = pd.DataFrame(df)
    df.to_csv(f'./csv_files/exchange_june2023_{base}.csv', index=False)
    print()
    print(f'Первые 5 строк значений валюты {base}:')
    print(df[:5])


