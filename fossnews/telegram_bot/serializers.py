from rest_framework.serializers import HyperlinkedModelSerializer

from .models import *


__all__ = ('TelegramUserSerializer',)


class TelegramUserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = TelegramUser
        fields = '__all__'
