from django.db import models
from django.utils.translation import get_language_info, gettext_lazy as _


__all__ = (
    'Source',
    'GatheringResult',
    'News',
    'DigestIssue',
    'DigestIssueLink',
)


class Language(models.TextChoices):
    EN = 'en', get_language_info('en')['name_translated']
    RU = 'ru', get_language_info('ru')['name_translated']


class SourceType(models.TextChoices):
    RSS = 'rss', _('RSS')
    HTML = 'html', _('HTML')
    YOUTUBE = 'youtube', _('YouTube')


class Source(models.Model):
    enabled = models.BooleanField(default=True)
    title = models.CharField(max_length=32, unique=True)
    url = models.URLField(unique=True)
    type = models.CharField(max_length=8, choices=SourceType.choices, default=SourceType.RSS)
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.EN)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('source')
        verbose_name_plural = _('sources')
        ordering = ['enabled', 'title']
        indexes = [
            models.Index(fields=('title',)),
        ]


class GatheringResult(models.Model):
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(blank=True, null=True)
    source = models.ForeignKey('Source', null=True, on_delete=models.SET_NULL)
    total_count = models.IntegerField(default=0)
    saved_count = models.IntegerField(default=0)
    filtered_count = models.IntegerField(default=0)
    errors_count = models.IntegerField(default=0)
    errors = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Gathering from {self.source.title} at {self.finished_at}'

    def to_dict(self) -> dict:
        return dict(
            source=self.source.title,
            started_at=self.started_at,
            finished_at=self.finished_at,
            total_count=self.total_count,
            saved_count=self.saved_count,
            filtered_count=self.filtered_count,
            errors_count=self.errors_count,
        )

    class Meta:
        ordering = ['-finished_at', 'source__title']


class ContentType(models.TextChoices):
    ARTICLE = 'article', _('article')
    NEWS = 'news', _('news')
    RELEASE = 'release', _('release')
    VIDEO = 'video', _('video')
    OTHER = 'other', _('other')
    UNKNOWN = 'unknown', _('unknown')


class News(models.Model):
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=256, blank=True, null=True)
    url = models.URLField()
    origin = models.URLField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=8, choices=ContentType.choices, default=ContentType.UNKNOWN)
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.EN)
    published_at = models.DateTimeField()
    gathered_at = models.DateTimeField()
    gathering = models.ForeignKey('gatherer.GatheringResult', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.title} ({self.url})'

    class Meta:
        verbose_name = _('news')
        verbose_name_plural = _('news')
        ordering = ['-gathered_at', 'title']
        indexes = [
            models.Index(fields=('title',)),
            models.Index(fields=('url',)),
        ]


class DigestStatus(models.TextChoices):
    PLANNING = 'planning', _('planning')
    GATHERING = 'gathering', _('gathering')
    EDITING = 'editing', _('editing')
    PUBLISHED = 'published', _('published')


class DigestIssue(models.Model):
    number = models.IntegerField(help_text='Digest issue number.')
    is_special = models.BooleanField(help_text='Is this digest issue special?')
    status = models.CharField(max_length=16, choices=DigestStatus.choices, default=DigestStatus.PLANNING)
    planned_at = models.DateField(help_text='Date this digest issue is planned to be published at.')
    published_at = models.DateField(blank=True, null=True, help_text='Date this digest issue was actually published at.')

    def __str__(self):
        s = f'Digest issue #{self.number}'
        if self.published_at:
            s += f' ({self.published_at})'
        return s

    class Meta:
        verbose_name = _('digest issue')
        verbose_name_plural = _('digest issues')
        ordering = ['-number']
        indexes = [
            models.Index(fields=('number',)),
        ]


class DigestIssueLinkType(models.TextChoices):
    HABR = 'habr'
    FACEBOOK = 'facebook'
    VK = 'vk'


class DigestIssueLink(models.Model):
    issue = models.ForeignKey('DigestIssue', on_delete=models.CASCADE)
    type = models.CharField(max_length=16, choices=DigestIssueLinkType.choices, default=DigestIssueLinkType.HABR)
    url = models.URLField()

    def __str__(self):
        return f'Digest issue #{self.issue.number} {self.type} link'

    class Meta:
        verbose_name = _('digest link')
        verbose_name_plural = _('digest links')
        ordering = ['-issue__number', 'type']
