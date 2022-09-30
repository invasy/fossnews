from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClassifierConfig(AppConfig):
    name = 'fossnews.classifier'
    verbose_name = _('Classifier')
