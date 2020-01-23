from functions import get_icos, get_number_of_pages
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


@app.route("/", methods=['POST'])
def post():
    if request.method == 'POST':
        print('Зашли на страницу методом POST!')
        num = int(request.form['num_pages'])
        print(f'Получен запрос отпарсить первые {num} страниц.')

        ico_data_dict = get_icos(num)
        one_ico_data = ico_data_dict[0]

        # pprint.pprint(ico_data_dict)
        for item in ico_data_dict.values():
            print(item['index'])
            print(item['name'])
            print(item['url'])
        return render_template('index.html', one_ico_data=one_ico_data, ico_data_dict=ico_data_dict)


if __name__ == "__main__":
    app.run(debug=True)
