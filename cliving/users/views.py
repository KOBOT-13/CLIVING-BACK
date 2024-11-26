import random
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, mixins
from dj_rest_auth.views import LoginView
from django.contrib.auth import authenticate, login
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import views as auth_views
# from users.adapter import CustomAccountAdapter
from rest_framework import generics
from django.utils.http import urlsafe_base64_decode
from .models import CustomUser, PhoneVerification
from .serializers import CustomUserSerializer, ProfileSerializer
from django.contrib.auth import authenticate, login, get_user_model
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
import re

User = get_user_model()

from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
from django.conf import settings


def send_sms(phone_number, verification_code):
    api_key = settings.COOLSMS_API_KEY
    api_secret = settings.COOLSMS_SECRET_KEY

    params = {
        'type': 'sms',
        'to': phone_number,
        'from': settings.COOLSMS_SENDER_NUMBER,  # 발신자 번호
        'text': f'[인증번호] {verification_code}입니다.'
    }

    try:
        cool = Message(api_key, api_secret)
        response = cool.send(params)
        print(f"발송 성공: {response}")
    except CoolsmsException as e:
        print(f"발송 실패: {e.code}, {e.msg}")


def send_verification_code_func(phone_number):
    verification_code = str(random.randint(100000, 999999))

    phone_number = phone_number.replace('-', '')

    # 기존 인증 기록 삭제 (같은 번호에 대해)
    PhoneVerification.objects.filter(phone_number=phone_number).delete()

    # 새로운 인증번호 저장
    PhoneVerification.objects.create(
        phone_number=phone_number,
        verification_code=verification_code
    )

    # send_sms 주석 해제 시, 유료 sms 전송. 건당 20원.
    print(f"Sending SMS to {phone_number}: 인증번호는 {verification_code}입니다.")
    send_sms(phone_number, verification_code)


class SendPhoneVerificationCodeView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')

        send_verification_code_func(phone_number)

        return Response({"detail": "인증번호가 발송되었습니다."}, status=status.HTTP_200_OK)


class VerifyPhoneCodeView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        input_code = request.data.get('verification_code')
        phone_number = phone_number.replace('-', '')

        try:
            verification = PhoneVerification.objects.get(phone_number=phone_number)

            if verification.is_expired():
                return Response({"detail": "인증번호가 만료되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

            if verification.verification_code != input_code:
                return Response({"detail": "인증번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

            # 인증 성공 처리
            verification.is_verified = True
            verification.save()

            return Response({"detail": "휴대폰 인증 성공!"}, status=status.HTTP_200_OK)

        except PhoneVerification.DoesNotExist:
            return Response({"detail": "해당 번호에 대한 인증 요청이 없습니다."}, status=status.HTTP_404_NOT_FOUND)


class RegisterView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer

    def perform_create(self, serializer):
        # 유저 생성 (검증 및 저장은 시리얼라이저가 처리)
        serializer.save()


class CheckUsernameView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            return Response({"detail": "이미 존재하는 ID입니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "사용 가능한 ID입니다."}, status=status.HTTP_200_OK)


class CheckNicknameView(APIView):
    def post(self, request, *args, **kwargs):
        nickname = request.data.get('nickname')
        if User.objects.filter(nickname=nickname).exists():
            return Response({"detail": "이미 존재하는 닉네임입니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "사용 가능한 닉네임입니다."}, status=status.HTTP_200_OK)


class CheckPhoneNumberView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({"detail": "이미 존재하는 휴대폰 번호입니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "사용 가능한 휴대폰 번호입니다."}, status=status.HTTP_200_OK)


class CustomLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # 사용자명과 비밀번호로 사용자 인증
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 토큰 발행
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "detail": "로그인 성공",
                "refresh": str(refresh),
                "access": access_token,
                "username": user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "아이디 또는 비밀번호가 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)


class CustomLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "로그아웃 성공"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"로그아웃 실패: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # 기존 비밀번호와 새 비밀번호 가져오기
        current_password = request.data.get('current_password')
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')

        if new_password1 != new_password2:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        new_password = new_password1

        # 기존 비밀번호 확인
        if not user.check_password(current_password):
            return Response({"detail": "현재 비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 새 비밀번호 유효성 검증
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"detail": list(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 비밀번호 변경
        user.set_password(new_password)
        user.save()

        return Response({"detail": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        try:
            user.delete()
            return Response({"detail": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"회원 탈퇴 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserAndSendVerificationCode(APIView):
    def post(self, request):
        username = request.data.get("username")
        phone_number = request.data.get("phone_number")
        phone_number = phone_number.replace('-', '')

        try:
            # 유저 검증
            user = User.objects.get(username=username, phone_number=phone_number)

            # 인증번호 발송
            send_verification_code_func(phone_number)

            return Response({"detail": "User verified. Verification code sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found or phone number mismatch."}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    def post(self, request):
        username = request.data.get("username")
        new_password = request.data.get("password1")
        confirm_password = request.data.get("password2")

        if new_password != confirm_password:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(username=username)

            user.set_password(new_password)
            user.save()

            return Response({"detail": "Password reset successfully!"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # 현재 로그인된 사용자만 반환
        profile = self.request.user
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # 현재 로그인된 사용자만 업데이트
        profile = self.request.user
        serializer = self.get_serializer(profile, data=request.data, partial=True)  # 부분 업데이트(PATCH)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_queryset(self):
        # 인증된 사용자만 쿼리셋 반환 (list 액션에서 필요할 수 있음)
        return CustomUser.objects.filter(id=self.request.user.id)


