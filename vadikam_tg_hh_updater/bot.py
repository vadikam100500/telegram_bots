import logging
import time

import telegram

from db import (FIRST_ACCESS_TOKEN, FIRST_REFRESH_TOKEN, TOKEN_TYPE, chat_id,
                db, telegram_token, timeout)
from hh_api import get_negotiations, get_update

bot = telegram.Bot(token=telegram_token)


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_message(message):
    try:
        bot.send_message(chat_id, message)
        logging.info('Бот отправил сообщение')
    except TypeError:
        message = 'Проверьте введенный токен телеграма'
        logger.error(message)
        raise TypeError(message)
    except Exception as error:
        message = f'Бот не отправил сообщение в send_message, т.к. {error}'
        logger.error(message)
        raise Exception(message)


def main():
    try:
        message = 'Бот перезапустился'
        send_message(message)
        logging.info(message)
    except Exception as error:
        message = f'Бот упал с ошибкой: {error}'
        logger.error(message)

    while True:
        try:
            if get_update():
                logging.info('Обновление резюме прошло успешно')
            else:
                logger.error('Ошибка в API HH при обновлении резюме')
                time.sleep(timeout)
                continue
            result, data = get_negotiations()
            if result:
                if data:
                    for vacancy in data:
                        (verdict, message, vacancy_name,
                         vacancy_city, vacancy_url) = vacancy
                        send_message(
                            f'{verdict} по вакансии {vacancy_name}'
                            f'({vacancy_city}) \n\nCcылка на вакансию:'
                            f' {vacancy_url} \n\n'
                            f'Ответ от работодателя: {message}'
                        )
                    logging.info('Отклики получены')
            else:
                logger.error('Ошибка в API HH при получении откликов')
                time.sleep(timeout)
                continue

            time.sleep(timeout)

        except Exception as error:
            logger.error(f'Бот упал с ошибкой: {error}')
            time.sleep(timeout)


if __name__ == '__main__':
    if not db.get('access_token') and not db.get('refresh_token'):
        db['access_token'] = f'{TOKEN_TYPE} {FIRST_ACCESS_TOKEN}'
        db['refresh_token'] = FIRST_REFRESH_TOKEN

    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s:%(levelname)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('Logger')
    logger.setLevel(logging.ERROR)
    logger.addHandler(TelegramLogsHandler(bot, chat_id))

    main()
