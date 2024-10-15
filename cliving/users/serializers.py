from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password


class CustomUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'nickname', 'password1', 'password2', 'phone_number', 'birth_date']

    def create(self, validated_data):
        if validated_data['password1'] != validated_data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        user = CustomUser(
            username=validated_data['username'],
            nickname=validated_data['nickname'],
            phone_number=validated_data['phone_number'],
            birth_date=validated_data.get('birth_date', None)
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'nickname', 'birth_date', 'profile_image']
        extra_kwargs = {
            'username': {'required': False},
            'nickname': {'required': False},
            'birth_date': {'required': False},
            'profile_image': {'required': False},
        }
