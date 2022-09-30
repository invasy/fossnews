from django.contrib import admin
from django.db.models import F

from .models import *


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('enabled', 'title', 'url', 'type', 'language')
    list_display_links = ('title',)
    list_editable = ('enabled', 'url', 'type', 'language')
    actions = ['enable', 'disable', 'toggle']

    @admin.action(description='Enable selected sources')
    def enable(self, request, queryset):
        queryset.update(active=True)

    @admin.action(description='Disable selected sources')
    def disable(self, request, queryset):
        queryset.update(active=False)

    @admin.action(description='Toggle selected sources')
    def toggle(self, request, queryset):
        queryset.update(active=not F('enabled'))


@admin.register(GatheringResult)
class GatheringResultAdmin(admin.ModelAdmin):
    list_display = ('started_at', 'finished_at', 'source', 'total_count', 'saved_count', 'filtered_count', 'errors_count')
    list_display_links = ('started_at', 'finished_at', 'source')
    fields = (
        ('started_at', 'finished_at'),
        'source',
        ('total_count', 'saved_count', 'filtered_count', 'errors_count'),
        'errors',
        'news',
    )
    readonly_fields = (
        'source', 'started_at', 'finished_at',
        'total_count', 'saved_count', 'filtered_count', 'errors_count',
        'errors', 'news',
    )
    date_hierarchy = 'finished_at'

    @admin.display(description='News')
    def news(self, model) -> str:
        return ',\n'.join(f'{n.title} ({n.url})' for n in model.news_set.all())


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'url', 'published_at', 'gathered_at', 'source')
    list_display_links = ('title',)
    date_hierarchy = 'gathered_at'

    @admin.display(description='Source')
    def source(self, model) -> Source:
        return model.gathering.source


@admin.register(DigestIssue)
class DigestIssueAdmin(admin.ModelAdmin):
    list_display = ('number', 'is_special', 'status', 'planned_at', 'published_at')
    list_display_links = ('number',)
    list_editable = ('is_special', 'status', 'planned_at', 'published_at')
    date_hierarchy = 'published_at'


@admin.register(DigestIssueLink)
class DigestIssueLinkAdmin(admin.ModelAdmin):
    list_display = ('issue', 'type', 'url')
    list_display_links = ('issue',)
    list_editable = ('type', 'url')
