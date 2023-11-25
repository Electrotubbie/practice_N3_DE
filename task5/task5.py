'''
В данной работе реализован парсер списка новостей из киргизского новостного ресурса.
Реализовано получение максимально допустимой страницы.
Перебор и заполнение датасета информацией с каждой страницы.
'''

from bs4 import BeautifulSoup
import pandas as pd
import time
import regex as re
from tqdm import tqdm
import requests
# response_handler - это мои попытки попробовать в рекурсию 
# и предотвращение потери информации путём обращения к пользователю
# есть ощущение, что на текущем этапе это рудимент, от которого лучше избавиться
# для минимизации общения с пользователем, но оставил ради интереса услышать рекацию от вас :)
from response_handler import get_response 

T_PAUSE = 0.5
TASK_PATH = './task5/'

news_link = 'https://www.super.kg/kabar'

def get_pages_num(link: str) -> int:
    main_news_page = get_response(link)
    if main_news_page:
        soup = BeautifulSoup(main_news_page.text, 'lxml')
        max_page_num = max([int(tag.text) for tag in soup.find_all("a", class_="page-link") if tag.text.isdigit()]) # поиск максимального числа в плашке выбора страницы
        return max_page_num
    else:
        return 0
    
def get_new_list_on_page(page_id: int) -> list[BeautifulSoup]:
    link = 'https://www.super.kg/kabar' + f'?page={page_id}'
    news_page = get_response(link)
    soup = BeautifulSoup(news_page.text, 'lxml')
    # все строки с короткой информацией о новостях описаны в html таблице, которая ищется по тегу div и классу mt-4 d-flex flex-row jitem
    news_table = soup.find_all("div", class_="mt-4 d-flex flex-row jitem")
    return news_table
    
def get_new_data(new):
    # парсинг информации с заголовком, просмотрами, ссылкой
    title_info = new.find("div", class_=re.compile("lh-\dp e_\d m_\d")).find("a", class_="text-decoration-none") # поиск тега, содержащего заголовок, количество просмотров и ссылку на новость
    title_strings = [s.strip() for s in title_info.strings if s not in ('\n', '(фото)', '(видео)')] # считывание всех строк предыдущего тега из итератора strings
    new_views = int(title_strings[-2]) # считывание количества просмотров для новости из списка
    new_title = ' '.join(title_strings[:-2]) # считывание заголовка новости
    new_link = title_info.get('href') # считывание ссылки на новость
    # парсинг информации с категорией, датой, временем
    category_info = new.find("div", class_="cat-color") # считывание тега, содержащего дату публикации, время, а также наименование категории новости
    category_strings = [s for s in category_info.strings if s not in ['\n', ' ', '|']] # считывание всех строк предыдущего тега из итератора strings
    new_category = category_strings[1] 
    [new_public_date, new_public_time] = category_strings[0].split(' ') # в данной строке я перепутал дату и время, оставил как есть, чтоб совпадало с длительно спарсенным датасетом 
    # создание словаря для записи в датасет
    new_info = {
            'new_title': new_title,
            'new_text': pd.NA,
            'new_category': new_category,
            'new_public_date': new_public_date,
            'new_public_time': new_public_time,
            'new_link': new_link,
            'new_tags': 'Na',
            'new_views': new_views
            }
    return new_info

def main():
    main_df = pd.DataFrame(columns=['new_title', 'new_text', 'new_category', 'new_tags', 'new_public_date', 'new_public_time', 'new_link', 'new_views'])
    # получение максимального числа страниц на ресурсе
    max_page = get_pages_num(news_link)
    # перебор страниц и получение с них информации
    # for page_id in tqdm(range(1, max_page + 1, 1)): # парсил с этой строкой до достижения примерно подоходящего размера файла
    for page_id in tqdm(range(1, 91, 1)): # оставил эту строку, чтоб меньше ждать
        # пауза для того, чтоб не отправлять часто запросы
        time.sleep(T_PAUSE)
        news_list = list()
        # любым путём получаем список новостей из страницы
        while not news_list:
            try:
                news_list = get_new_list_on_page(page_id)
            except requests.exceptions.ConnectTimeout as ex:
                tqdm.write(str(ex))
                time.sleep(60)
            except Exception as ex:
                tqdm.write(str(ex))
        # считывание информации о новостях из списка новостей
        for new in news_list:
            try:
                new_data = get_new_data(new)
                main_df.loc[len(main_df.index)] = [new_data[item] for item in ['new_title', 'new_text', 'new_category', 'new_tags', 'new_public_date', 'new_public_time', 'new_link', 'new_views']]
            except Exception as ex:
                tqdm.write(f'Парсинг страницы {page_id}/{max_page} закончился ошибкой {str(ex)}')
                continue
        # сохранение датасета каждые 30 считанных страниц
        if page_id%30 == 0:
            main_df.to_json(f'{TASK_PATH}dataset.json', orient='records', force_ascii=False)
    # результирующее сохранение датасета, до которого я так и не добрался
    main_df.to_json(f'{TASK_PATH}dataset.json', orient='records', force_ascii=False)

# анализ датасета выполнен в отдельном файле analyse_data.py
# в данном файле выполнен парсинг

if __name__ == '__main__':
    main()