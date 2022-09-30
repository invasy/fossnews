from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..gatherer.models import ContentType


__all__ = ('NewsCategory', 'NewsTag', 'ClassificationAttempt', 'Classification')


class NewsStatus(models.TextChoices):
    IN_DIGEST = 'in_digest'
    OUTDATED = 'outdated'
    DUPLICATE = 'duplicate'
    IGNORED = 'ignored'
    FILTERED = 'filtered'
    SKIPPED = 'skipped'


class NewsCategory(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']


class NewsTag(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['name']


class ClassificationAttempt(models.Model):
    classified_at = models.DateTimeField()
    news = models.ForeignKey('gatherer.News', on_delete=models.CASCADE)
    classificator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=NewsStatus.choices, blank=True, null=True)
    front_page = models.BooleanField(blank=True, null=True)
    category = models.ForeignKey('NewsCategory', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-classified_at', 'news__title']


class Classification(models.Model):
    news = models.OneToOneField('gatherer.News', on_delete=models.CASCADE)
    digest_issue = models.ForeignKey('core.DigestIssue', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=NewsStatus.choices, blank=True, null=True)
    front_page = models.BooleanField(blank=True, null=True)
    content_type = models.CharField(max_length=8, choices=ContentType.choices, default=ContentType.ARTICLE)
    category = models.ForeignKey('NewsCategory', blank=True, null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField('NewsTag')

    class Meta:
        ordering = ['digest_issue__number', 'status', 'news__title']
