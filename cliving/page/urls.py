from django.urls import path, include
from .views import PageViewSet #, ClipViewSet, FrameViewSet, HoldViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('page', PageViewSet)
# router.register('clip', ClipViewSet)
# router.register('Frame', FrameViewSet)
# router.register('hold', HoldViewSet)

urlpatterns = [
    path('', include([
        path('', include(router.urls)),
    ])),
]