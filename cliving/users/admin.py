from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'phone_number', 'birth_date', 'is_staff', 'is_active', 'is_verified', 'profile_image')
    list_filter = ('is_staff', 'is_active', 'is_verified')
    fieldsets = (
        (None, {'fields': ('username', 'phone_number', 'birth_date', 'password', 'profile_image')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'profile_image', 'birth_date', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser', 'is_verified')}  # email 삭제, phone_number 추가
        ),
    )
    search_fields = ('username', 'phone_number')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
