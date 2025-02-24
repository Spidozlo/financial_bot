# Financial Bot

Это Telegram-бот для учёта доходов и расходов, который также осуществляет парсинг транзакций с внешнего сайта.

## Описание

Бот позволяет:
- Добавлять доходы и расходы;
- Получать статистику по расходам и доходам (например, по месяцу);
- Автоматически обновлять данные, получая актуальные транзакции с сайта через парсер.

## Особенности

- Парсинг транзакций с сайта с использованием `requests` и `BeautifulSoup`.
- Использование базы данных SQLite для хранения данных.
- Асинхронный Telegram-бот на основе фреймворка [aiogram](https://docs.aiogram.dev/).

## Требования

- Python 3.8+
- [aiogram](https://pypi.org/project/aiogram/)
- [requests](https://pypi.org/project/requests/)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [lxml](https://pypi.org/project/lxml/)

## Установка

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/spidozlo/financial_bot.git
   cd financial_bot

2.**Создайте и активируйте виртуальное окружение:**
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

3. **Установите зависимости:**
pip install -r requirements.txt

**Настройка**
Создайте файл config.py на основе шаблона config.example.py и заполните его необходимыми данными:

python
**Копировать**
API_TOKEN = "YOUR_TELEGRAM_BOT_API_TOKEN"
PARSER_USERNAME = "your_username_for_parser"
PARSER_PASSWORD = "your_password_for_parser"
Убедитесь, что config.py добавлен в .gitignore, чтобы приватные данные не попадали в публичный репозиторий.

**Запуск**
Чтобы запустить бота, выполните:
bash
python bot.py
Бот автоматически удаляет webhook и использует long polling для получения обновлений.