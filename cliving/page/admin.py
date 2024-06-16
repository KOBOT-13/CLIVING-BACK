import os
from django.contrib import admin
from .models import *

"""class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_created', 'show_clips')

    def show_clips(self, obj):
        output_dir = 'media/clips'
        video_clips = [f"{output_dir}/{clip}" for clip in os.listdir(output_dir) if clip.startswith(f"{obj.id}_")]
        return ', '.join(video_clips)
    show_clips.short_description = 'Clips'"""
class VideoAdmin(admin.ModelAdmin):
    list_display = ['page_id', 'custom_id', 'videofile', 'end_time', 'start_time', 'duration', 'video_color']
    fields = ['page_id', 'custom_id', 'videofile', 'end_time', 'start_time', 'duration','video_color']
    readonly_fields = ['custom_id']


# Register your models here.
admin.site.register(Page)
admin.site.register(Video, VideoAdmin)
admin.site.register(Checkpoint)
admin.site.register(Hold)
admin.site.register(Frame)




