from django.conf import settings
from django.db import models

from ..core.models import Language


__all__ = ('TelegramUser',)


class TelegramUser(models.Model):
    """
    Telegram bot user.

    .. seealso::
        Telegram API
            User_

    .. _User: https://core.telegram.org/bots/api#user
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tg_id = models.PositiveBigIntegerField()
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    username = models.CharField(max_length=32, blank=True, null=True)
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.EN)
    is_premium = models.BooleanField(blank=True, null=True)
