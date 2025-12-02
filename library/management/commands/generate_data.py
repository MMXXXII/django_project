# library/management/commands/generate_data.py

from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import timedelta
from library.models import Library, Book, Genre, Member, Loan


class Command(BaseCommand):
    help = "Генерирует реалистичные тестовые данные для библиотек Иркутска"

    def handle(self, *args, **options):
        fake = Faker("ru_RU")

        # ------------------------------
        # 1. Жанры
        # ------------------------------
        genre_map = {
            "Русская классика": [
                "Преступление и наказание",
                "Мастер и Маргарита",
                "Война и мир",
                "Анна Каренина",
                "Идиот",
                "Обломов",
                "Отцы и дети",
                "Евгений Онегин",
                "Герой нашего времени",
                "Доктор Живаго",
                "Белая гвардия",
                "Собачье сердце",
                "Мёртвые души",
            ],
            "Фантастика": [
                "Пикник на обочине",
                "Трудно быть богом",
                "Мы",
                "1984",
                "Человек-амфибия",
            ],
            "Приключения": [
                "Три мушкетёра",
                "Граф Монте-Кристо",
                "Золотой телёнок",
                "Двенадцать стульев",
            ],
        }

        for name in genre_map.keys():
            Genre.objects.get_or_create(name=name)
        genres = list(Genre.objects.all())

        # ------------------------------
        # 2. Библиотеки Иркутска
        # ------------------------------
        libraries_data = [
            ("ИОГУНБ им. Молчанова-Сибирского", "ул. Лермонтова, 253"),
            ("ЦГБ им. Потаниной", "ул. Урицкого, 32"),
            ("Детская библиотека им. Маршака", "ул. Ленина, 23"),
            ("Библиотека им. Чехова", "ул. Рабочего Штаба, 10"),
            ("Библиотека №4 им. Некрасова", "ул. Красногвардейская, 18"),
        ]

        for name, address in libraries_data:
            Library.objects.get_or_create(name=name, address=address)

        libraries = list(Library.objects.all())
        self.stdout.write(self.style.SUCCESS("📚 Библиотеки готовы."))

        # ------------------------------
        # 3. Книги
        # ------------------------------
        if Book.objects.count() < 800:
            for genre_name, titles in genre_map.items():
                genre = Genre.objects.get(name=genre_name)
                for library in libraries:
                    for _ in range(random.randint(10, 25)):
                        Book.objects.create(
                            title=random.choice(titles),
                            genre=genre,
                            library=library,
                        )

            self.stdout.write(self.style.SUCCESS("📘 Книги созданы."))

        books = list(Book.objects.all())

        # ------------------------------
        # 4. Читатели
        # ------------------------------
        if Member.objects.count() < 200:
            for _ in range(200):
                Member.objects.create(
                    first_name=fake.name(),
                    library=random.choice(libraries),
                )

        members = list(Member.objects.all())
        self.stdout.write(self.style.SUCCESS("🧍 Читатели готовы."))

        # ------------------------------
        # 5. Реалистичные выдачи
        # ------------------------------
        if Loan.objects.count() < 1000:
            for _ in range(1000):

                library = random.choice(libraries)
                library_books = [b for b in books if b.library == library]
                library_members = [m for m in members if m.library == library]

                if not library_books or not library_members:
                    continue

                book = random.choice(library_books)
                member = random.choice(library_members)

                loan_date = fake.date_between(start_date="-2y", end_date="today")

                return_date = None
                if random.random() < 0.4:
                    return_date = loan_date + timedelta(days=random.randint(3, 60))

                Loan.objects.create(
                    book=book,
                    member=member,
                    loan_date=loan_date,
                    return_date=return_date,
                )

        self.stdout.write(self.style.SUCCESS("🎉 Выдачи созданы!"))
        self.stdout.write(self.style.SUCCESS("✨ ГЕНЕРАЦИЯ УСПЕШНА"))
