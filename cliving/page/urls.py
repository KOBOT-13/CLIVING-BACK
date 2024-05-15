from django.urls import path, include
from .views import PageViewSet, VideoViewSet, CheckpointViewSet, FrameViewSet, HoldViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('page', PageViewSet)
router.register('video', VideoViewSet)
router.register('checkpoint', CheckpointViewSet)
router.register('Frame', FrameViewSet)
router.register('hold', HoldViewSet)

urlpatterns = [
    path('v1/', include([
        path('', include(router.urls)),
    ])),
]