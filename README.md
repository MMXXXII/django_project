# 📚 Django Library Management System / Система управления библиотекой на Django

Учебный проект на Django и Vue.js для управления библиотеками, книгами, читателями и выдачами.  
Включает REST API и SPA фронтенд.

Educational project using Django and Vue.js for managing libraries, books, members, and loans.  
Includes REST API and SPA frontend.

---

## 🌟 Особенности / Features

- Управление библиотеками / Manage libraries  
- CRUD операций с книгами / CRUD operations for books  
- Жанры книг / Book genres  
- Читатели (Members) / Library members  
- Выдачи книг (Loans) и возвраты / Book loans and returns  
- REST API через Django REST Framework / REST API via Django REST Framework  
- SPA интерфейс на Vue.js / SPA frontend with Vue.js  
- Генератор тестовых данных Faker / Faker-based test data generator  

---

## 🧱 Стек технологий / Tech Stack

**Backend / Сервер:**

- Python 3.x  
- Django  
- Django REST Framework  
- SQLite (по умолчанию) / SQLite (default)  
- Faker (генерация тестовых данных) / Faker (test data generation)

**Frontend / Клиент:**

- Vue.js + JavaScript  
- Axios для работы с API / Axios for API requests  

---

## 🚀 Установка и запуск / Installation and Run

### 1. Клонировать репозиторий / Clone repository

```bash
git clone https://github.com/MMXXXII/django_project.git
cd django_project

python -m venv .venv

.venv\Scripts\activate

2. Создать и активировать виртуальное окружение / Create and activate virtual environment
python -m venv .venv


Windows:

.venv\Scripts\activate


Linux/macOS:

source .venv/bin/activate

3. Установить зависимости / Install dependencies
pip install -r requirements.txt


Если есть фронтенд-зависимости:

cd client
npm install

4. Выполнить миграции / Run migrations
python manage.py migrate

5. (Опционально) Сгенерировать тестовые данные / (Optional) Generate test data
python manage.py generate_data

6. Запустить backend / Run backend
python manage.py runserver


Доступно по: http://localhost:8000

7. Запустить фронтенд / Run frontend
cd client
npm run dev


SPA доступно по: http://localhost:8080
