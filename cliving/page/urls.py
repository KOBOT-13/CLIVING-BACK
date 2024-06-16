from django.urls import path, include

from .views import PageViewSet, VideoViewSet, CheckpointViewSet, FrameViewSet, HoldViewSet, Yolov8ViewSet, \
    SpecificMonthClimbingTimeView, MonthlyClimbingTimeView, AnnualClimbingTimeView, MonthlyColorTriesView, \
    AnnualColorTriesView, ImageUploadView


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
        path('statistics/monthly/climbing-time/', MonthlyClimbingTimeView.as_view(), name='monthly-climbing-time'),
        path('statistics/annual/climbing-time/', AnnualClimbingTimeView.as_view(), name='annual-climbing-time'),
        path('statistics/climbing-time/<int:year>/<int:month>/', SpecificMonthClimbingTimeView.as_view(), name='specific-month-climbing-time'),
        path('statistics/monthly/color-tries/', MonthlyColorTriesView.as_view(), name='monthly-color-tries'),
        path('statistics/annual/color-tries/', AnnualColorTriesView.as_view(), name='annual-color-tries'),

        path('upload/', ImageUploadView.as_view(), name='image-upload'),

    ])),
]