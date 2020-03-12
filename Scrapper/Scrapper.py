import requests
import time
import re
from bs4 import BeautifulSoup
import cPython
import urllib3
import re
import json
import lxml
import itertools


# заменить пробелы плюсами
def replace_space_to_plus(str):
    l = len(str)
    for i in range(0, l):
        if str[i] == ' ':
            str = str[:i] + '+' + str[i + 1:]
    return str


# убрать пробелы
def remove_spaces(str):
    l = len(str)
    for i in range(0, l):
        if str[i] == ' ':
            str = str[:i] + '' + str[i + 1:]
    return str


# все ссылки на странице
def get_links_on_page(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "lxml")
    links = []

    for link in soup.findAll('a'):
        links.append(link.get('href'))
    return links


# отфильтровать только ссылки на вакансии
def filter_links(links):
    count = 0
    f_links = []
    for i in links:
        if re.match('https://hh.ru/vacancy/', i):
            f_links.append(i)
            count += 1
    return f_links


# зарплата со страницы
def get_salary(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "lxml")
    sal_class = soup.find("p", {"class": "vacancy-salary"})
    return sal_class


# описание вакансии
def get_vacancy_description(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "lxml")
    desc_class = soup.findAll("div", {"class": "vacancy-description"})
    return desc_class


# зарплата с помощью api
def api_get_salary(url):
    base_url = 'https://api.hh.ru/'
    res = requests.get(base_url + url)
    if res:
        js = json.loads(res.text)
        sal = js['salary']
        return (sal['from'])
    else:
        print('error')


# найти общее количество вакансий
def soup_vacancies_amount(str):
    url = 'https://hh.ru/search/vacancy?text=' + replace_space_to_plus(str)
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "lxml")
    desc_class = soup.find("h1", {"class": "bloko-header-1"})
    desc_class = desc_class.text
    desc_class = re.match('\\d*\\s\\d*', desc_class)
    desc_class = desc_class.group(0).split()
    desc_class = ''.join(desc_class)
    print(desc_class)
    amount = int(desc_class)
    print('amount:', amount)
    return amount


# максимальное количество страниц
def max_pages(str):
    amount = soup_vacancies_amount(str)
    d = amount / 50
    if d >= 40:
        return 40
    else:
        return int(d)


# все вакансии по ключевому слову
def get_all_vacancies_all_regions(vacancy_name):
    base_url = 'https://hh.ru/search/vacancy?'
    url = base_url + 'text=' + replace_space_to_plus(vacancy_name)
    max_p = max_pages(vacancy_name)
    all_vacancies = []
    page_str = '&page='
    for i in range(0, int(max_p)):
        print('page:', i)
        url_c = url + page_str + str(i)
        filtered_links = filter_links(get_links_on_page(url_c))
        all_vacancies.append(filtered_links)
        print(all_vacancies[i])
    all_vacancies = list(itertools.chain.from_iterable(all_vacancies))
    return all_vacancies


# описание вакансии с помошью id
def get_vacancy_description_api(vacancy_id):
    base_url = 'https://api.hh.ru/'
    res = requests.get(base_url + 'vacancies/' + str(vacancy_id))
    if res:
        js = json.loads(res.text)
        return (js['description'])
    else:
        print('error')


def parse_vacancy_and_write_to_database():

all_vac = get_all_vacancies_all_regions('python')

#print(all_vac)
print(len(all_vac))
