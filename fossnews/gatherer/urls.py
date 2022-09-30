from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register(r'sources', SourceViewSet)
router.register(r'results', GatheringResultViewSet)
router.register(r'news', NewsViewSet)
router.register(r'issues', DigestIssueViewSet)
router.register(r'issue-links', DigestIssueLinkViewSet)

app_name = 'gatherer'
urlpatterns = router.urls
