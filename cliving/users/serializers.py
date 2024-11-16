from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from .models import CustomUser, PhoneVerification


class CustomUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'nickname', 'password1', 'password2', 'phone_number']

    def validate(self, data):
        # 비밀번호 일치 여부 확인
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")

        # 전화번호 인증 여부 확인
        try:
            verification = PhoneVerification.objects.get(phone_number=data['phone_number'])
            if not verification.is_verified:
                raise serializers.ValidationError("휴대폰 인증이 필요합니다.")
        except PhoneVerification.DoesNotExist:
            raise serializers.ValidationError("인증되지 않은 전화번호입니다.")

        return data

    def create(self, validated_data):
        # 비밀번호 처리
        password = validated_data.pop('password1')
        validated_data.pop('password2')

        # 유저 생성 및 인증 처리
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_verified = True  # 인증된 사용자로 설정
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'nickname', 'profile_image']  # 필요한 필드만 직렬화