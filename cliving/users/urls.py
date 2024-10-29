from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import *

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # Check
    path('check-username/', CheckUsernameView.as_view(), name='check-username'),
    path('check-nickname/', CheckNicknameView.as_view(), name='check-nickname'),
    path('check-phone-number/', CheckPhoneNumberView.as_view(), name='check-phone-number'),

    # registration
    path('send-verification-code/', SendPhoneVerificationCodeView.as_view(), name='send_verification_code'),
    path('verify-phone-code/', VerifyPhoneCodeView.as_view(), name='verify_phone_code'),
    path('auth/registration/', RegisterView.as_view(), name='custom-registration'),

    # log in&out
    path('auth/login/', CustomLoginView.as_view(), name='custom_login'),
    path('auth/logout/', CustomLogoutView.as_view(), name='custom-logout'),

    # profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),

    # delete_account
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),

    # change password
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]