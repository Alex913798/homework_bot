import os
import requests
import logging
import time
import telegram
from http import HTTPStatus
from dotenv import load_dotenv
from exceptions import RequestError, ConnectError
load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(leveltime)s, %(message)s',
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def check_tokens():
    """Проверяет наличие токена."""
    var_list = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(var_list)


def send_message(bot, message):
    """Отправляет сообщения в телеграм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено')
    except Exception as error:
        logging.error(f'Сообщение не отправлено: {error}')


def get_api_answer(timestamp):
    """Получает ответ от сервера."""
    payload = {'from_date': timestamp}
    try:
        logging.debug('Отправка запроса к эндпоинту')
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != HTTPStatus.OK:
            raise RequestError('Ошибка при запросе к эндпоинту')
        return response.json()
    except Exception:
        raise ConnectError('Ошибка сетевого соединения')


def check_response(response):
    """Проверяет ответ сервера."""
    if not response:
        raise KeyError('Ответ сервера содержит пустой словарь')
    if not isinstance(response, dict):
        raise TypeError('Тип данных - не словарь')
    if 'homeworks' not in response:
        raise KeyError('отсутствует ожидаемый ключ homework')
    if 'current_date' not in response:
        raise KeyError('отсутствует ожидаемый ключ current_date')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Тип данных - не список')
    return response['homeworks']


def parse_status(homework):
    """Поверяет статус домашней работы. Формирует сообщение для отправки."""
    if 'homework_name' not in homework:
        raise Exception('отсутствует ожидаемый ключ homework_name')
    else:
        homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError('Неизвестный статус домашней работы')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    error_message = None
    status_message = None
    if not check_tokens():
        logging.critical('Отсутствуют обязательные пепеменные окружения./n'
                         'Работа программы завершена')
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if not homeworks:
                logging.debug('В ответе отсутствуют новые статусы работ')
            else:
                message = parse_status(homeworks[0])
                if status_message != message:
                    send_message(bot, message)
                status_message = message
            timestamp = response.get('current_date')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if error_message != message:
                send_message(bot, message)
            error_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
