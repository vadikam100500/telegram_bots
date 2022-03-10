import json
import logging

import requests

from db import NEGOTIATIONS_URL, RESUME_URL, db
from utils import negotiations, token_check

logger = logging.getLogger('Logger')


def get_update():
    logging.info('Начало обновления резюме')
    headers = {'Authorization': db['access_token']}
    try:
        response = requests.get(RESUME_URL, headers=headers)
        if response.status_code != 200:
            return token_check(response, 'получение резюме', get_update)
        logging.info('Страница резюме доступна.')
        data = response.json()
        skills = data['skills']
        if skills[-3:] != '^_^':
            update_data = f"{skills} ^_^"
        else:
            update_data = skills[:-3]
        response = requests.put(RESUME_URL, headers=headers,
                                json={'skills': update_data})
        if response.status_code != 204:
            return token_check(response, 'обновление резюме', get_update)
    except requests.exceptions.RequestException:
        logger.error('Не удается подключиться к hh при обновлении.')
        return False
    except json.JSONDecodeError:
        logger.error('Cервис при обновлении вернул не валидный json')
        return False
    logging.info('Резюме обновлено')
    return True


def get_negotiations():
    logging.info('Начало получения откликов')
    headers = {'Authorization': db['access_token']}
    try:
        response = requests.get(NEGOTIATIONS_URL, headers=headers)
        if response.status_code != 200:
            return token_check(response, 'получение откликов',
                               get_negotiations)
        data = response.json()['items']
        if not data:
            logging.info('Отликов нет')
            return True, None
        logging.info('Отклики получены')
        return negotiations(data, get_negotiations)
    except requests.exceptions.RequestException:
        logger.error('Не удается подключиться к hh при получении откликов.')
        return False, None
    except json.JSONDecodeError:
        logger.error('Cервис при получении откликов вернул не валидный json')
        return False
