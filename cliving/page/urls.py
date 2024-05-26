from django.urls import path, include
from .views import PageViewSet, VideoViewSet, CheckpointViewSet, FrameViewSet, HoldViewSet, Yolov8ViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('page', PageViewSet)
router.register('video', VideoViewSet)
router.register('checkpoint', CheckpointViewSet)
router.register('frame', FrameViewSet)
router.register('hold', HoldViewSet)
router.register('yolov8', Yolov8ViewSet)

urlpatterns = [
    path('v1/', include([
        path('', include(router.urls)),
    ])),
]