import requests
from bs4 import BeautifulSoup
from time import sleep
import json
import sqlite3
from sqlalchemy import create_engine, Column, String, Integer, Date, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# получение максимального числа страниц с данными ico
def get_number_of_pages(url='https://icobench.com/icos?'):

    html_doc = requests.get(url).text

    soup = BeautifulSoup(html_doc, 'html.parser')
    # print(soup.prettify())
    max_page_num = max([int(num.text) for num in soup.find_all('a', class_='num')])
    print(f'number of pages: {max_page_num}')
    return max_page_num


# Парсинг данных с ico-сайта в базу данных
def parse_icos_to_db(page_num):
    domain = 'https://icobench.com'
    url = f'{domain}/icos?'

    # получаем число страниц на сайте с ico
    max_page_num = get_number_of_pages(url)

    # если запрошенное пользователем число страниц больше, чем есть на сайте, то корректируем это число.
    if page_num > max_page_num:
        page_num = max_page_num

    # подключение к БД
    conn = sqlite3.connect('icoparser_db.db')  # коннектор к БД
    cursor = conn.cursor()  # курсор для запросов
    cursor.execute("delete from ico_datas")  # предварительная очистка таблицы

    # парсим данные с ico-сайта в переменные, а затем в БД
    for i in range(page_num):
        sleep(1)
        next_page_url = f'{url}page={i + 1}'
        print(f'current page url: {next_page_url}\n')
        html_doc = requests.get(next_page_url).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        ico_list = soup.find('div', class_='ico_list').find_all_next('tr')[1:-1]
        for item in ico_list:
            ico_name = item.find('div', class_='content').a.text.strip()
            ico_url = f"{domain}{item.find('div', class_='content').a.get('href')}"
            ico_description = item.find('p', class_='notranslate').text
            ico_dates = item.find_all('td', class_='rmv')
            ico_start_date = ico_dates[0].text
            ico_end_date = ico_dates[1].text
            ico_rating = item.find('div', class_='rate').text
            print(f'{ico_name}: {ico_url}\n{ico_description}')
            print(f'start date: {ico_start_date}\nend date: {ico_end_date}\nrating: {ico_rating}\n')

            # Запуск на исполнение запроса на добавление данных в БД
            cursor.execute(
                "insert into ico_datas (ico_name, ico_description, ico_start, ico_end, ico_rating, ico_url) values (?, ?, ?, ?, ?, ?)",
                (ico_name, ico_description, ico_start_date, ico_end_date, ico_rating, ico_url)
            )

    # Сохранение данных в БД и закрытие подключения
    conn.commit()
    conn.close()


# считывание данных из БД в словарь icos_data
def get_db_data_sqlite():
    # подключаемся к БД
    conn = sqlite3.connect('ico_db.sqlite')  # коннектор к БД
    cursor = conn.cursor()  # курсор для запросов
    # выбираем все данные из таблицы
    cursor.execute("select * from ico")
    db_data = cursor.fetchall()
    conn.close()  # закрываем соединение с БД

    # проверка результата
    print('***********************************')
    print(f'db_data: {db_data}')
    print('***********************************')

    # формируем словарь с данными из БД и возвращаем его
    icos_data = {}
    n = 0
    for item in db_data:
        icos_data[n] = {
            'name': item[1],
            'description': item[2],
            'start_date': item[3],
            'end_date': item[4],
            'rating': item[5],
            'url': item[6],
            'index': item[0],
        }
        n += 1

    return icos_data


