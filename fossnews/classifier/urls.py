from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register(r'attempts', ClassificationAttemptViewSet)

app_name = 'classifier'
urlpatterns = router.urls
