from bs4 import BeautifulSoup
import numpy as np
import json
import os

TASK_PATH = './task3/'
PAGES_PATH = f'{TASK_PATH}pages/'

def get_page_data(xml_data):
    soup = BeautifulSoup(xml_data, 'xml')
    file_data = {
        tag.name.strip(): tag.text.strip()
        for tag in soup.contents[0].children if tag != '\n'
    }
    return file_data

def analyse_data(dataset):
    # сортировка по полю distance в порядке возрастания 
    # и фильтрация датасета по значениям поля radius, по значениям больше 5 * 10**8
    handled_dataset = dataset.copy()
    handled_dataset = sorted(handled_dataset, key=lambda x: float(x['distance'].split(' million km')[0]), reverse=False)
    filtered_dataset = list(filter((lambda x: float(x['radius']) > 5 * 10**8), handled_dataset))
    with open(f'{TASK_PATH}handled_dataset.json', 'w', encoding='UTF-8') as f:
        json.dump(filtered_dataset, f, ensure_ascii=False)
    # анализ числовой колонки 'radius'
    radius_column = np.array([float(row['radius']) for row in dataset])
    nums_stats = {
        'count': int(len(radius_column)),
        'mean': float(radius_column.mean()),
        'min': float(min(radius_column)),
        'max': float(max(radius_column)),
        'std': float(radius_column.std()),
        'sum': float(sum(radius_column))
    }
    # анализ текстовой колонки 'constellation' и вывод частоты повторения значений в порядке возрастания
    constellation_column = [row['constellation'] for row in dataset]
    labels_stats = {
        label: constellation_column.count(label)
        for label in set(constellation_column)
    }
    labels_stats = dict(sorted(labels_stats.items(), key=lambda x: x[1]))
    stats = {
        'nums_radius': nums_stats,
        'labels_constellation': labels_stats
    }
    with open(f'{TASK_PATH}stats.json', 'w', encoding='UTF-8') as f:
        json.dump(stats, f, ensure_ascii=False)

def main():
    dataset = list()
    # считывание информации с файлов
    for file in os.scandir(PAGES_PATH):
        with open(f'{PAGES_PATH}{file.name}', 'r', encoding='UTF-8') as f:
            xml_data = f.read() 
        file_data = get_page_data(xml_data) # сбор данных из страницы
        file_data['file_name'] = file.name 
        dataset.append(file_data) # добавление собранных со страницы данных
    # запись считанных данных
    with open(f'{TASK_PATH}dataset.json', 'w', encoding='UTF-8') as f:
        json.dump(dataset, f, ensure_ascii=False)
    analyse_data(dataset)

if __name__ == '__main__':
    main()
