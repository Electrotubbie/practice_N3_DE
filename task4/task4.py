from bs4 import BeautifulSoup
import numpy as np
import json
import os

TASK_PATH = './task4/'
PAGES_PATH = f'{TASK_PATH}pages/'

def get_page_data(xml_data, file_name):
    soup = BeautifulSoup(xml_data, 'xml')
    file_data = list()
    for item in soup.contents[0].children:
        if item != '\n':
            item_data = {
                tag.name.strip(): tag.text.strip()
                for tag in item.children if tag != '\n'
            }
            item_data['file_name'] = file_name
            file_data.append(item_data)
    return file_data

def analyse_data(dataset):
    # сортировка по полю rating в порядке убывания 
    # и фильтрация датасета по значениям поля material, по значениям НЕ ['полиэстер', 'нейлон']
    handled_dataset = dataset.copy()
    handled_dataset = sorted(handled_dataset, key=lambda x: float(x['rating']), reverse=True)
    filtered_dataset = list(filter((lambda x: x['material'].lower() not in ['полиэстер', 'нейлон']), handled_dataset))
    with open(f'{TASK_PATH}handled_dataset.json', 'w', encoding='UTF-8') as f:
        json.dump(filtered_dataset, f)
    # анализ числовой колонки 'reviews'
    reviews_column = np.array([float(row['reviews']) for row in dataset])
    nums_stats = {
        'count': int(len(reviews_column)),
        'mean': float(reviews_column.mean()),
        'min': float(min(reviews_column)),
        'max': float(max(reviews_column)),
        'std': float(reviews_column.std()),
        'sum': float(sum(reviews_column))
    }
    # анализ текстовой колонки 'category' и вывод частоты повторения значений в порядке возрастания
    category_column = [row['category'] for row in dataset]
    labels_stats = {
        label: category_column.count(label)
        for label in set(category_column)
    }
    labels_stats = dict(sorted(labels_stats.items(), key=lambda x: x[1]))
    stats = {
        'nums_reviews': nums_stats,
        'labels_category': labels_stats
    }
    with open(f'{TASK_PATH}stats.json', 'w', encoding='UTF-8') as f:
        json.dump(stats, f)

def main():
    dataset = list()
    # считывание информации с файлов
    for file in os.scandir(PAGES_PATH):
        with open(f'{PAGES_PATH}{file.name}', 'r', encoding='UTF-8') as f:
            xml_data = f.read() 
        file_data = get_page_data(xml_data, file.name)
        dataset.extend(file_data) # добавление собранных со страницы данных
    # запись считанных данных
    with open(f'{TASK_PATH}dataset.json', 'w', encoding='UTF-8') as f:
        json.dump(dataset, f)
    analyse_data(dataset)

if __name__ == '__main__':
    main()