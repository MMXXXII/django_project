from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Max, Min
from django.http import HttpResponse
import io
from openpyxl import Workbook
from docx import Document

from .models import Library, Book, Genre, Member, Loan
from .serializers import (
    LibrarySerializer, BookSerializer, GenreSerializer,
    MemberSerializer, LoanSerializer
)


class BaseExportMixin:
    """Миксин для экспорта Excel и Word"""

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
        if self.request.user.is_superuser:
            return Genre.objects.all()
        return Genre.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = self.get_queryset().aggregate(
            count=Count('id'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id')
        )
        return Response(stats)

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        data = [{'ID': g.id, 'Name': g.name, 'User': g.user.username if g.user else ''} for g in queryset]
        return self.export_queryset(data, ['ID', 'Name', 'User'], 'Genres')


class LibraryViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = LibrarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Library.objects.all()
        return Library.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = self.get_queryset().aggregate(
            count=Count('id'), avg=Avg('id'), max=Max('id'), min=Min('id')
        )
        return Response(stats)

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        data = [{'ID': l.id, 'Name': l.name, 'User': l.user.username if l.user else ''} for l in queryset]
        return self.export_queryset(data, ['ID', 'Name', 'User'], 'Libraries')


class BookViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Book.objects.all()
        return Book.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        data = []
        for b in queryset:
            data.append({
                'ID': b.id,
                'Title': b.title,
                'Genre': b.genre.name if b.genre else '',
                'Library': b.library.name if b.library else '',
                'User': b.user.username if b.user else ''
            })
        return self.export_queryset(data, ['ID', 'Title', 'Genre', 'Library', 'User'], 'Books')


class MemberViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Member.objects.all()
        return Member.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = self.get_queryset().aggregate(
            count=Count('id'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id')
        )
        return Response(stats)

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        data = [
            {
                'ID': m.id,
                'Name': m.first_name,  # <-- исправлено
                'User': m.user.username if m.user else ''
            }
            for m in queryset
        ]
        return self.export_queryset(data, ['ID', 'Name', 'User'], 'Members')


class LoanViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Loan.objects.all()
        return Loan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = self.get_queryset().aggregate(
            count=Count('id'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id')
        )
        return Response(stats)

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        data = [
            {
                'ID': l.id,
                'Book': l.book.title if l.book else '',
                'Member': l.member.first_name if l.member else '',  # <-- исправлено
                'User': l.user.username if l.user else ''
            }
            for l in queryset
        ]
        return self.export_queryset(data, ['ID', 'Book', 'Member', 'User'], 'Loans')

