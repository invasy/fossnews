from django.contrib import admin

from .models import *


admin.site.register(NewsCategory)
admin.site.register(NewsTag)
admin.site.register(ClassificationAttempt)
admin.site.register(Classification)
