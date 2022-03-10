import json
import logging

import requests

from db import TOKEN_REFRESH_URL, TOKEN_TYPE, db

logger = logging.getLogger('Logger')


def refresh_token():
    logging.info('Начало обновления токена.')
    data = {'grant_type': 'refresh_token',
            'refresh_token': db.get('refresh_token')}
    try:
        new_token = requests.post(TOKEN_REFRESH_URL, json=data)
        token_data = new_token.json()
        db['access_token'] = f'{TOKEN_TYPE} {token_data["access_token"]}'
        db['refresh_token'] = token_data['refresh_token']
        logging.info('Новый токен записан в базу.')
    except json.JSONDecodeError:
        logger.error('При обновлении токена сервис вернул не валидный json')
        return False
    except requests.exceptions.RequestException:
        logger.error('Не удается подключиться к hh при обновлении токена.')
        return False
    except Exception as e:
        logger.error(e)
        return False
    logging.info('Токен обновлен.')
    return True


def is_token_fresh(my_data, what):
    if my_data.status_code == 403:
        logging.info(f'Страница {what} не доступна.')
        try:
            my_data = my_data.json()
            if my_data['access_token'] == 'token_expired':
                return refresh_token()
        except json.JSONDecodeError:
            logger.error(f'Cервис {what} вернул не валидный json')
        except KeyError:
            pass
        resp_desc = my_data.get('errors')
        logger.error(f'Проблема с доступом по токену: {resp_desc}')
        return False
    else:
        message = f'Не предвиденная ошибка при доступе в {what}.'
        logging.info(message)
        try:
            logger.error(f'{message} : {my_data.json()}')
        except json.JSONDecodeError:
            logger.error(f'{message} : сервис вернул не валидный json')
        return False


def token_check(response, what, func):
    if is_token_fresh(response, what):
        return func()
    return False


def negotiation_handler(data, func):
    try:
        headers = {'Authorization': db['access_token']}
        verdict = data['state']['name']
        if verdict not in ['Приглашение', 'Отказ']:
            return None
        vacancy_messages_url = data['messages_url']
        response = requests.get(vacancy_messages_url, headers=headers)
        if response.status_code != 200:
            return token_check(response, 'получение откликов', func)
        message = response.json()['items'][1]['text']
        vacancy_name = data['vacancy']['name']
        vacancy_city = data['vacancy']['area']['name']
        vacancy_url = data['vacancy']['alternate_url']
        return [verdict, message, vacancy_name, vacancy_city, vacancy_url]
    except requests.exceptions.RequestException:
        logger.error('Не удается подключиться к hh при обработке откликов.')
        return False, None
    except json.JSONDecodeError:
        logger.error('Cервис при обработке откликов вернул не валидный json')
        return False


def negotiations(data, func):
    last = data[0]
    last_negotiation = db.get('negotiation')
    main_data = []
    if last_negotiation != last:
        logging.info('Обработка откликов')
        for i in range(len(data)):
            initial_data = data[i]
            if initial_data == last_negotiation:
                break
            handled_data = negotiation_handler(initial_data, func)
            if not handled_data:
                continue
            main_data.append(handled_data)
        db['negotiation'] = last
        logging.info('Обработка откликов завершена')
        return True, main_data
    else:
        logging.info('Новых откликов нет')
        return True, None
