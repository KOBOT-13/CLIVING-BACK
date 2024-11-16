from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PhoneVerification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'nickname', 'phone_number', 'is_staff', 'is_active', 'is_verified', 'profile_image')
    list_filter = ('is_staff', 'is_active', 'is_verified')
    fieldsets = (
        (None, {'fields': ('username', 'nickname', 'phone_number', 'password', 'profile_image')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nickname', 'phone_number', 'profile_image', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser', 'is_verified')}  # email 삭제, phone_number 추가
        ),
    )
    search_fields = ('username', 'nickname', 'phone_number')
    ordering = ('username',)


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'verification_code', 'is_verified', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('phone_number',)
