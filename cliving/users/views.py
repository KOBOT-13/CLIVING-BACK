import random
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, mixins
from dj_rest_auth.views import LoginView
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import views as auth_views
# from users.adapter import CustomAccountAdapter
from rest_framework import generics
from django.utils.http import urlsafe_base64_decode
from .models import CustomUser
from .serializers import CustomUserSerializer, ProfileUpdateSerializer
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


def send_sms(phone_number, verification_code):
    print(f"Sending SMS to {phone_number}: 인증번호는 {verification_code}입니다.")
    # Twilio API OR KAKAO API


class SendPhoneVerificationCodeView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        verification_code = random.randint(100000, 999999)

        # 인증번호를 세션에 저장
        request.session['verification_code'] = verification_code
        request.session['phone_number'] = phone_number

        send_sms(phone_number, verification_code)

        return Response({"detail": "인증번호가 발송되었습니다."}, status=status.HTTP_200_OK)


class VerifyPhoneCodeView(APIView):
    def post(self, request, *args, **kwargs):
        input_code = request.data.get('verification_code')
        session_code = request.session.get('verification_code')
        phone_number = request.session.get('phone_number')

        if not session_code or input_code != str(session_code):
            return Response({"detail": "인증번호가 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

        request.session['is_verified'] = True
        del request.session['verification_code']  # 인증번호 제거

        return Response({"detail": "휴대폰 인증이 완료되었습니다.", "phone_number": phone_number}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer

    def perform_create(self, serializer):
        phone_number = self.request.session.get('phone_number')
        is_verified_in_session = self.request.session.get('is_verified')

        # 세션에서 인증 여부 확인
        if not is_verified_in_session:
            return Response({"detail": "휴대폰 인증을 완료하세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 회원가입 진행, 인증된 사용자로 저장
        user = serializer.save(phone_number=phone_number)
        user.is_verified = True
        user.save()

        return Response({"detail": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)


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

#
# class DeleteAccountView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def delete(self, request, *args, **kwargs):
#         user = request.user
#         try:
#             user.delete()
#             return Response({"detail": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"detail": f"회원 탈퇴 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class ProfileUpdateView(generics.GenericAPIView, mixins.UpdateModelMixin):
#     queryset = CustomUser.objects.all()
#     serializer_class = ProfileUpdateSerializer
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#
#     def get_object(self):
#         return self.request.user
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
#
#     def patch(self, request, *args, **kwargs):
#         return self.partial_update(request, *args, **kwargs)
#
#
# class ProfileView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.user
#         profile_image = user.profile_image.url if user.profile_image else None
#         return Response({
#             'id': user.id,
#             'username': user.username,
#             'is_staff': user.is_staff,
#             'birth_date': user.birth_date,
#             'profile_image': profile_image,
#         })
#
# #
# class PasswordResetRequestView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         if not email:
#             return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
#
#         token = default_token_generator.make_token(user)
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         request.session['password_reset_token'] = token
#         current_site = get_current_site(request)
#         domain = request.get_host()
#         protocol = 'https' if request.is_secure() else 'http'
#
#         # 비밀번호 재설정 링크를 먼저 생성
#         reset_link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
#         reset_url = f'{protocol}://{domain}{reset_link}'
#
#         mail_subject = '[CLIVING] 비밀번호 재설정 이메일'
#         message = render_to_string('account/email/password_reset_email.html', {
#             'user': user,
#             'reset_url': reset_url,
#         })
#         send_mail(
#             mail_subject,
#             message,
#             settings.DEFAULT_FROM_EMAIL,
#             [email],
#             fail_silently=False,
#             html_message=message
#         )
#
#         return Response({'success': '비밀번호 재설정 이메일이 전송되었습니다.'}, status=status.HTTP_200_OK)
#

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    def dispatch(self, request, *args, **kwargs):
        # URL에서 uidb64와 token을 가져오기
        uidb64 = kwargs.get('uidb64')
        token = request.session.get('password_reset_token')

        # uidb64를 디코드하여 user ID를 복원
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # 토큰 유효성 검사
        if user is not None and default_token_generator.check_token(user, token):
            # 토큰이 유효하면, user와 token을 설정
            self.user = user
            self.token = token
        else:
            # 토큰이 유효하지 않으면, 오류 페이지로 리다이렉트
            return render(request, 'account/email/password_reset_invalid.html')

        # 나머지 dispatch 처리
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data.get('new_password1')
        password_regex = re.compile(r'^(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-])(?=.*[0-9]).{8,32}$')

        if not password_regex.match(password):
            form.add_error('new_password1', '비밀번호는 8-32자리여야 하며, 최소 하나의 문자, 숫자 및 특수 문자를 포함해야 합니다.')
            return self.form_invalid(form)

        form.save()  # 비밀번호 저장
        print("비밀번호 재설정이 완료되었습니다.")
        messages.success(self.request, '비밀번호가 성공적으로 재설정되었습니다.')
        return redirect('/api/users/password_reset/done/')

    def form_invalid(self, form):
        print("폼이 유효하지 않습니다. 오류:", form.errors)
        messages.error(self.request, '비밀번호 재설정 중 오류가 발생했습니다. 다시 시도해주세요.')
        return self.render_to_response(self.get_context_data(form=form))




