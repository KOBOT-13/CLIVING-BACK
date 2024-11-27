from django.urls import path, include


from .views import PageViewSet, VideoViewSet, CheckpointViewSet, FrameViewSet, HoldViewSet, FirstImageView, \
    SpecificMonthClimbingTimeView, MonthlyClimbingTimeView, AnnualClimbingTimeView, SpecificMonthColorTriesView, \
    SpecificAnnualColorTriesView, \
    VideoFileView, AllPagesView, ImageUploadView, VideoClipViewSet, VideoClipPathsView, VideoClipThumbnailsView, \
    VideoClipColorsView, VideoClipTypesView, SpecificAnnualClimbingTimeView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('page', PageViewSet, basename='page')
router.register('video', VideoViewSet, basename='video')
router.register('videoclips', VideoClipViewSet, basename='videoclips')
router.register('checkpoint', CheckpointViewSet, basename='checkpoint')
router.register('frame', FrameViewSet, basename='frame')
router.register('hold', HoldViewSet, basename='hold')
router.register('image', FirstImageView, basename='image')


urlpatterns = [
    path('v1/', include([
        path('', include(router.urls)),
        path('statistics/monthly/climbing-time/', MonthlyClimbingTimeView.as_view(), name='monthly-climbing-time'),
        path('statistics/annual/climbing-time/', AnnualClimbingTimeView.as_view(), name='annual-climbing-time'),
        path('statistics/climbing-time/<int:year>/<int:month>/', SpecificMonthClimbingTimeView.as_view(), name='specific-month-climbing-time'),
        path('statistics/climbing-time/<int:year>/', SpecificAnnualClimbingTimeView.as_view(), name='specific-annual-climbing-time'),
        path('statistics/color-tries/<int:year>/<int:month>/', SpecificMonthColorTriesView.as_view(), name='monthly-color-tries'),
        path('statistics/color-tries/<int:year>/', SpecificAnnualColorTriesView.as_view(), name='annual-color-tries'),
        path('video/<str:custom_id>/file/', VideoFileView.as_view(), name='video-file'),
        path('pages/<int:year>/', AllPagesView.as_view(), name='all-pages-list'),
        path('videoclips/by_page/', VideoClipViewSet.as_view({'get': 'by_page'})),
        path('upload/image/', ImageUploadView.as_view(), name='image-upload'),
        path('videoclips/by_page/thumbnails/<str:page_id>/', VideoClipThumbnailsView.as_view()),
        path('videoclips/by_page/paths/<str:page_id>/', VideoClipPathsView.as_view()),
        path('hold/<int:first_image>/<int:index_number>/', HoldViewSet.as_view({'get': 'first_image_and_index_number', 'put': 'put_hold'})),
        path('videoclips/by_page/colors/<str:page_id>/', VideoClipColorsView.as_view()),
        path('videoclips/by_page/types/<str:page_id>/', VideoClipTypesView.as_view()),
        path('firstimage/<int:first_image>/', FirstImageView.as_view({'get': 'first_image_id'})),
    ])),
]
    