import pandas as pd
import json

TASK_PATH = './task5/'

def analyse_data(dataset):
    handled_df = dataset.copy()
    handled_df = handled_df.drop_duplicates('new_link') # удаление дубликатов
    handled_df = handled_df.reset_index(drop='index') # сброс индексов после удаления строк
    new_cols = {
        'new_public_date': 'new_public_time',
        'new_public_time': 'new_public_date'
    } # смена имён столбцов new_public_date и new_public_time
    # из-за того, что долго парсил, решил не менять код парсинга
    handled_df = handled_df.rename(columns=new_cols)
    handled_df = handled_df.drop(columns=['new_public_time', 'new_text', 'new_tags'])
    handled_df['new_public_date'] = pd.to_datetime(handled_df['new_public_date'], format='mixed')
    df_to_analyse = handled_df.copy()
    # сортировка датасета по полю new_public_date
    # и фильтрация по полю new_category
    handled_df = handled_df.sort_values(by='new_public_date')
    handled_df = handled_df[handled_df['new_category'] == 'Коом жана турмуш']
    # сохранение полученного датасета
    handled_df.to_json(f'{TASK_PATH}handled_dataset.json', orient='records', force_ascii=False)
    # анализ числового столбца new_views и текстового столбца new_category
    nums_stats_df = df_to_analyse.new_views.describe().loc[['count', 'mean', 'min', 'max', 'std']]
    nums_stats_df['sum'] = sum(df_to_analyse.new_views)
    nums_stats = nums_stats_df.to_dict()
    nums_stats['column_name'] = nums_stats_df.name
    labels_stats_df = df_to_analyse.new_category.value_counts()
    labels_stats = labels_stats_df.to_dict()
    labels_stats['column_name'] = 'new_category'
    stats = {
        'nums': nums_stats,
        'labels': labels_stats
    }
    with open(f'{TASK_PATH}stats.json', 'w', encoding='UTF-8') as f:
        json.dump(stats, f, ensure_ascii=False)

df = pd.read_json(f'{TASK_PATH}dataset.json', encoding='UTF-8')
analyse_data(df)