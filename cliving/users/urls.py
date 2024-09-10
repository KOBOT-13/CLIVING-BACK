from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import *

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('check-username/', CheckUsernameView.as_view(), name='check-username'),
    path('check-email/', CheckEmailView.as_view(), name='check-email'),

    # allauth
    path('accounts/', include('allauth.urls')),
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password_reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='account/email/password_reset_complete.html'),
         name='password_reset_complete'),
    path(
        'password_reset_confirm/<uidb64>/<token>/',
        CustomPasswordResetConfirmView.as_view(template_name='account/email/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),

    # path('password_reset_complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # dj-rest-auth
    path('auth/registration/', RegisterView.as_view(), name='custom-registration'),
    path('auth/login/', CustomLoginView.as_view(), name='custom_login'),
    path('auth/logout/', CustomLogoutView.as_view(), name='custom-logout'),
    path('auth/', include('dj_rest_auth.urls')),
    path("auth/registration/account-confirm-email/<str:key>", CustomConfirmEmailView.as_view(),
         name="account_confirm_email"),
    # path('kakao-login/', kakao_login_view, name='kakao-login'),
    # path('kakao-user-info/', kakao_user_info, name='kakao-user-info'),

    path('profile/', ProfileView.as_view(), name='profile'),  # 프로필 URL 추가
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('delete_account/', DeleteAccountView.as_view(), name='delete-account'),
]