# homework_bot
python telegram bot
## Описание проекта
Бот опрашивает API сервис Практикум.Домашка, чтобы проверить статус домашней работы студента (один раз в 10 минут). Бот отправляет пользователю сообщение в Telegram с информацией о статусе домашней работы, логирует свою работу и сообщает о важных ошибках (уровни critical, error) сообщением в Telegram.

Возможны следующие статусы домашней работы:

- "Работа проверена: ревьюеру всё понравилось. Ура!"
- "Работа взята на проверку ревьюером."
- "Работа проверена: у ревьюера есть замечания."

## Запуск проекта локально
Клонировать репозиторий и перейти в него в командной строке:

git@github.com:Alex913798/homework_bot
Создать и активировать виртуальное окружение:

python3 -m venv venv
Если у вас Linux/MacOS:

source env/bin/activate
Если у вас windows

source venv/scripts/activate
python3 -m pip install --upgrade pip
Установить зависимости из файла requirements.txt:

pip install -r requirements.txt
Создать файл .env со следующими данными:

- PRACTICUM_TOKEN = 
- TELEGRAM_TOKEN = 
- TELEGRAM_CHAT_ID =
- Запустить проект:

python homework.py

## Автор проекта
Александр Ермаков