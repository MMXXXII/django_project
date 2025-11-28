from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Member, Library


@receiver(post_save, sender=User)
def ensure_member_profile(sender, instance, created, **kwargs):
    """
    Создаёт профиль читателя (Member) для каждого нового пользователя.
    Если библиотека по умолчанию существует — привязывает к ней.
    """
    if not created:
        return  # чтобы не дергать код при обновлении пользователя

    default_library = Library.objects.first()

    if default_library is None:
        # Можно логировать или просто выйти
        return

    # Проверяем, что Member ещё не существует (хотя при created обычно не существует)
    if not Member.objects.filter(user=instance).exists():
        Member.objects.create(
            user=instance,
            library=default_library,
            first_name=instance.first_name or instance.username,
            last_name=instance.last_name or ""
        )
