from rest_framework import serializers 

from library.models import Library, Book

# class BookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Book
#         fields = 


class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ['id', 'name', 'address']