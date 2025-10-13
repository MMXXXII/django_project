from django.db import models

# Create your models here.
class Genre(models.Model):
    name = models.TextField("Жанр")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self) -> str:
        return self.name


class Library(models.Model):
    name = models.TextField("Название библиотеки")
    address = models.TextField("Адрес")

    class Meta:
        verbose_name = "Библиотека"
        verbose_name_plural = "Библиотеки"

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.TextField("Название книги")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="Жанр")
    library = models.ForeignKey(Library, on_delete=models.CASCADE, verbose_name="Библиотека")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self) -> str:
        return self.title


class Member(models.Model):
    first_name = models.TextField("Имя")
    library = models.ForeignKey(Library, on_delete=models.CASCADE, verbose_name="Библиотека")

    class Meta:
        verbose_name = "Читатель"
        verbose_name_plural = "Читатели"

    def __str__(self) -> str:
        return self.first_name


class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="Читатель")
    loan_date = models.DateField("Дата выдачи")

    class Meta:
        verbose_name = "Выдача книги"
        verbose_name_plural = "Выдачи книг"

    def __str__(self) -> str:
        return f"{self.book} → {self.member}"
