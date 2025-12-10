from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.http import HttpResponse
import io
from django.contrib.auth.models import User
from openpyxl import Workbook
from docx import Document
from library.models import Library, Book, Genre, Member, Loan, UserProfile
from library.serializers import (LibrarySerializer, BookSerializer, GenreSerializer,MemberSerializer, LoanSerializer, UserSerializer)


class BaseExportMixin:
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
        return Genre.objects.all().order_by('name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        total_count = queryset.count()
        top_genre = Genre.objects.annotate(num_books=Count('book')).order_by('-num_books').first()
        top_name = top_genre.name if top_genre else None

        return Response({
            'count': total_count,
            'top': top_name
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        
        if request.user.is_superuser:
            data = [{'ID': g.id, 'Name': g.name, 'User': g.user.username if g.user else ''} for g in queryset]
            columns = ['ID', 'Name', 'User']
        else:
            data = [{'ID': g.id, 'Name': g.name} for g in queryset]
            columns = ['ID', 'Name']
            
        return self.export_queryset(data, columns, 'Genres')


class LibraryViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = LibrarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
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
        top_library = Library.objects.annotate(num_loans=Count('book__loan')).order_by('-num_loans').first()

        top_name = top_library.name if top_library else None

        return Response({
            'count': total_count,
            'top': top_name
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        
        if request.user.is_superuser:
            data = [{'ID': l.id, 'Name': l.name, 'User': l.user.username if l.user else ''} for l in queryset]
            columns = ['ID', 'Name', 'User']
        else:
            data = [{'ID': l.id, 'Name': l.name} for l in queryset]
            columns = ['ID', 'Name']
            
        return self.export_queryset(data, columns, 'Libraries')


class BookViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Book.objects.all()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика по книгам"""
        queryset = self.get_queryset()
        total_count = queryset.count()

        most_borrowed = (
            Loan.objects.values('book__id', 'book__title')
            .annotate(borrow_count=Count('book'))
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
        """Экспорт книг - только для администраторов"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only administrators can export books"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        data = [
            {
                'ID': b.id,
                'Title': b.title,
                'Genre': b.genre.name if b.genre else '',
                'Library': b.library.name if b.library else '',
                'Status': 'Available' if b.is_available else 'Borrowed'
            }
            for b in queryset
        ]
        return self.export_queryset(data, ['ID', 'Title', 'Genre', 'Library', 'Status'], 'Books')


class LoanViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Loan.objects.select_related('book', 'member', 'user')
        if self.request.user.is_superuser:
            return qs
        
        return qs.filter(member__user=self.request.user)

    @action(detail=True, methods=['post'], url_path='return')
    def return_book(self, request, pk=None):
        """Возврат книги (установка return_date)"""
        loan = self.get_object()
        
        if loan.return_date:
            return Response(
                {'detail': 'Книга уже возвращена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from datetime import date
        loan.return_date = date.today()
        loan.save()
        
        self.update_loan_stats()

        serializer = self.get_serializer(loan)
        return Response({
            'detail': 'Книга успешно возвращена.',
            'loan': serializer.data
        })

    def update_loan_stats(self):
        top_reader = Loan.objects.filter(return_date__isnull=True).values('member__id', 'member__first_name').annotate(loan_count=Count('id')).order_by('-loan_count').first()

        top_reader_data = {
            'name': top_reader['member__first_name'] if top_reader else None,
            'loan_count': top_reader['loan_count'] if top_reader else 0
        }

        loan_count = Loan.objects.filter(return_date__isnull=False).count()

        return Response({
            'count': loan_count,
            'topReader': top_reader_data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()

        count = qs.count()

        top_reader = (
            qs.values('member__id', 'member__first_name')
            .annotate(loan_count=Count('id'))
            .order_by('-loan_count')
            .first()
        )
        
        top_reader_data = {
            'name': top_reader['member__first_name'] if top_reader else None,
            'loan_count': top_reader['loan_count'] if top_reader else 0
        }

        return Response({
            'count': count,
            'topReader': top_reader_data
        })

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
                'User': l.user.username if l.user else '',
                'Loan Date': l.loan_date,
                'Return Date': l.return_date if l.return_date else 'Not returned'
            }
            for l in queryset
        ]
        return self.export_queryset(data, ['ID', 'Book', 'Member', 'User', 'Loan Date', 'Return Date'], 'Loans')


class MemberViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email', '')
        password = request.data.get('password')
        is_superuser = request.data.get('is_superuser', False)
        is_staff = request.data.get('is_staff', False)
        age = request.data.get('age')

        if isinstance(is_superuser, str):
            is_superuser = is_superuser.lower() in ('true', '1', 'yes')
        if isinstance(is_staff, str):
            is_staff = is_staff.lower() in ('true', '1', 'yes')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'User with this username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.save()
        
        if age:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.age = int(age)
            profile.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if 'username' in request.data:
            instance.username = request.data['username']
        if 'email' in request.data:
            instance.email = request.data['email']
        
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

        if 'password' in request.data and request.data['password']:
            instance.set_password(request.data['password'])

        instance.save()
        
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
        queryset_users = self.get_queryset().filter(is_superuser=False)
        total_count_users = queryset_users.count()

        queryset_admins = self.get_queryset().filter(is_superuser=True)
        total_count_admins = queryset_admins.count()

        user_profiles = UserProfile.objects.filter(user__in=queryset_users, age__isnull=False)
        if user_profiles.exists():
            user_ages = [p.age for p in user_profiles if p.age]
            avg_age_users = round(sum(user_ages) / len(user_ages), 1)
        else:
            avg_age_users = 0

        admin_profiles = UserProfile.objects.filter(user__in=queryset_admins, age__isnull=False)
        if admin_profiles.exists():
            admin_ages = [p.age for p in admin_profiles if p.age]
            avg_age_admins = round(sum(admin_ages) / len(admin_ages), 1)
        else:
            avg_age_admins = 0

        loans_count = Loan.objects.filter(member__user__in=queryset_users).count()
        avg_books = round(loans_count / total_count_users, 1) if total_count_users else 0

        return Response({
            'count_users': total_count_users,
            'count_admins': total_count_admins,
            'avg_age_users': avg_age_users,
            'avg_age_admins': avg_age_admins,
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
        from django.http import QueryDict
        query_dict = request.GET.copy()
        query_dict['type'] = 'word'
        request.GET = query_dict
        return self.export_queryset(data, ['ID', 'Username', 'Email', 'Is Superuser', 'Is Staff'], 'Members')


class LibraryMemberViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Member.objects.all().select_related('user', 'library')
        
        if self.request.user.is_superuser:
            return queryset
        
        user_member = queryset.filter(user=self.request.user).first()
        
        if not user_member:
            from library.models import Library
            default_library = Library.objects.first()
            
            if default_library:
                user_member = Member.objects.create(
                    user=self.request.user,
                    first_name=self.request.user.username,
                    library=default_library
                )
        
        return queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can add library members.")
        serializer.save()
    
    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can edit library members.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can delete library members.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        
        if not request.user.is_superuser:
            data = [
                {
                    'ID': m.id,
                    'Library': m.library.name if m.library else '',
                    'User': '*****'
                }
                for m in queryset
            ]
            columns = ['ID', 'Library', 'User']
        else:
            data = [
                {
                    'ID': m.id,
                    'Name': m.first_name,
                    'Library': m.library.name if m.library else '',
                    'User': m.user.username if m.user else ''
                }
                for m in queryset
            ]
            columns = ['ID', 'Name', 'Library', 'User']
        
        return self.export_queryset(data, columns, 'LibraryMembers')