from django.db import models

class Library(models.Model):
    name = models.TextField("Название библиотеки")
    address = models.TextField("Адрес")

    class Meta:
        verbose_name = "Библиотека"
        verbose_name_plural = "Библиотеки"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField("Название категории", max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.TextField("Название книги")
    author = models.TextField("Автор")
    library = models.ForeignKey(Library, on_delete=models.CASCADE, null=True, related_name="books")
    categories = models.ManyToManyField(Category, related_name="books", blank=True)

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.name


class Reader(models.Model):
    first_name = models.CharField("Имя", max_length=50)
    last_name = models.CharField("Фамилия", max_length=50)
    email = models.EmailField("Email", unique=True)

    class Meta:
        verbose_name = "Читатель"
        verbose_name_plural = "Читатели"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="loans")
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name="loans")
    date_borrowed = models.DateField("Дата выдачи")
    date_returned = models.DateField("Дата возврата", null=True, blank=True)

    class Meta:
        verbose_name = "Выдача"
        verbose_name_plural = "Выдачи"

    def __str__(self):
        return f"{self.book} → {self.reader}"
