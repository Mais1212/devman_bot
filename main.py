import logging
from time import sleep

import requests
import telegram
from environs import Env


class TgLoggerHandler(logging.Handler):
    def __init__(self, token: str, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.token = token

        self.bot = telegram.Bot(token=self.token)

    def emit(self, record):
        message = self.format(record)
        self.bot.send_message(self.user_id, message, parse_mode="HTML")


def start_long_pooling(devman_token, telegram_token, telegram_chat_id):
    bot = telegram.Bot(telegram_token)
    logger.info("Бот запущен.")

    headers = {
        'Authorization': f'Token {devman_token}'
    }
    url = 'https://dvmn.org/api/long_polling/'

    while True:
        params = {}
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10,
                params=params
            )
            response.raise_for_status()

            user_reviews = response.json()
            if user_reviews['status'] == 'timeout':
                params = {
                    'timestamp': user_reviews['timestamp_to_request']
                }
                continue
            elif user_reviews['status'] == 'found':
                params = {
                    'timestamp': user_reviews['last_attempt_timestamp']
                }

            lesson_title = user_reviews["new_attempts"][0]["lesson_title"]
            lesson_url = user_reviews["new_attempts"][0]["lesson_url"]
            message = f'Работа[{lesson_title}]({lesson_url}) готова\.'

            bot.send_message(
                text=message,
                chat_id=telegram_chat_id,
                parse_mode='MarkdownV2'
            )

        except requests.exceptions.ReadTimeout:
            logger.info("Привышено время ожидания.")
        except requests.exceptions.ConnectionError:
            logger.error("Потеряно подключение к интернету.")
            sleep(5)
        except requests.exceptions.HTTPError as exception:
            logger.error(exception)
        except Exception as exception:
            logger.error(exception)
            exit()


if __name__ == '__main__':
    env = Env()
    Env.read_env()
    devman_token = env('DEVMAN_TOKEN')
    telegram_token = env('TELEGRAM_TOKEN')
    telegram_debug_token = env('TELEGRAM_DEBUG_TOKEN')
    telegram_chat_id = env('TG_CHAT_ID')

    logger = logging.getLogger("Telegram logger")
    logger.setLevel(logging.WARNING)
    logger.addHandler(TgLoggerHandler(telegram_debug_token, telegram_chat_id))

    start_long_pooling(devman_token, telegram_token, telegram_chat_id)
