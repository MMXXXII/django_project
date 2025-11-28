from django.contrib import admin
from library.models import Library, Genre, Book, Member, Loan

# Register your models here.
@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "address"]

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "genre", "library"]

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "library"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Проверка, что пользователь является суперпользователем
        if request.user.is_superuser:
            return queryset  # Суперпользователь видит всех читалетей
        return queryset.none()  # Обычные пользователи не видят читалетей

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["id", "book", "member", "loan_date"]
