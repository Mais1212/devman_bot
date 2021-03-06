from time import sleep

import requests
import telegram
from environs import Env


def start_long_pooling(devman_token, telegram_token, telegram_chat_id):
    bot = telegram.Bot(telegram_token)

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
            message = f'Работа [{lesson_title}]({lesson_url}) готова'

            bot.send_message(
                text=message,
                chat_id=telegram_chat_id,
                parse_mode='MarkdownV2'
            )

        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            sleep(5)
            pass
        except requests.exceptions.HTTPError as exception:
            print(exception)


if __name__ == '__main__':
    env = Env()
    Env.read_env()
    devman_token = env('DEVMAN_TOKEN')
    telegram_token = env('TELEGRAM_TOKEN')
    telegram_chat_id = env('TG_CHAT_ID')

    start_long_pooling(devman_token, telegram_token, telegram_chat_id)
