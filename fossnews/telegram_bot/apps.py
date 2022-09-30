from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TelegramBotConfig(AppConfig):
    name = 'fossnews.telegram_bot'
    verbose_name = _('Telegram bot')
