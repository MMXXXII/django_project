from rest_framework import serializers

from library.models import Library, Book, Genre, Member, Loan

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = "__all__"

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    library = serializers.PrimaryKeyRelatedField(queryset=Library.objects.all())
    genre = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all())


        
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"