# Foodgram
![CI](https://github.com/Elithabeth2003/foodgram/actions/workflows/main.yml/badge.svg)

## Описание

Проект «Фудграм» — это сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По [адресу](http://localhost) изучите фронтенд веб-приложения, а по [адресу](http://localhost/api/docs/) — спецификацию API.

## Автор

[Elithabeth2003](https://github.com/Elithabeth2003)

## Функциональность

- Регистрация и авторизация пользователей
- Создание и редактирование профилей питомцев
- Загрузка и просмотр фотографий котов
- Поиск и подписка на других пользователей
- Ведение блога о жизни своих питомцев

## Технологический стек

- Python
- Django
- Django REST Framework
- Gunicorn
- Nginx
- Docker Compose
- GitHub Actions
- PostgreSQL (SQLite)

## Установка и запуск

### Локальное развертывание

Для локального развертывания проекта без использования Docker выполните следующие шаги:

1. **Клонируйте репозиторий**:

    ```bash
    git clone git@github.com:Elithabeth2003/foodgram.git
    cd foodgram
    ```

2. **Установите зависимости для бэкенда**:

    Убедитесь, что у вас установлен [Python](https://www.python.org/) и [pip](https://pip.pypa.io/en/stable/).

    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Unix/MacOS
    venv\Scripts\activate  # Для Windows
    cd backend
    pip install -r requirements.txt
    ```

3. **Настройте базу данных**:

    Создайте файл `.env` в корне проекта и добавьте необходимые переменные окружения, например:

    ```ini
    DJANGO_DB_NAME=your_db_name
    DJANGO_DB_USER=your_db_user
    DJANGO_DB_PASSWORD=your_db_password
    DJANGO_DB_HOST=localhost
    DJANGO_DB_PORT=5432
    ```

4. **Примените миграции и создайте суперпользователя**:

    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```
5. **Заполните базу данных**:

    ```bash
    python manage.py import_ingredients
    python manage.py import_tags
    ```
6. **Запустите сервер разработки**:

    ```bash
    python manage.py runserver
    ```

На сайт можно посмотреть вот здесь - [FOODGRAM](https://cooker.sytes.net/recipes).
Здесь можно ознакомится с документацией - [DOCKS](https://cooker.sytes.net/api/docks).
