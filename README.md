# Where-to-sit
Meeting room booking service "Where to sit?"


# Где сидеть? (Where to Sit)

Система бронирования переговорных комнат с лимитами по времени и проверкой пересечений.

## О проекте

Проект решает задачу резервирования переговорных комнат сотрудниками компании. Система гарантирует, что:
*   Комната не будет забронирована дважды на одно и то же время.
*   Одно бронирование не превышает 3 часов.
*   Суммарное время бронирований одного пользователя в сутки не превышает 4 часов.
*   Нельзя забронировать комнату на время в прошлом.

## Стек технологий

*   **Backend:** Python, Django (>=4.2), Django REST Framework.
*   **Аутентификация:** TokenAuthentication (`rest_framework.authtoken`).
*   **Тестирование:** pytest, pytest-django.
*   **База данных:** SQLite (по умолчанию), поддержка PostgreSQL.
*   **ОС:** Кроссплатформенный (Windows/macOS/Linux).

## Структура проекта

```text
where_to_sit/
├── core/                 # Настройки Django (settings.py, urls.py и т.д.)
├── rooms/                # Приложение с логикой: модели, сериализаторы, views, admin
│   ├── models.py         # Room, Booking + валидация на уровне модели
│   ├── serializers.py    # RoomSerializer, BookingSerializer + бизнес-логика
│   ├── views.py          # API endpoints (List, Create, Delete)
│   ├── urls.py           # Роутинг API
│   └── admin.py          # Настройка админ-панели
├── tests/                # Тесты
│   └── test_booking_logic.py
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md

Быстрый старт (Windows PowerShell)

1. Создание и активация виртуального окружения

powershell
python -m venv myenv
myenv\Scripts\Activate.ps1
pip install --upgrade pip

2. Установка зависимостей

powershell

pip install -r requirements.txt

3. Инициализация проекта

powershell

# Создание проекта

django-admin startproject where_to_sit

# Создание приложения rooms

python manage.py startapp rooms

⚠️ Важно: Не забудь добавить 'rooms' и 'rest_framework', 'rest_framework.authtoken' в INSTALLED_APPS в файле where_to_sit/settings.py.

4. Миграции и суперпользователь

powershell

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

5. Запуск сервера

powershell

python manage.py runserver

Сервер будет доступен по адресу: http://127.0.0.1:8000.

Настройка аутентификации

Для работы API требуется токен пользователя.

Зайди в админку: http://127.0.0.1:8000/admin/.
Перейди в раздел Authentication and Authorization → Tokens.
Нажми Add Token, выбери пользователя и сохрани.
Скопируй полученный токен (строка из 40 символов).

В запросах к API используй заголовок: Authorization: Token <твой_токен>

Эндпоинты API

Метод	    URL	                Описание	          Авторизация

GET 	/api/rooms/	        Список всех комнат	      Требуется

GET	    /api/rooms/free/
        ?start=...&end=...	Свободные комнаты на                                                                                   интервал	                                     Требуется

POST	/api/bookings/	    Создать бронирование	  Требуется

GET	    /api/bookings/my/	Мои бронирования	      Требуется


DELETE	/api/bookings/<id>/	Отменить свое 
                            бронирование              Требуется

Получить список комнат:

powershell
\$token = "593413bcd18285ec49993a4b6c1f8881cabddb87" # Вставь свой токен
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/rooms/" -Headers @{ Authorization = "Token \$token" } | ConvertTo-Json -Depth 10

Создать бронирование:

powershell
\$body = @{
    room = 1
    start = "2023-10-27T14:00:00"
    end = "2023-10-27T15:00:00"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/bookings/" `
  -Method Post `
  -Headers @{ Authorization = "Token \$token" } `
  -ContentType "application/json" `
  -Body \$body

Тестирование
В проекте используются тесты на базе pytest.

Запуск всех тестов:

powershell
pytest

Запуск конкретного файла тестов:

powershell
pytest rooms/tests/test_booking_logic.py

Что покрыто тестами:

Проверка отклонения бронирования при пересечении времени.
Проверка отклонения бронирования, если длительность > 3 часов.
Проверка отклонения бронирования, если суммарное время пользователя за день > 4 часов.
Проверка отклонения бронирования в прошлом.

Работа с Django Admin

Админка доступна по адресу: http://127.0.0.1:8000/admin/.

Rooms: Управление комнатами (добавление, редактирование). Поле name уникально.
Bookings: Управление бронированиями. При сохранении срабатывает валидация модели (clean()), которая также проверяет время в будущем и длительность.
Tokens: Управление токенами доступа для пользователей.

Конфигурация окружения

requirements.txt

Django>=4.2
djangorestframework
pytest
pytest-django
psycopg2-binary

.gitignore

# Виртуальное окружение
myenv/
venv/
.venv/

# База данных (SQLite)
db.sqlite3

# Python кэши и байт-код
__pycache__/
*.pyc
*.pyo

# Медиа и собранная статика
media/
staticfiles/

# IDE
.idea/
.vscode/

# Временные файлы
*.swp
*.swo
.DS_Store

pytest.ini

[pytest]
DJANGO_SETTINGS_MODULE = where_to_sit.settings
python_files = tests.py test_*.py *_tests.py