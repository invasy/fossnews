from rest_framework.viewsets import ModelViewSet

from .models import *
from .serializers import *


__all__ = ('TelegramUserViewSet',)


class TelegramUserViewSet(ModelViewSet):
    permission_classes = []
    queryset = TelegramUser.objects.all().order_by('username')
    serializer_class = TelegramUserSerializer
