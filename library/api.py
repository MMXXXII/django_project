from library.models import Library, Book, Genre, Loan, Member
from rest_framework import serializers
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from library.serializers import LibrarySerializer, BookSerializer, GenreSerializer, MemberSerializer, LoanSerializer
from rest_framework import filters
from django.db.models import Count, Avg, Max, Min



class StatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    avg = serializers.FloatField()
    max = serializers.IntegerField()
    min = serializers.IntegerField()

class LibraryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Library.objects.aggregate(
            count=Count("id"),
            avg=Avg("id"),
            max=Max("id"),
            min=Min("id")
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)
    


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        # Агрегируем статистику по жанрам, считая количество книг в каждом жанре
        stats = Genre.objects.aggregate(
            count=Count("id"),
            avg=Avg("id"),
            max=Max("id"),
            min=Min("id")
        )
        
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)



class BookViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username']

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Book.objects.aggregate(
            count=Count("id"),
            avg=Avg("id"),
            max=Max("id"),
            min=Min("id")
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)

class MemberViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Member.objects.aggregate(
            count=Count("id"),
            avg=Avg("id"),
            max=Max("id"),
            min=Min("id")
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class LoanViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Loan.objects.aggregate(
            count=Count("id"),
            avg=Avg("id"),
            max=Max("id"),
            min=Min("id")
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)
