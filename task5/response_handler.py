import requests
import fake_useragent

def get_response(link) -> requests.Response:
    UA = fake_useragent.UserAgent().random
    header = {
        'user-agent': UA
    }
    response = requests.get(url=link, headers=header)
    if response.status_code == 200:
        return response
    else:
        print(f'Запрос на страницу {link} произошёл с кодом {response.status_code}.')
        return get_response(link) if quest('Повторить запрос?') else None

def quest(text: str) -> bool:
    answ = input(f'{text} [y/n]: ')
    if answ == 'y':
        return True
    elif answ == 'n':
        return False
    else:
        print('Некорректный ответ, повторите попытку!')
        return quest(text)