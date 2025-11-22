from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Max, Min
from .models import Library, Book, Genre, Member, Loan
from .serializers import (
    LibrarySerializer, BookSerializer, GenreSerializer, 
    MemberSerializer, LoanSerializer
)


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Genre.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            count=Count('id'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id')
        )
        return Response(stats)


class LibraryViewSet(viewsets.ModelViewSet):
    serializer_class = LibrarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Library.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            count=Count('id'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id')
        )
        return Response(stats)


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            count=Count('id'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id')
        )
        return Response(stats)


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Member.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            count=Count('id'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id')
        )
        return Response(stats)


class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            count=Count('id'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id')
        )
        return Response(stats)
