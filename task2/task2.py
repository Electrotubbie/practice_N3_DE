from bs4 import BeautifulSoup
import os
import re
import json
import numpy as np

TASK_PATH = './task2/'
PAGES_PATH = f'{TASK_PATH}pages/'

def get_page_data(html_page, file_name):
    soup = BeautifulSoup(html_page, 'html.parser')
    page_data = list()

    for item in soup.find_all('div', class_='product-item'):
        item_data = dict()
        item_data['file_name'] = file_name
        item_data['data_id'] = int(item.find('a', class_='add-to-favorite').get('data-id'))
        item_data['href'] = item.find_all('a')[1].get('href')
        item_data['src_img'] = item.find('img').get('src')
        item_data['title'] = item.find('span').text.strip()
        item_data['price'] = int(''.join(re.findall('\d+', item.find('price').text.strip())))
        item_data['bonus'] = int(''.join(re.findall('\d+', item.find('strong').text.strip())))
        item_data['params'] = {
            param.get('type'): param.text.strip()
            for param in item.find_all('li')
        }
        page_data.append(item_data)
        
    return page_data


def analyse_data(dataset):
    # сортировка по полю price в порядке убывания 
    # и фильтрация датасета по значениям поля title, по содержимому ['micron', 'seagate', 'sandisk']
    handled_dataset = dataset.copy()
    handled_dataset = sorted(handled_dataset, key=lambda x: x['price'], reverse=True)
    filter_phrases = ['micron', 'seagate', 'sandisk']
    filtered_dataset = list(filter(lambda x: max([phrase in x['title'].lower() for phrase in filter_phrases]), handled_dataset))
    with open(f'{TASK_PATH}handled_dataset.json', 'w', encoding='UTF-8') as f:
        json.dump(filtered_dataset, f, ensure_ascii=False)
    # анализ числовой колонки 'bonus'
    bonus_column = np.array([row['bonus'] for row in dataset])
    nums_stats = {
        'count': int(len(bonus_column)),
        'mean': float(bonus_column.mean()),
        'min': float(min(bonus_column)),
        'max': float(max(bonus_column)),
        'std': float(bonus_column.std()),
        'sum': float(sum(bonus_column))
    }
    # анализ текстовой колонки 'matrix' и вывод частоты повторения значений в порядке возрастания
    matrix_column = [row['params']['matrix'] for row in dataset if 'matrix' in row['params'].keys()]
    labels_stats = {
        label: matrix_column.count(label)
        for label in set(matrix_column)
    }
    labels_stats = dict(sorted(labels_stats.items(), key=lambda x: x[1]))
    stats = {
        'nums_bonus': nums_stats,
        'labels_matrix': labels_stats
    }
    with open(f'{TASK_PATH}stats.json', 'w', encoding='UTF-8') as f:
        json.dump(stats, f, ensure_ascii=False)

def main():
    dataset = list()
    # считывание информации с файлов
    for file in os.scandir(PAGES_PATH):
        with open(f'{PAGES_PATH}{file.name}', 'r', encoding='UTF-8') as f:
            html_page = f.read() 
        page_data = get_page_data(html_page, file.name) # сбор данных из страницы
        dataset.extend(page_data) # добавление собранных со страницы данных
    # запись считанных данных
    with open(f'{TASK_PATH}dataset.json', 'w', encoding='UTF-8') as f:
        json.dump(dataset, f, ensure_ascii=False)
    analyse_data(dataset)

if __name__ == '__main__':
    main()