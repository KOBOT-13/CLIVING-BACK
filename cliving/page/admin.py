import os
from django.contrib import admin
from .models import *
from django.contrib.admin import DateFieldListFilter


class PageAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'climbing_center_name', 'play_time')  # 표시할 필드
    ordering = ('-date_dateFieldValue',)  # 기본 정렬 기준
    list_filter = (
        'user',  # 유저별 필터링
        ('date_dateFieldValue', DateFieldListFilter),  # 날짜별 필터링
    )
    search_fields = ('user__username', 'climbing_center_name')  # 검색 필드


class VideoAdmin(admin.ModelAdmin):
    list_display = ['user', 'page_id', 'page_id_int', 'custom_id', 'videofile', 'end_time', 'start_time', 'duration', 'video_color']
    fields = ['user', 'page_id', 'page_id_int', 'custom_id', 'videofile', 'end_time', 'start_time', 'duration','video_color']
    readonly_fields = ['custom_id']

# class VideoClipAdmin(admin.ModelAdmin):

# Register your models here.
admin.site.register(Page, PageAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(VideoClip)
admin.site.register(Checkpoint)
admin.site.register(Hold)
admin.site.register(Frame)
admin.site.register(FirstImage)




