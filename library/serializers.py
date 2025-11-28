from rest_framework import serializers
from library.models import Library, Book, Genre, Member, Loan, UserProfile
from django.contrib.auth.models import User

class BookSerializer(serializers.ModelSerializer):
    genre_name = serializers.StringRelatedField(source='genre', read_only=True)
    library_name = serializers.StringRelatedField(source='library', read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'genre', 'library', 'genre_name', 'library_name', 'cover', 'cover_url']
        read_only_fields = ['user']

    def get_cover_url(self, obj):
        if obj.cover:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover.url) if request else obj.cover.url
        return None


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class MemberSerializer(serializers.ModelSerializer):
    library = serializers.PrimaryKeyRelatedField(queryset=Library.objects.all())
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'first_name', 'library', 'photo', 'photo_url', 'user']
        read_only_fields = ['user']

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        photo = validated_data.pop('photo', None)
        if photo:
            instance.photo = photo
        return super().update(instance, validated_data)


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'book', 'member', 'loan_date']  # user убрали из полей
        read_only_fields = []  # все поля можно отправлять кроме user, который подставляется автоматически

    def create(self, validated_data):
        # Автоматически подставляем пользователя из request
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Обновление доступно только админам (логика в ViewSet)
        return super().update(instance, validated_data)


class OTPSerializer(serializers.Serializer):
    key = serializers.CharField()


# Сериализатор для пользователей системы (User) с полем возраста
class UserSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(source='profile.age', required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'age']
        read_only_fields = ['id']
    
    def update(self, instance, validated_data):
        # Извлекаем данные профиля
        profile_data = validated_data.pop('profile', {})
        age = profile_data.get('age')
        
        # Обновляем пользователя
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Обновляем возраст в профиле
        if age is not None:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            profile.age = age
            profile.save()
        
        return instance