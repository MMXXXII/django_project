from rest_framework.viewsets import GenericViewSet
from library.models import Library

class LibraryViewSet(GenericViewSet):
    queryset = Library.objects.all()