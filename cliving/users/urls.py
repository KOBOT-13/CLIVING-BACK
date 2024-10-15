from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import *

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('check-username/', CheckUsernameView.as_view(), name='check-username'),
    path('send-verification-code/', SendPhoneVerificationCodeView.as_view(), name='send_verification_code'),
    path('verify-phone-code/', VerifyPhoneCodeView.as_view(), name='verify_phone_code'),
    path('auth/registration/', RegisterView.as_view(), name='custom-registration'),
    path('auth/login/', CustomLoginView.as_view(), name='custom_login'),
    path('auth/logout/', CustomLogoutView.as_view(), name='custom-logout'),

    path('auth/', include('dj_rest_auth.urls')),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('delete_account/', DeleteAccountView.as_view(), name='delete-account'),
]