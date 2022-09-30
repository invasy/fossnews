from rest_framework.serializers import ModelSerializer

from .models import *


__all__ = (
    'SourceSerializer',
    'GatheringResultSerializer',
    'NewsSerializer',
    'DigestIssueSerializer',
    'DigestIssueLinkSerializer',
)


class SourceSerializer(ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class GatheringResultSerializer(ModelSerializer):
    class Meta:
        model = GatheringResult
        fields = '__all__'


class NewsSerializer(ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'


class DigestIssueSerializer(ModelSerializer):
    class Meta:
        model = DigestIssue
        fields = '__all__'


class DigestIssueLinkSerializer(ModelSerializer):
    class Meta:
        model = DigestIssueLink
        fields = '__all__'
