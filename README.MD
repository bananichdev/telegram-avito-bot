# Телеграм бот
Телеграм бот, который ищет лучшие объявления на Авито

## Описание
Телеграм бот созданный с использованием фреймворка aiogram и веб-драйвера Selenium

## Технологии
* Python
* aiogram
* Selenium

## Как запустить
1. Склонируйте репозиторий
2. Создайте и активируйте виртуальное окружение
```commandline
python -m venv venv
source venv/Scripts/activate (для Windows)
source venv/bin/activate (для Linux)
```
3. Установите зависимости
```commandline
pip install -r requirements.txt
```
4. Создайте файл .env и укажите токен вашего бота и вашу систему
```commandline
TOKEN=YOUR_TOKEN
SYSTEM=your_system (win или linux)
```
5. Установите Chrome for Testing и ChromeDriver по ссылке [Link](https://googlechromelabs.github.io/chrome-for-testing) и переместите их в директорию app/parser
6. Запустите бота
```commandline
python3 run.py
```
