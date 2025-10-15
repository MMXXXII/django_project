# library/management/commands/generate_data.py

from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import timedelta, date
from django.contrib.auth.models import User
from library.models import Library, Book, Genre, Member, Loan


class Command(BaseCommand):
    help = "Генерирует реалистичные тестовые данные для библиотек Иркутска"

    def handle(self, *args, **options):
        fake = Faker('ru_RU')

        # 1️⃣ Пользователи
        if User.objects.count() < 5:
            for i in range(1, 6):
                username = f"user{i}"
                User.objects.create_user(username=username, password="12345")
            self.stdout.write(self.style.SUCCESS("✅ Созданы тестовые пользователи."))
        users = list(User.objects.all())

        # 2️⃣ Жанры
        genre_names = [
            "Фантастика", "Детектив", "Роман", "Поэзия", "Фэнтези",
            "История", "Биография", "Научная литература", "Приключения", "Драма"
        ]
        for name in genre_names:
            Genre.objects.get_or_create(name=name)
        genres = list(Genre.objects.all())

        # 3️⃣ Реальные библиотеки Иркутска
        library_data = [
            ("Иркутская областная государственная универсальная научная библиотека им. И. И. Молчанова-Сибирского", "ул. Лермонтова, 253"),
            ("Центральная городская библиотека им. А. В. Потаниной", "ул. Урицкого, 32"),
            ("Детская библиотека имени Маршака", "ул. Ленина, 23"),
            ("Библиотека имени Чехова", "ул. Рабочего Штаба, 10"),
            ("Библиотека № 4 им. Некрасова", "ул. Красногвардейская, 18")
        ]
        for name, address in library_data:
            Library.objects.get_or_create(name=name, address=address)
        libraries = list(Library.objects.all())

        # 4️⃣ Реальные книги (примерный список)
        book_titles = [
            "Преступление и наказание", "Мастер и Маргарита", "Война и мир", "Анна Каренина",
            "Идиот", "Обломов", "Отцы и дети", "Евгений Онегин", "Герой нашего времени",
            "Три мушкетёра", "Граф Монте-Кристо", "1984", "Улисс", "Пикник на обочине",
            "Трудно быть богом", "Мы", "Белая гвардия", "Собачье сердце", "Доктор Живаго",
            "Золотой телёнок", "Двенадцать стульев", "Мёртвые души", "Человек-амфибия"
        ]

        # 1000 книг с повторениями
        if Book.objects.count() < 1000:
            for _ in range(1000):
                Book.objects.create(
                    title=random.choice(book_titles),
                    genre=random.choice(genres),
                    library=random.choice(libraries),
                    user=random.choice(users),
                )
            self.stdout.write(self.style.SUCCESS("✅ Сгенерированы книги."))

        books = list(Book.objects.all())

        # 5️⃣ Читатели с настоящими ФИО
        if Member.objects.count() < 300:
            for _ in range(300):
                full_name = fake.name()
                Member.objects.create(
                    first_name=full_name,
                    library=random.choice(libraries),
                )
            self.stdout.write(self.style.SUCCESS("✅ Сгенерированы читатели."))

        members = list(Member.objects.all())

        # 6️⃣ Выдачи книг
        if Loan.objects.count() < 1000:
            for _ in range(1000):
                loan_date = fake.date_between(start_date='-2y', end_date='today')
                Loan.objects.create(
                    book=random.choice(books),
                    member=random.choice(members),
                    loan_date=loan_date
                )
            self.stdout.write(self.style.SUCCESS("✅ Сгенерированы выдачи книг."))

        self.stdout.write(self.style.SUCCESS("🎉 Данные успешно сгенерированы!"))
