from django.urls import path, include


from .views import PageViewSet, VideoViewSet, CheckpointViewSet, FrameViewSet, HoldViewSet, FirstImageView,  \
    SpecificMonthClimbingTimeView, MonthlyClimbingTimeView, AnnualClimbingTimeView, MonthlyColorTriesView, AnnualColorTriesView, \
    VideoFileView, AllPagesView, ImageUploadView, VideoClipViewSet, VideoClipPathsView, VideoClipThumbnailsView,  \
    VideoClipColorsView, VideoClipTypesView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('page', PageViewSet)
router.register('video', VideoViewSet)
router.register('videoclips', VideoClipViewSet)
router.register('checkpoint', CheckpointViewSet)
router.register('frame', FrameViewSet)
router.register('hold', HoldViewSet)
router.register('image', FirstImageView)


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
        path('upload/image/', ImageUploadView.as_view(), name='image-upload'),
        path('videoclips/by_page/thumbnails/<str:page_id>/', VideoClipThumbnailsView.as_view()),  # 썸네일 뷰 엔드포인트 추가
        path('videoclips/by_page/paths/<str:page_id>/', VideoClipPathsView.as_view()),  # 영상 경로 뷰 엔드포인트 추가
        # path('set-bottom-hold/', set_bottom_hold, name='set-bottom-hold'),
        path('hold/<int:first_image>/<int:index_number>/', HoldViewSet.as_view({'get': 'first_image_and_index_number'})),
        path('videoclips/by_page/colors/<str:page_id>/', VideoClipColorsView.as_view()),  # 썸네일 뷰 엔드포인트 추가
        path('videoclips/by_page/types/<str:page_id>/', VideoClipTypesView.as_view()),  # 썸네일 뷰 엔드포인트 추가    ])),
        path('firstimage/<int:first_image>/', FirstImageView.as_view({'get': 'first_image_id'})),
    ])),
]
    