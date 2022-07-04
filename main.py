import asyncio
from pprint import pprint

import requests
import telegram
from environs import Env


def start_long_pooling(devman_token, telegram_token, chat_id):
    bot = telegram.Bot(telegram_token)

    headers = {
        'Authorization': f'Token {devman_token}'
    }
    url = 'https://dvmn.org/api/long_polling/'

    while True:
        try:
            response_json = requests.get(
                url, headers=headers, timeout=10).json()

            if response_json['status'] == 'timeout':
                params = {
                    'timestamp': response_json['timestamp_to_request']
                }
                response_json = requests.get(
                    url, headers=headers,
                    timeout=10,
                    params=params
                ).json()

            send_message(bot, response_json)

        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            pass


def send_message(bot, response_json, chat_id):
    lesson_title = response_json["new_attempts"][0]["lesson_title"]
    lesson_url = response_json["new_attempts"][0]["lesson_url"]
    message = f'Работа [{lesson_title}]({lesson_url}) готова'
    bot.send_message(text=message, chat_id=chat_id, parse_mode='MarkdownV2')


if __name__ == '__main__':
    env = Env()
    Env.read_env()
    devman_token = env('DEVMAN_TOKEN')
    telegram_token = env('TELEGRAM_TOKEN')
    chat_id = env('CHAT_ID')

    start_long_pooling(devman_token, telegram_token, chat_id)