# Парсинг данных с ico-сайта в базу данных с помощью sqlalchemy
def parse_icos_to_db_sqlalchemy(page_num, db_fname):
    domain = 'https://icobench.com'
    url = f'{domain}/icos?'

    # получаем число страниц на сайте с ico
    max_page_num = get_number_of_pages(url)

    # если запрошенное пользователем число страниц больше, чем есть на сайте, то корректируем это число.
    if page_num > max_page_num:
        page_num = max_page_num

    # создание движка для подключения к БД (с выводом инфо: echo=True)
    engine = create_engine(f'sqlite:///{db_fname}', echo=True)
    Base = declarative_base()

    # описание класса для таблицы в БД
    class Ico(Base):
        __tablename__ = 'ico'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        description = Column(Text)
        starts = Column(String)
        ends = Column(String)
        rating = Column(Float)
        url = Column(String)

        def __init__(self, name, desription, starts, ends, rating, url):
            self.name = name
            self.description = desription
            self.starts = starts
            self.ends = ends
            self.rating = rating
            self.url = url

        def __repr__(self):
            return "<Ico('%s', '%s', '%s', '%s', '%s', '%s'>" % (
                self.name, self.description, self.starts, self.ends, self.rating, self.url)

    # Создание таблицы
    Base.metadata.create_all(engine)
    # создание класса Сессии
    Session = sessionmaker(bind=engine)
    # создание сессии (подключения к БД)
    session = Session()
    # предварительная очистка таблицы
    session.query(Ico).delete()
    session.commit()
    # print('таблица очищена')

    # парсим данные с ico-сайта в переменные, а затем в БД
    for i in range(page_num):
        sleep(1)
        next_page_url = f'{url}page={i + 1}'
        print(f'current page url: {next_page_url}\n')
        html_doc = requests.get(next_page_url).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        ico_list = soup.find('div', class_='ico_list').find_all_next('tr')[1:-1]
        for item in ico_list:
            ico_name = item.find('div', class_='content').a.text.strip()
            ico_description = item.find('p', class_='notranslate').text
            ico_dates = item.find_all('td', class_='rmv')
            ico_start_date = ico_dates[0].text
            ico_end_date = ico_dates[1].text
            ico_rating = item.find('div', class_='rate').text
            ico_url = f"{domain}{item.find('div', class_='content').a.get('href')}"
            print(f'{ico_name}: {ico_url}\n{ico_description}')
            print(f'start date: {ico_start_date}\nend date: {ico_end_date}\nrating: {ico_rating}\n')

            # добавление обекта (строка таблицы) в сессию
            session.add(Ico(ico_name, ico_description, ico_start_date, ico_end_date, ico_rating, ico_url))
            # запись сессии в БД
            session.commit()


# считывание данных из БД в словарь icos_data
def get_db_data_sqlalchemy(db_fname):

    engine = create_engine(f'sqlite:///{db_fname}', echo=True)
    Base = declarative_base()

    class Ico(Base):
        __tablename__ = 'ico'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        description = Column(Text)
        starts = Column(String)
        ends = Column(String)
        rating = Column(Float)
        url = Column(String)

        def __init__(self, name, desription, starts, ends, rating, url):
            self.name = name
            self.description = desription
            self.starts = starts
            self.ends = ends
            self.rating = rating
            self.url = url

        def __repr__(self):
            return "<Ico('%s', '%s', '%s', '%s', '%s', '%s'>" % (
                self.name, self.description, self.starts, self.ends, self.rating, self.url)

    # создание класса Сессии
    Session = sessionmaker(bind=engine)

    # создание сессии (подключения к БД)
    session = Session()
    # запрос данных
    ico_query = session.query(Ico).all()

    for ico in ico_query:
        print(f'{ico.id}. {ico.name} - {ico.description} - {ico.starts} - {ico.ends} - {ico.rating} - {ico.url}')

    # проверка результата
    print('***********************************')
    print(f'db_data: {ico_query}')
    print('***********************************')

    # формируем словарь с данными из БД и возвращаем его
    icos_data = {}
    n = 0
    for ico in ico_query:
        icos_data[n] = {
            'index': ico.id,
            'name': ico.name,
            'description': ico.description,
            'start_date': ico.starts,
            'end_date': ico.ends,
            'rating': ico.rating,
            'url': ico.url
        }
        n += 1

    return icos_data


# сохранение данных в json
def make_json(data):
    # Создание json версии БД для скачивания пользователем с сайта
    with open('static/ico_data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))
