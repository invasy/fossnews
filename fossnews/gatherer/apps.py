from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GathererConfig(AppConfig):
    name = 'fossnews.gatherer'
    verbose_name = _('Gatherer')
