from django.shortcuts import render
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .models import *
from .serializers import *


__all__ = ('ClassificationAttemptViewSet',)


class ClassificationAttemptViewSet(ModelViewSet):
    permission_classes = []
    queryset = ClassificationAttempt.objects.all().order_by('-classified_at')
    serializer_class = ClassificationAttemptSerializer
