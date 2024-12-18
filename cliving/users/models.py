from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, nickname, phone_number, password=None, **extra_fields):
        if not username:
            raise ValueError('The username field must be set')
        if not password:
            raise ValueError('The Password field must be set')
        if not phone_number:
            raise ValueError('The phone_number field must be set')
        user = self.model(
            username=username,
            nickname=nickname,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nickname, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, nickname, phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    nickname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    birth_date = models.DateField(null=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/profile_image.png', blank=False, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nickname', 'phone_number']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class PhoneVerification(models.Model):
    phone_number = models.CharField(max_length=15)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        # 인증번호 유효 시간 설정 (예: 5분)
        return now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.phone_number} - {self.verification_code}"

