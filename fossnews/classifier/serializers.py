from rest_framework.serializers import ModelSerializer

from .models import *


__all__ = ('ClassificationAttemptSerializer',)


class ClassificationAttemptSerializer(ModelSerializer):
    class Meta:
        model = ClassificationAttempt
        fields = '__all__'
