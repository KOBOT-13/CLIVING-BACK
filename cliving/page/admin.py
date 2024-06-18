import os
from django.contrib import admin
from .models import *

class VideoAdmin(admin.ModelAdmin):
    list_display = ['page_id', 'custom_id', 'videofile', 'end_time', 'start_time', 'duration', 'video_color']
    fields = ['page_id', 'custom_id', 'videofile', 'end_time', 'start_time', 'duration','video_color']
    readonly_fields = ['custom_id']

# Register your models here.
admin.site.register(Page)
admin.site.register(Video, VideoAdmin)
admin.site.register(VideoClip)
admin.site.register(Checkpoint)
admin.site.register(Hold)
admin.site.register(Frame)
admin.site.register(FirstImage)




