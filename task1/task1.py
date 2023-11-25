from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import json

TASK_PATH = './task1/'
PAGES_PATH = f'{TASK_PATH}pages/'

def get_page_data(html_page):
    soup = BeautifulSoup(html_page, 'html.parser')
    page_data = dict()

    book_wrapper = soup.find('div', class_='book-wrapper')
    page_data['category'] = book_wrapper.find(string=re.compile("Категор")).split(':')[-1].strip()
    page_data['name'] = book_wrapper.find('h1', class_='book-title').text.strip()
    page_data['author'] = book_wrapper.find('p', class_='author-p').text.strip()
    page_data['volume'] = int(book_wrapper.find('span', class_='pages').text.split(':')[-1].split('страниц')[0].strip())
    page_data['year'] = int(book_wrapper.find('span', class_='year').text.split('Издано в')[-1].strip())
    page_data['ISBN'] = book_wrapper.find(string=re.compile("ISBN")).split(':')[-1].strip()
    page_data['description'] = book_wrapper.find(string=re.compile("Описан")).split('Описание')[-1].strip().lower()
    page_data['image_link'] = book_wrapper.find('img').get('src').lower()
    page_data['ratio'] = float(book_wrapper.find(string=re.compile("Рейтинг")).split(':')[-1].strip())
    page_data['views'] = int(book_wrapper.find(string=re.compile("Просмотр")).split(':')[-1].strip())

    return page_data

def analyse_data(df):
    # сортировка по полю year в порядке убывания 
    # и фильтрация датасета по значениям поля category ['роман', 'триллер', 'приключения']
    handled_df = df.copy()
    handled_df = handled_df.sort_values('year', ascending=False)
    handled_df = handled_df[handled_df['category'].isin(['роман', 'триллер', 'приключения'])]
    handled_df.to_json(f'{TASK_PATH}handled_dataset.json', orient='records', force_ascii=False) # запись обработанных данных
    # анализ числового столбца ratio и текстового столбца author
    nums_stats_df = df.ratio.describe().loc[['count', 'mean', 'min', 'max', 'std']]
    nums_stats_df['sum'] = sum(df.ratio)
    nums_stats = nums_stats_df.to_dict()
    nums_stats['column_name'] = nums_stats_df.name
    labels_stats_df = df.author.value_counts()
    labels_stats = labels_stats_df.to_dict()
    labels_stats['column_name'] = labels_stats_df.name
    stats = {
        'nums': nums_stats,
        'labels': labels_stats
    }
    with open(f'{TASK_PATH}stats.json', 'w', encoding='UTF-8') as f:
        json.dump(stats, f, ensure_ascii=False)

def main():
    df_cols = ['html_name', 'category', 'name', 'author', 'volume', 'year', 'ISBN', 'description', 'image_link', 'ratio', 'views']
    df = pd.DataFrame(columns=df_cols)
    for file in os.scandir(PAGES_PATH):
        with open(f'{PAGES_PATH}{file.name}', 'r', encoding='UTF-8') as f:
            html_page = f.read() 
        page_data = get_page_data(html_page) # сбор данных из страницы
        page_data['html_name'] = file.name # добавление имени файла с данными в данные страницы
        df.loc[len(df.index)] = page_data # добавление собранных со страницы данных
    df.to_json(f'{TASK_PATH}dataset.json', orient='records', force_ascii=False) # запись исходно собранных данных
    analyse_data(df)

if __name__ == '__main__':
    main()