import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
data = pd.read_csv(r'E:\IDE\PY_10_Введение в Pandas\hh_database.csv', sep=";")


def get_education(arg):
    arg =' '.join(arg.split(' ')[:3])
    if'Высшее'in arg:
        return 'высшее'
    elif 'Неоконченное высшее' in arg:
        return 'неоконченное высшее'
    elif 'Среднее специальное' in arg:
        return 'среднее специальное'
    elif 'Среднее образование' in arg:
        return 'среднее'
data['Образование'] = data['Образование и ВУЗ'].apply(get_education)
data = data.drop('Образование и ВУЗ', axis=1)
print(data['Образование'].value_counts()['среднее'])


def get_sex(arg):
    if'Мужчина'in arg:
        return 'М'
    else:
        return 'Ж'
    
def get_age(arg):
    arg_splitted = arg.split(' ')
    year_words=['год', 'года', 'лет']
    for index, item in enumerate (arg_splitted):
        if item in year_words:
            return int(arg_splitted[index-1])

data['Пол'] = data['Пол, возраст'].apply(get_sex)
data['Возраст'] = data['Пол, возраст'].apply(get_age)
data = data.drop('Пол, возраст', axis=1)

print(round(data['Пол'].value_counts(normalize=True)['Ж'] * 100, 2))
print(round(data['Возраст'].mean(), 2))


def get_experience(arg):
    if arg is np.nan or arg == 'Не указано':
        return None
    year_words=['год', 'года', 'лет']
    month_words=['месяц', 'месяца', 'месяцев']
    arg_splitted = arg.split(' ')[:7]
    years = 0
    months = 0
    for index, item in enumerate (arg_splitted):
        if item in year_words:
            years = int(arg_splitted[index-1])
        if item in month_words:
            months = int(arg_splitted[index-1])
    return int(years*12 + months)
data['Опыт работы (месяц)'] = data['Опыт работы'].apply(get_experience)
data = data.drop('Опыт работы', axis=1)
print(round(data['Опыт работы (месяц)'].median()))


def get_city(arg):
    million_cities = ['Новосибирск', 'Екатеринбург', 'Нижний Новгород',
                      'Казань', 'Челябинск', 'Омск', 'Самара', 'Ростов-на-Дону', 
                      'Уфа', 'Красноярск', 'Пермь', 'Воронеж', 'Волгоград'
                     ]
    city = arg.split(' , ')[0]
    if (city == 'Москва') or (city == 'Санкт-Петербург'):
        return city
    elif city in million_cities:
        return 'город миллионник'
    else:
        return 'другие'
    
def get_ready_to_move(arg):
    if ('не готов к переезду' in arg) or ('не готова к переезду' in arg):
        return False
    elif 'хочу' in arg:
        return True
    else:
        return True
    
def get_ready_for_bisiness_trips(arg):
    if ('командировка' in arg):
        if ('не готов к командировкам' in arg) or('не готова к командировкам' in arg):
            return False
        else: 
            
            return True
    else:
        return False
    
data['Город'] = data['Город, переезд, командировки'].apply(get_city)
data['Готовность к переезду'] = data['Город, переезд, командировки'].apply(get_ready_to_move)
data['Готовность к командировкам'] = data['Город, переезд, командировки'].apply(get_ready_for_bisiness_trips)
data = data.drop('Город, переезд, командировки', axis=1)
print(round(data['Город'].value_counts(normalize=True)['Санкт-Петербург'] * 100)) 
print(round(data[data['Готовность к переезду'] & data['Готовность к командировкам']].shape[0] / data.shape[0] *100))


employments = ['полная занятость', 'частичная занятость',
              'проектная работа', 'волонтерство', 'стажировка']
charts = ['полный день', 'сменный график', 
         'гибкий график', 'удаленная работа',
         'вахтовый метод']
for employment, chart in zip(employments, charts):
    data[employment] = data['Занятость'].apply(lambda x: employment in x)
    data[chart] = data['График'].apply(lambda x: chart in x)
data = data.drop('Занятость', axis=1)
data = data.drop('График', axis=1)
print(data[data['проектная работа'] & data['волонтерство']].shape[0])
print(data[data['вахтовый метод'] & data['гибкий график']].shape[0])


def get_salary_num(arg):
    return float(arg.split(' ')[0])

def get_salary_currency(arg):
    currency_dict = {
        'USD': 'USD', 'KZT': 'KZT',
        'грн': 'UAH', 'белруб': 'BYN',
        'EUR': 'EUR', 'KGS': 'KGS',
        'сум': 'UZS', 'AZN': 'AZN'
    }
    curr = arg.split(' ')[1].replace('.', '')
    return 'RUB' if curr == 'руб' else currency_dict[curr]

path = r'E:\IDE\PY_10_Введение в Pandas\ExchangeRates.csv'
rates = pd.read_csv(path)                        # исправлено: sep по умолчанию ','
rates.columns = rates.columns.str.strip()
rates['date'] = pd.to_datetime(rates['date'].astype(str).str.strip(), dayfirst=True, errors='coerce').dt.date

data['Обновление резюме'] = pd.to_datetime(data['Обновление резюме'], dayfirst=True, errors='coerce').dt.date
data['ЗП (tmp)'] = data['ЗП'].apply(get_salary_num)
data['Курс (tmp)'] = data['ЗП'].apply(get_salary_currency)

merged = data.merge(
    rates,
    left_on=['Курс (tmp)', 'Обновление резюме'],
    right_on=['currency', 'date'],
    how='left'
)

merged['close'] = merged['close'].fillna(1)
merged['proportion'] = merged['proportion'].fillna(1)

data['ЗП (руб)'] = merged['close'].values * merged['ЗП (tmp)'].values / merged['proportion'].values

data = data.drop(['ЗП', 'ЗП (tmp)', 'Курс (tmp)'], axis=1, errors='ignore')
print(int(round(data['ЗП (руб)'].median() / 1000)))



import plotly
import plotly.express as px



    
