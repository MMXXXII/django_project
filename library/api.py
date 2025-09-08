from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from library.models import Library
from library.serializers import LibrarySerializer


class LibraryViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer