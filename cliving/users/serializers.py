from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password


class CustomUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'birth_date']

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            birth_date=validated_data['birth_date'],
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'birth_date', 'profile_image']
        extra_kwargs = {
            'email': {'read_only': True},
            'username': {'required': False},
            'birth_date': {'required': False},
            'profile_image': {'required': False},
        }