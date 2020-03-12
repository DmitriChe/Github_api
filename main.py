from functions import parse_icos_to_db, get_number_of_pages, get_data_from_db, make_json
import pprint

from flask import Flask, render_template, request
app = Flask(__name__)


# связка route + template: при переходе по адресу '/' вывести шаблон index.html
@app.route("/", methods=['GET'])
def index():
    if request.method == 'GET':
        print('Зашли на страницу методом GET!')
    number_of_pages = get_number_of_pages()
    return render_template('index.html', number_of_pages=number_of_pages)


# при переходе методом post парсим ico сайт в базу данных, а затем берем данные из БД для своего сайта и файла json
@app.route("/", methods=['POST'])
def post():
    if request.method == 'POST':
        print('Зашли на страницу методом POST!')
        num = int(request.form['num_pages'])  # сколько страниц нужно спарсить
        print(f'Получен запрос отпарсить первые {num} страниц.')

        # парсим указанное число страниц и сохраняем в БД
        parse_icos_to_db(num)
        # читаем данные из БД в виде словаря
        ico_data_dict = get_data_from_db()
        # формируем json с данными для скачивания данных с нашего сайта
        make_json(ico_data_dict)
        one_ico_data = ico_data_dict[0]

        # проверка данных
        # pprint.pprint(ico_data_dict)
        for item in ico_data_dict.values():
            print(item['index'])
            print(item['name'])
            print(item['url'])

        # отрисовка шаблона (рендеринг шаблона)
        return render_template('index.html', one_ico_data=one_ico_data, ico_data_dict=ico_data_dict)


if __name__ == "__main__":
    app.run(debug=True)
