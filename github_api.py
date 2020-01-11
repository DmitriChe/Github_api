import requests
import pprint
import base64
import json

DOMAIN = 'https://api.github.com/'

with open('github_token', 'r') as f:
    token = f.readline()

# # 1. auth with request
# result = requests.get(url, auth=('DmitriChe', token))
#
# # 2. auth with headers
# headers = {
#     'Authorization': f'token {token}',
# }
# result = requests.get(url, headers=headers)

# 3. auth with session
session = requests.Session()
session.auth = ('DmitriChe', token)


print('\n\n****************** ПОИСК УЯЗВИМОСТЕЙ В КОДЕ ******************')
print('\n****************** Открытые логины и пароли ******************\n')

search_url = 'search/code'
request_github = 'q=' \
                 'EMAIL_HOST_USER+' \
                 'EMAIL_HOST_PASSWORD+' \
                 'in:file+' \
                 'filename:settings+' \
                 'filename:py+' \
                 'language:django+' \
                 'language:python'  # +repo:jquery/jquery

url = DOMAIN + search_url + '?' + request_github
code = session.get(url).status_code
print(f'status code: {code}')

result = session.get(url).json()
items = result['items']

all_info = {}

for item in items:
    file_path = item['url']
    f = session.get(file_path).json()
    f = base64.b64decode(f['content']).decode('utf-8')
    f = f.replace(' = ', '=').replace('\n', ' ').split(' ')
    info = {'emails': [],
            'passwords': [],
            'file_url': '',
            'error_type': ['открытые логины и пароли', ],
            'status': ['содержит уязвимость', ]}

    for elem in f:
        if elem.find('EMAIL_HOST_USER') >= 0 and elem.find('=\'') >= 0:
            splited = elem.split('=')[1].replace('\'', '')
            if splited != '':
                print(f"{elem.split('=')[0]} == {splited}")
                if splited not in info['emails']:
                    info['emails'].append(splited)

        elif elem.find('EMAIL_HOST_PASSWORD') >= 0 and elem.find('=\'') >= 0:
            splited = elem.split('=')[1].replace('\'', '')
            if splited != '':
                print(f"{elem.split('=')[0]} == {splited}")
                if splited not in info['passwords']:
                    info['passwords'].append(splited)

        if info['emails'] and info['passwords']:
            info['file_url'] = item['html_url']
            all_info[item['repository']['html_url']] = info


print('\n****************** используется функция eval ******************\n')

search_url = 'search/code'
request_github = 'q=' \
                 'eval+' \
                 'in:file+' \
                 'language:python'

url = DOMAIN + search_url + '?' + request_github
code = session.get(url).status_code
print(f'status code: {code}')

result = session.get(url).json()
items = result['items']

for item in items:

    info = {'emails': [],
            'passwords': [],
            'file_url': item['html_url'],
            'error_type': ['используется функция eval', ],
            'status': ['содержит уязвимость', ]}

    print('Обнаружена уязвимость: используется функция eval! ')

    if not item['repository']['html_url'] in all_info.keys():
        all_info[item['repository']['html_url']] = info
    else:
        all_info[item['repository']['html_url']]['error_type'] = info['error_type']
        all_info[item['repository']['html_url']]['status'] = info['status']


print('\n****************** используется модуль pickle ******************\n')

search_url = 'search/code'
request_github = 'q=' \
                 'pickle+' \
                 'in:file+' \
                 'language:python'

url = DOMAIN + search_url + '?' + request_github
code = session.get(url).status_code
print(f'status code: {code}')

result = session.get(url).json()
items = result['items']

for item in items:

    info = {'emails': [],
            'passwords': [],
            'file_url': item['html_url'],
            'error_type': ['используется модуль pickle', ],
            'status': ['содержит уязвимость', ]}

    print('Обнаружена уязвимость:  используется модуль pickle! ')

    if not item['repository']['html_url'] in all_info.keys():
        all_info[item['repository']['html_url']] = info
    else:
        all_info[item['repository']['html_url']]['error_type'] = info['error_type']
        all_info[item['repository']['html_url']]['status'] = info['status']


print('\n****************** локально отключен csrf token ******************\n')

search_url = 'search/code'
request_github = 'q=' \
                 'csrf_exempt+' \
                 'in:file+' \
                 'language:django+' \
                 'language:python'  # +repo:jquery/jquery

url = DOMAIN + search_url + '?' + request_github
code = session.get(url).status_code
print(f'status code: {code}')

result = session.get(url).json()
items = result['items']

for item in items:

    info = {'emails': [],
            'passwords': [],
            'file_url': item['html_url'],
            'error_type': ['локально отключен csrf token', ],
            'status': ['потенциально опасен', ]}

    print('Потенциальная опасность: csrf token локально отключен! ')

    if not item['repository']['html_url'] in all_info.keys():
        all_info[item['repository']['html_url']] = info
    else:
        all_info[item['repository']['html_url']]['error_type'] = info['error_type']
        all_info[item['repository']['html_url']]['status'] = info['status']


print('\n****************** отключен csrf token ******************\n')
# В settings.py в константе MIDDLEWARE_CLASSES  отстутствует или закоменчен 'django.middleware.csrf.CsrfViewMiddleware'

search_url = 'search/code'
request_github = 'q=' \
                 'MIDDLEWARE_CLASSES+' \
                 'in:file+' \
                 'filename:settings+' \
                 'filename:py+' \
                 'language:django+' \
                 'language:python'  # +repo:jquery/jquery

url = DOMAIN + search_url + '?' + request_github
code = session.get(url).status_code
print(f'status code: {code}')

result = session.get(url).json()
items = result['items']

for item in items:
    file_path = item['url']
    f = session.get(file_path).json()
    f = base64.b64decode(f['content']).decode('utf-8')
    f = f.replace('\n', '').replace('  ', '').replace(' ', '')

    if f.find('django.middleware.csrf.CsrfViewMiddleware') == -1 \
            or f.find("#'django.middleware.csrf.CsrfViewMiddleware'") >= 0:
        print('Есть УЯЗВИМОСТЬ!!! отключен csrf token...')
        info = {'emails': [],
                'passwords': [],
                'file_url': item['html_url'],
                'error_type': ['отключен csrf token', ],
                'status': ['потенциально опасен', ]}

        if not item['repository']['html_url'] in all_info.keys():
            all_info[item['repository']['html_url']] = info
        else:
            all_info[item['repository']['html_url']]['error_type'] = info['error_type']
            all_info[item['repository']['html_url']]['status'] = info['status']

    elif f.find('django.middleware.csrf.CsrfViewMiddleware') >= 0:
        print('Все в порядке - уязвимости нет!')


print('\n****************** ИТОГОВЫЙ JSON с ДАННЫМИ ******************\n')
pprint.pprint(all_info)
with open('result.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(all_info))
