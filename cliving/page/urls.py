from django.urls import path, include

from .views import PageViewSet, VideoViewSet, CheckpointViewSet, FrameViewSet, HoldViewSet, \
    SpecificMonthClimbingTimeView, MonthlyClimbingTimeView, AnnualClimbingTimeView, MonthlyColorTriesView, \
    AnnualColorTriesView, ImageUploadView, VideoClipViewSet, VideoClipPathsView, VideoClipThumbnailsView, \
    VideoClipPathsView

from .views import PageViewSet, VideoViewSet, CheckpointViewSet, FrameViewSet, HoldViewSet, \
    SpecificMonthClimbingTimeView, \
    MonthlyClimbingTimeView, AnnualClimbingTimeView, MonthlyColorTriesView, AnnualColorTriesView, \
    VideoFileView, AllPagesView, ImageUploadView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('page', PageViewSet)
router.register('video', VideoViewSet)
router.register('videoclips', VideoClipViewSet)
router.register('checkpoint', CheckpointViewSet)
router.register('frame', FrameViewSet)
router.register('hold', HoldViewSet)

urlpatterns = [
    path('v1/', include([
        path('', include(router.urls)),
        path('statistics/monthly/climbing-time/', MonthlyClimbingTimeView.as_view(), name='monthly-climbing-time'),
        path('statistics/annual/climbing-time/', AnnualClimbingTimeView.as_view(), name='annual-climbing-time'),
        path('statistics/climbing-time/<int:year>/<int:month>/', SpecificMonthClimbingTimeView.as_view(), name='specific-month-climbing-time'),
        path('statistics/monthly/color-tries/', MonthlyColorTriesView.as_view(), name='monthly-color-tries'),
        path('statistics/annual/color-tries/', AnnualColorTriesView.as_view(), name='annual-color-tries'),
        path('video/<str:custom_id>/file/', VideoFileView.as_view(), name='video-file'),
        path('pages/<int:year>/<int:month>/', AllPagesView.as_view(), name='all-pages-list'),
        path('videoclips/by_page/', VideoClipViewSet.as_view({'get': 'by_page'})),
        path('upload/', ImageUploadView.as_view(), name='image-upload'),
        path('videoclips/by_page/thumbnails/<str:page_id>/', VideoClipThumbnailsView.as_view()),  # 썸네일 뷰 엔드포인트 추가
        path('videoclips/by_page/paths/<str:page_id>/', VideoClipPathsView.as_view()),  # 영상 경로 뷰 엔드포인트 추가


    ])),
]