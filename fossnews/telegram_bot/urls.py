from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register(r'users', TelegramUserViewSet)

app_name = 'telegram_bot'
urlpatterns = router.urls
