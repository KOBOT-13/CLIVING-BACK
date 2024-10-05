from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from allauth.account.views import ConfirmEmailView
from allauth.account.models import EmailConfirmationHMAC
from allauth.account.models import EmailAddress
from rest_framework import status, mixins
from dj_rest_auth.views import LoginView
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import views as auth_views
from cliving.settings import *
# from users.adapter import CustomAccountAdapter
from rest_framework import generics
from django.utils.http import urlsafe_base64_decode
from .models import CustomUser
from .serializers import CustomUserSerializer, ProfileUpdateSerializer
from allauth.account.utils import send_email_confirmation
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


class RegisterView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer

    def perform_create(self, serializer):
        user = serializer.save()  # 사용자를 저장합니다.

        # 이메일 주소를 가져옵니다.
        email_address = EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)

        # 이메일 인증 링크를 보내는 함수 호출
    #     self.send_email_confirmation(user, email_address)
    #
    # def send_email_confirmation(self, user, email_address):
    #     request = self.request  # 현재 요청 객체를 사용합니다.
    #
    #     # 이메일 인증 메일 전송
    #     send_email_confirmation(request, user)


class CheckUsernameView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            return Response({"detail": "이미 존재하는 닉네임입니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "사용 가능한 닉네임입니다."}, status=status.HTTP_200_OK)


class CheckEmailView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({"detail": "이미 존재하는 이메일 주소입니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "사용 가능한 이메일 주소입니다."}, status=status.HTTP_200_OK)


class CustomConfirmEmailView(ConfirmEmailView):
    template_name = 'account/email/success_verify_email.html'

    def get_template_names(self) -> list[str]:
        return super().get_template_names()

    def dispatch(self, request, *args, **kwargs):
        key = kwargs.get('key', None)
        print(f'dispatch called with key: {key}')
        if key:
            email_confirmation = EmailConfirmationHMAC.from_key(key)
            if email_confirmation:
                email_address = email_confirmation.email_address
                print(f'EmailConfirmation found: {email_confirmation}')

                # 여기서 이메일 인증을 완료
                email_confirmation.confirm(request)

                # 다시 한 번 확인
                email_address.refresh_from_db()

                if email_address and email_address.verified:
                    user = email_address.user
                    user.is_verified = True
                    user.save()
                    print(f'User {user.email} verified and saved')
                else:
                    print(f'EmailAddress not verified or not found: {email_address.email if email_address else "None"}')
            else:
                print(f'EmailConfirmation not found for key: {key}')

        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        print('custom login view call')

        # 요청에서 email과 password 가져오기
        email = request.data.get('email')  # 이메일 필드
        password = request.data.get('password')  # 비밀번호 필드
        print(email)
        print(password)

        # 이메일로 사용자 인증
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # 이메일 주소로 사용자 가져오기
            email_address = EmailAddress.objects.filter(email=email, primary=True).first()
            # if email_address and not email_address.verified:
            #     # 이메일 주소가 인증되지 않은 경우
            #     adapter = CustomAccountAdapter()
            #     adapter.send_email_confirmation(request, user)  # 인증 이메일 재전송
            #     return Response(
            #         {"detail": "이메일 인증이 필요합니다. 인증 이메일이 재전송되었습니다."},
            #         status=status.HTTP_401_UNAUTHORIZED
            #     )
            #
            # # 이메일 인증이 완료된 경우 로그인
            login(request, user)
            return super().post(request, *args, **kwargs)
        else:
            # 로그인 실패 시 처리
            if not EmailAddress.objects.filter(email=email).exists():
                return Response(
                    {"detail": "등록된 이메일 주소가 아닙니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.filter(email=email).first()
            if user and not user.check_password(password):
                return Response(
                    {"detail": "비밀번호가 잘못되었습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {"detail": "이메일 주소 또는 비밀번호가 잘못되었습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )


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


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile_image = user.profile_image.url if user.profile_image else None
        return Response({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'is_staff': user.is_staff,
            'birth_date': user.birth_date,
            'profile_image': profile_image,
        })


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        request.session['password_reset_token'] = token
        current_site = get_current_site(request)
        domain = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'

        # 비밀번호 재설정 링크를 먼저 생성
        reset_link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        reset_url = f'{protocol}://{domain}{reset_link}'

        mail_subject = '[CLIVING] 비밀번호 재설정 이메일'
        message = render_to_string('account/email/password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })
        send_mail(
            mail_subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=message
        )

        return Response({'success': '비밀번호 재설정 이메일이 전송되었습니다.'}, status=status.HTTP_200_OK)


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


class ProfileUpdateView(generics.GenericAPIView, mixins.UpdateModelMixin):
    queryset = CustomUser.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        try:
            user.delete()
            return Response({"detail": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"회원 탈퇴 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
