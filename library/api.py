from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Max, Min
from django.http import HttpResponse
import io
from django.contrib.auth.models import User
from openpyxl import Workbook
from docx import Document
from rest_framework import serializers
from .models import Library, Book, Genre, Member, Loan, UserProfile
from .serializers import (
    LibrarySerializer, BookSerializer, GenreSerializer,
    MemberSerializer, LoanSerializer, UserSerializer
)


class BaseExportMixin:
    """Mixin для экспорта queryset в Excel или Word"""
    def export_queryset(self, queryset, columns, filename_base):
        file_type = self.request.query_params.get('type', 'excel')

        if file_type == 'excel':
            wb = Workbook()
            ws = wb.active
            ws.title = filename_base
            ws.append(columns)
            for row in queryset:
                ws.append([row.get(col, '') for col in columns])
            stream = io.BytesIO()
            wb.save(stream)
            stream.seek(0)
            response = HttpResponse(
                stream,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.xlsx"'
            return response

        elif file_type == 'word':
            doc = Document()
            doc.add_heading(filename_base, 0)
            for row in queryset:
                doc.add_paragraph(' | '.join(str(row.get(col, '')) for col in columns))
            stream = io.BytesIO()
            doc.save(stream)
            stream.seek(0)
            response = HttpResponse(
                stream,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.docx"'
            return response

        return Response({"error": "Unknown file type"}, status=400)


class GenreViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # ВСЕ пользователи видят все жанры
        return Genre.objects.all().order_by('name')

    def perform_create(self, serializer):
        # сохраняем автора только если это админ или нужно
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Статистика по жанрам:
        - Количество жанров
        - Самый популярный жанр (по количеству книг)
        """
        queryset = self.get_queryset()
        total_count = queryset.count()
        # Жанр с наибольшим количеством книг
        top_genre = Genre.objects.annotate(num_books=Count('book')).order_by('-num_books').first()
        top_name = top_genre.name if top_genre else None

        return Response({
            'count': total_count,
            'top': top_name
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        data = [{'ID': g.id, 'Name': g.name, 'User': g.user.username if g.user else ''} for g in queryset]
        return self.export_queryset(data, ['ID', 'Name', 'User'], 'Genres')



class LibraryViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = LibrarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Все видят библиотеки
        return Library.objects.all().order_by('name')

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can add libraries.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can edit libraries.")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can delete libraries.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        total_count = queryset.count()
        # Можно добавить популярную библиотеку по выдачам, если нужно
        return Response({'count': total_count})

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        data = [{'ID': l.id, 'Name': l.name, 'User': l.user.username if l.user else ''} for l in queryset]
        return self.export_queryset(data, ['ID', 'Name', 'User'], 'Libraries')


class BookViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Все видят все книги
        return Book.objects.all()

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can add books.")
        serializer.save()  # без user

    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can edit books.")
        serializer.save()  # без user

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can delete books.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        total_count = queryset.count()

        most_borrowed = (
            Loan.objects.values('book__id', 'book__title')
            .annotate(borrow_count=Count('id'))
            .order_by('-borrow_count')
            .first()
        )

        most_borrowed_book = {
            'id': most_borrowed['book__id'],
            'title': most_borrowed['book__title'],
            'borrow_count': most_borrowed['borrow_count']
        } if most_borrowed else None

        return Response({
            'count': total_count,
            'most_borrowed': most_borrowed_book
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        data = [{
            'ID': b.id,
            'Title': b.title,
            'Genre': b.genre.name if b.genre else '',
            'Library': b.library.name if b.library else ''
        } for b in queryset]  # убрали поле User
        return self.export_queryset(data, ['ID', 'Title', 'Genre', 'Library'], 'Books')




class LoanViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Админ видит все, обычный пользователь — только свои выдачи"""
        qs = Loan.objects.select_related('book', 'member', 'user')
        if self.request.user.is_superuser:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Любой пользователь создаёт выдачу для себя"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Только админ может редактировать"""
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can edit loans.")
        serializer.save()

    def perform_destroy(self, instance):
        """Только админ может удалять"""
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can delete loans.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика выдач"""
        qs = self.get_queryset()
        stats = qs.aggregate(
            count=Count('id'),
            # можно заменить id на book__id или другой числовой параметр
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id')
        )
        return Response(stats)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Экспорт выдач (только админ)"""
        if not request.user.is_superuser:
            return Response({"error": "Permission denied"}, status=403)

        queryset = self.get_queryset()
        data = [
            {
                'ID': l.id,
                'Book': l.book.title if l.book else '',
                'Member': l.member.first_name if l.member else '',
                'User': l.user.username if l.user else ''
            }
            for l in queryset
        ]
        return self.export_queryset(data, ['ID', 'Book', 'Member', 'User'], 'Loans')


# ViewSet для пользователей системы (Django User) - используется на /members/
class MemberViewSet(viewsets.ModelViewSet, BaseExportMixin):
    """
    ViewSet для управления пользователями системы (Django User).
    Используется на эндпоинте /members/ для авторизации в системе.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        """
        Создание нового пользователя с правильным хэшированием пароля
        """
        username = request.data.get('username')
        email = request.data.get('email', '')
        password = request.data.get('password')
        is_superuser = request.data.get('is_superuser', False)
        is_staff = request.data.get('is_staff', False)
        age = request.data.get('age')

        # Конвертируем строковые значения в boolean
        if isinstance(is_superuser, str):
            is_superuser = is_superuser.lower() in ('true', '1', 'yes')
        if isinstance(is_staff, str):
            is_staff = is_staff.lower() in ('true', '1', 'yes')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, существует ли пользователь
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'User with this username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Используем create_user для автоматического хэширования пароля
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.save()
        
        # Создаем/обновляем профиль с возрастом
        if age:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.age = int(age)
            profile.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Обновление пользователя с правильным хэшированием пароля
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Обновляем обычные поля
        if 'username' in request.data:
            instance.username = request.data['username']
        if 'email' in request.data:
            instance.email = request.data['email']
        
        # Обрабатываем булевы поля
        if 'is_superuser' in request.data:
            is_superuser = request.data['is_superuser']
            if isinstance(is_superuser, str):
                is_superuser = is_superuser.lower() in ('true', '1', 'yes')
            instance.is_superuser = is_superuser
            
        if 'is_staff' in request.data:
            is_staff = request.data['is_staff']
            if isinstance(is_staff, str):
                is_staff = is_staff.lower() in ('true', '1', 'yes')
            instance.is_staff = is_staff

        # Используем set_password для хэширования пароля
        if 'password' in request.data and request.data['password']:
            instance.set_password(request.data['password'])

        instance.save()
        
        # Обновляем возраст в профиле
        if 'age' in request.data:
            age = request.data['age']
            if age:
                profile, created = UserProfile.objects.get_or_create(user=instance)
                profile.age = int(age)
                profile.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()

        total_count = queryset.count()

        # Средний возраст
        profiles = UserProfile.objects.filter(user__in=queryset, age__isnull=False)
        if profiles.exists():
            ages = [p.age for p in profiles if p.age]
            avg_age = round(sum(ages) / len(ages), 1)
        else:
            avg_age = 0

        # Среднее количество взятых книг
        loans_count = Loan.objects.filter(member__user__in=queryset).count()
        avg_books = round(loans_count / total_count, 1) if total_count else 0

        return Response({
            'count': total_count,
            'avg_age': avg_age,
            'avg_books': avg_books
        })

    @action(detail=False, methods=['get'], url_path='export/excel')
    def export_excel(self, request):
        queryset = self.get_queryset()
        data = [
            {
                'ID': u.id,
                'Username': u.username,
                'Email': u.email,
                'Is Superuser': 'Yes' if u.is_superuser else 'No',
                'Is Staff': 'Yes' if u.is_staff else 'No'
            }
            for u in queryset
        ]
        return self.export_queryset(data, ['ID', 'Username', 'Email', 'Is Superuser', 'Is Staff'], 'Members')

    @action(detail=False, methods=['get'], url_path='export/word')
    def export_word(self, request):
        queryset = self.get_queryset()
        data = [
            {
                'ID': u.id,
                'Username': u.username,
                'Email': u.email,
                'Is Superuser': 'Yes' if u.is_superuser else 'No',
                'Is Staff': 'Yes' if u.is_staff else 'No'
            }
            for u in queryset
        ]
        # Создаем копию request.query_params и меняем тип
        from django.http import QueryDict
        query_dict = request.GET.copy()
        query_dict['type'] = 'word'
        request.GET = query_dict
        return self.export_queryset(data, ['ID', 'Username', 'Email', 'Is Superuser', 'Is Staff'], 'Members')
    
