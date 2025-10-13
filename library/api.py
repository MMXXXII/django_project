from library.models import Library, Book, Genre, Loan, Member

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from library.serializers import LibrarySerializer, BookSerializer, GenreSerializer, MemberSerializer, LoanSerializer

from library.models import Library, Book, Genre, Loan, Member

class LibraryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class BookViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class MemberViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class LoanViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer