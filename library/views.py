
from django.views.generic import TemplateView
from typing import Any
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from .serializers import OTPSerializer
from .models import UserProfile
import pyotp
from django.core.cache import cache
import time
from rest_framework.permissions import BasePermission

from library.models import Library

# Create your views here.
class ShowLibraryView(TemplateView):
    template_name = "library/show_library.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['library'] = Library.objects.all()

        return context

class OTPRequired(BasePermission):
    def has_permission(self, request, view):
        otp_good = cache.get('otp_good', False)
        if not otp_good:
            return False
        
        # Проверка времени жизни OTP: если прошло больше 10 минут, сбрасываем состояние
        otp_timestamp = cache.get('otp_timestamp', 0)
        if otp_timestamp and (time.time() - otp_timestamp > 600):  # 600 секунд = 10 минут
            cache.set('otp_good', False)  # Сбрасываем состояние
            return False
        
        return True

class UserProfileViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["GET"], url_path="login")
    def use_login(self, request, *args, **kwargs):
        user = authenticate(username='username', password='pass')
        if user:
            login(request, user)
        return Response({
            'is_authenticated': bool(user)
        })

    @action(detail=False, methods=["POST"], url_path='otp-login', serializer_class=OTPSerializer)
    def otp_login(self, *args, **kwargs):
        totp = pyotp.TOTP(self.request.user.userprofile.opt_key)
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        success = False
        if totp.now() == serializer.validated_data['key']:
            cache.set('otp_good', True, 10)  # Сохраняем успешную аутентификацию
            cache.set('otp_timestamp', time.time(), 10)  # Время OTP
            success = True

        return Response({
            'success': success
        })

    @action(detail=False, methods=["GET"], url_path="otp-status")
    def get_otp_status(self, *args, **kwargs):
        otp_good = cache.get('otp_good', False)
        return Response({
            'otp_good': otp_good
        })

    @action(detail=False, methods=["GET"], url_path="update-object", permission_classes=[OTPRequired])
    def update_object(self, request, *args, **kwargs):
        # Логика для редактирования объектов
        return Response({
            'status': 'Объект успешно обновлен'
        })

