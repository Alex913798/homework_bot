import os
import requests
import logging
import time
import telegram
from dotenv import load_dotenv
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
    for var in var_list:
        if not var:
            return False
    return True


def send_message(bot, message):
    """Отправляет сообщения в телеграм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено')
    except Exception as error:
        logging.error(f'Сообщение не отправлено: {error}')


def get_api_answer(timestamp):
    """Получает ответ от сервера."""
    try:
        payload = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.exceptions.RequestException:
        ('Ошибка сетевого соединения')
    if response.status_code != 200:
        logging.error('Сбой при запросе к эндпоинту')
        raise Exception('Сбой при запросе к эндпоинту')
    return response.json()


def check_response(response):
    """Проверяет ответ сервера."""
    if len(response) == 0:
        logging.error('Ответ сервера содержит пустой словарь')
        raise KeyError('Ответ сервера содержит пустой словарь')
    if not isinstance(response, dict):
        logging.error('Тип данных - не словарь')
        raise TypeError('Тип данных - не словарь')
    if 'homeworks' not in response:
        logging.error('отсутствует ожидаемый ключ homework')
        raise KeyError('отсутствует ожидаемый ключ homework')
    if 'current_date' not in response:
        logging.error('отсутствует ожидаемый ключ current_date')
        raise KeyError('отсутствует ожидаемый ключ current_date')
    if not isinstance(response.get('homeworks'), list):
        logging.error('Тип данных - не список')
        raise TypeError('Тип данных - не список')
    return response['homeworks']


def parse_status(homework):
    """Поверяет статус домашней работы. Формирует сообщение для отправки."""
    if 'homework_name' not in homework:
        logging.error('отсутствует ожидаемый ключ homework_name')
        raise Exception('отсутствует ожидаемый ключ homework_name')
    else:
        homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if homework_status not in HOMEWORK_VERDICTS:
        logging.error('Неизвестный статус домашней работы')
        raise KeyError('Неизвестный статус домашней работы')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    error_message = {'error': None, }
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
            if len(homeworks) == 0:
                logging.debug('В ответе отсутствуют новые статусы работы')
            else:
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)
            timestamp = response.get('current_date')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if error_message['error'] != message:
                send_message(bot, message)
            error_message['error'] = message
        else:
            error_message['error'] = None
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
