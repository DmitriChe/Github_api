import requests
from bs4 import BeautifulSoup
from time import sleep
import json


def get_number_of_pages(url='https://icobench.com/icos?'):

    html_doc = requests.get(url).text

    soup = BeautifulSoup(html_doc, 'html.parser')
    # print(soup.prettify())
    max_page_num = max([int(num.text) for num in soup.find_all('a', class_='num')])
    print(f'number of pages: {max_page_num}')
    return max_page_num


def get_icos(page_num):
    domain = 'https://icobench.com'
    url = f'{domain}/icos?'

    max_page_num = get_number_of_pages(url)

    if page_num > max_page_num:
        page_num = max_page_num

    icos_data = {}
    n = 0
    for i in range(page_num):
        sleep(1)
        next_page_url = f'{url}page={i + 1}'
        print(f'current page url: {next_page_url}\n')
        html_doc = requests.get(next_page_url).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        ico_list = soup.find('div', class_='ico_list').find_all_next('tr')[1:-1]
        for item in ico_list:
            ico_name = item.find('div', class_='content').a.text
            ico_link = f"{domain}{item.find('div', class_='content').a.get('href')}"
            ico_description = item.find('p', class_='notranslate').text
            ico_dates = item.find_all('td', class_='rmv')
            ico_start_date = ico_dates[0].text
            ico_end_date = ico_dates[1].text
            ico_rating = item.find('div', class_='rate').text
            icos_data[n] = {
                'name': ico_name,
                'description': ico_description,
                'start_date': ico_start_date,
                'end_date': ico_end_date,
                'rating': ico_rating,
                'url': ico_link,
                'index': n
            }
            n += 1
            print(f'{ico_name}: {ico_link}\n{ico_description}')
            print(f'start date: {ico_start_date}\nend date: {ico_end_date}\nrating: {ico_rating}\n')

    with open('static/ico_data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(icos_data))

    return icos_data
