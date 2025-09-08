from django.contrib import admin
from .models import Library, Book, Category, Reader, Loan

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "address"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "author", "library"]
    list_filter = ["library", "categories"]
    search_fields = ["name", "author"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "email"]


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["id", "book", "reader", "date_borrowed", "date_returned"]
    list_filter = ["date_borrowed", "date_returned"]
