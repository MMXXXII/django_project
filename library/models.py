from django.db import models

# Create your models here.

class Book(models.Model):
    name = models.TextField('Название')
    author = models.TextField('Автор')
    library = models.ForeignKey("Library", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self) -> str:
        return self.name
    


class Library (models.Model):
    name = models.TextField('Название библиотеки')
    address = models.TextField('Адрес')

    class Meta:
        verbose_name = "Библиотека"
        verbose_name_plural = "Библиотеки"

    def __str__(self) -> str:
        return self.name

