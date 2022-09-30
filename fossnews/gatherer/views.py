from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .models import *
from .serializers import *


__all__ = (
    'SourceViewSet',
    'GatheringResultViewSet',
    'NewsViewSet',
    'DigestIssueViewSet',
    'DigestIssueLinkViewSet',
)


class SourceViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Source.objects.all().order_by('title')
    serializer_class = SourceSerializer


class GatheringResultViewSet(ModelViewSet):
    permission_classes = []
    queryset = GatheringResult.objects.all().order_by('-finished_at', 'source__title')
    serializer_class = GatheringResultSerializer


class NewsViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = News.objects.all().order_by('title')
    serializer_class = NewsSerializer


class DigestIssueViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = DigestIssue.objects.all().order_by('-number')
    serializer_class = DigestIssueSerializer


class DigestIssueLinkViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = DigestIssueLink.objects.all().order_by('-issue__number', 'type')
    serializer_class = DigestIssueLinkSerializer
