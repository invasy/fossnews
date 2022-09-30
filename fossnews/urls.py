from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('preferences/', include('dynamic_preferences.urls', namespace='preferences')),
    path('gatherer/', include('fossnews.gatherer.urls', namespace='gatherer')),
    # path('classifier/', include('fossnews.classifier.urls', namespace='classifier')),
    # path('bot/', include('fossnews.telegram_bot.urls', namespace='telegram-bot')),
]
