from bs4 import BeautifulSoup
import requests as r
import json
import os
from configs import URL, MAX_PAGES, headers, DOMEN

class Parser:
    def __init__(self, url: str, headers: dict[str, str], domen: str, max_pages: int=1):
        self.url = url
        self.heafers = headers
        self.domen = domen
        self.max_pages = max_pages

    def get_data(self, url: str, domen: str) -> dict:
        '''
        считывает страницу сайта и сохраняет словарик с названием: {ссылкой и лого сайта}
        а так же делает копию полученный странички
        '''
        # словарь для сохранения данных
        startup_data: dict[str, str] = {}
        # проходимся по всем страницам пагинации до последней
        for i in range(1, self.max_pages+1):
            page = f'/page/{i}/'
            # на каждой итерации прибавляем номер страницы
            url_page = url+page
            respond = r.get(url_page, headers=self.headers)
            
            # доп проверка если страницы нет, то выходим из цикла
            if respond.status_code == 404:
                break
            src = respond.text
            # создаем отдельную папку для каждой страницы
            folder_name = f'dinamic_site_pages/data_{i}'
            # если папка не существует, то создаем ее
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)

            # записываем каждую страничку файлом в отдельную папку
            with open(f'{folder_name}/dinamyc_site_example{i}.html', 'w', encoding='utf-8') as file:
                file.write(src)

            # считываем каждую страничку записанную на локальный компьютер
            # чтобы не ддосить сайт
            with open(f'{folder_name}/dinamyc_site_example{i}.html', 'r', encoding='utf-8') as file:
                src = file.read()
            
            soup = BeautifulSoup(src, 'lxml')
            all_startup_hrefs = soup.find_all('a', class_='projects_list_b')
            
            temp: dict = dict()
            # запрещенные в винде символы для названия файла
            forbiden = ['"', ':', '<', '>', '|', '?', '*', "'", '/', '\\']
            for startup in all_startup_hrefs:

                # получаем название проекта
                title: str = startup.find('div', class_='title').text
                for symble in forbiden:
                    if symble in title:
                        title = title.replace(symble, '')

                # получаем ссылку на страничку проекта
                href = startup.get('href')

                # получаем лого проекта если есть
                try:
                    image = startup.find('div', class_='rich_media').get('style').split('url')
                    image = domen+image[1][1:-1]
                except:
                    image = 'no logo'

                # данные сохраняем во временный словарь 
                temp[title] = {
                    'url': href,
                    'logo': image,
                }

            # сохранил словарь в котором ключ - номер страницы, а значение словарь с данными стартапов
            startup_data[i] = temp
        
        return startup_data





    def get_data_startup(self, data: dict) -> list[dict]:
        '''
        принимает словрь - результат функции get_data
        проходится по всем проектам на каждой странице, 
        сохраняет странички проектов в папке для каждой страницы пагинации
        возвращает список список с нужной нам информацией
        '''
        startapp_list: list[dict] = []
        for page, projects in data.items():
            print(page, projects)
            for title, iner_data in projects.items():
                url = iner_data['url']
                responce = r.get(url, headers=self.headers)
                src = responce.text

                folder_name = f'dinamic_site_pages/data_{page}/projects'
                if not os.path.exists(folder_name):
                    os.mkdir(folder_name)

                with open(f'{folder_name}/{title}.html', 'w', encoding='utf-8') as file:
                    file.write(src)
                
                with open(f'{folder_name}/{title}.html', 'r', encoding='utf-8') as file:
                    src = file.read()

                
                soup = BeautifulSoup(src, 'lxml')
                # забираем краткое описание проекта
                logo = iner_data['logo']


                short_description = soup.find('div', class_='main_d').find('span').text


                idea = soup.find('div', id='IDEA').find('span', {'itemprop':"description"}).text


                startapp_info = {
                            'title': title,
                            'logo': logo,
                            'short_description': short_description,
                            'idea': idea,
                }
                startapp_list.append(startapp_info)

        return startapp_list
        




    def write_data_to_json(self, startups: list)-> None:
        '''
        Принимает список с информацией которую нужно вытащить - результат раоты функции get_data_startup
        и сохраняет ее в json формате
        ''' 
        for i, startup in enumerate(startups):
            with open(f'dinamic_site_pages/startups_data.json', 'a', encoding='utf-8') as file:
                if i>0:
                    file.write(',\n')
                json.dump(startup, file, indent=4, ensure_ascii=False)

        



