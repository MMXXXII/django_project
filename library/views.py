from django.views.generic import TemplateView
from typing import Any
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from django.core.cache import cache
import time
from rest_framework.permissions import BasePermission
from library.models import Library
from rest_framework import serializers, status
from django.contrib.auth import logout as django_logout
import random
import string
from library.models import UserProfile, Library


# Create your views here.
class ShowLibraryView(TemplateView):
    template_name = "library/show_library.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['library'] = Library.objects.all()
        return context

class OTPRequired(BasePermission):
    def has_permission(self, request, view):
        otp_good = cache.get(f'otp_good_{request.user.id}', False)
        if not otp_good:
            return False
        otp_timestamp = cache.get(f'otp_timestamp_{request.user.id}', 0)
        if otp_timestamp and (time.time() - otp_timestamp > 600):
            cache.set(f'otp_good_{request.user.id}', False)
            return False
        return True

class UserProfileViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    class LoginSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField()

    class OTPSerializer(serializers.Serializer):
        key = serializers.CharField()
        username = serializers.CharField()

    class UserProfileSerializer(serializers.ModelSerializer):
        username = serializers.CharField(source='user.username', read_only=True)
        email = serializers.CharField(source='user.email', read_only=True)
        first_name = serializers.CharField(source='user.first_name', read_only=True)
        last_name = serializers.CharField(source='user.last_name', read_only=True)
        is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)

        class Meta:
            model = UserProfile
            fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'age']

    def list(self, request):
        profiles = UserProfile.objects.select_related('user').all()
        serializer = self.UserProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            profile = UserProfile.objects.select_related('user').get(pk=pk)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.UserProfileSerializer(profile)
        return Response(serializer.data)

    @action(detail=False, url_path="check-login", methods=['GET'], permission_classes=[])
    def get_check_login(self, request):
        return Response({'is_authenticated': request.user.is_authenticated})

    @action(detail=False, url_path="login", methods=['POST'], permission_classes=[], serializer_class=LoginSerializer)
    def use_login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            otp_code = ''.join(random.choices(string.digits, k=6))
            cache.set(f'otp_pending_{user.username}', {
                'otp_code': otp_code,
                'timestamp': time.time(),
                'password': serializer.validated_data['password']
            }, 300)
            print(f'[v0] OTP код для {user.username}: {otp_code}')
            return Response({
                'is_authenticated': False,
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser,
                'otp_sent': True
            })
        return Response({'is_authenticated': False, 'error': 'Неверные учетные данные'}, status=400)

    @action(detail=False, url_path='otp-login', methods=['POST'], serializer_class=OTPSerializer, permission_classes=[])
    def otp_login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        otp_code = serializer.validated_data['key']
        pending_data = cache.get(f'otp_pending_{username}')
        if not pending_data:
            return Response({'success': False, 'error': 'OTP истек или не найден'}, status=400)
        if pending_data['otp_code'] != otp_code:
            return Response({'success': False, 'error': 'Неверный OTP код'}, status=400)
        if time.time() - pending_data['timestamp'] > 300:
            cache.delete(f'otp_pending_{username}')
            return Response({'success': False, 'error': 'OTP истек'}, status=400)
        user = authenticate(username=username, password=pending_data['password'])
        if user:
            login(request, user)
            cache.set(f'otp_good_{user.id}', True, 600)
            cache.delete(f'otp_pending_{username}')
            return Response({'success': True, 'is_authenticated': True, 'is_superuser': user.is_superuser})
        return Response({'success': False, 'error': 'Ошибка аутентификации'}, status=400)

    @action(detail=False, url_path='otp-status', permission_classes=[IsAuthenticated])
    def get_otp_status(self, request):
        otp_good = cache.get(f'otp_good_{request.user.id}', False)
        return Response({'otp_good': otp_good})

    @action(detail=False, url_path='info', permission_classes=[IsAuthenticated])
    def get_user_info(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_superuser': user.is_superuser
        })

    @action(detail=False, url_path='otp-required', permission_classes=[OTPRequired])
    def page_with_otp_required(self, request):
        return Response({'success': True})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='logout')
    def logout(self, request):
        django_logout(request)
        cache.set(f'otp_good_{request.user.id}', False)
        return Response({'success': True})