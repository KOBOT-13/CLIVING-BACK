import os

from rest_framework import serializers
from .models import Page, Video, Checkpoint, Frame, Hold, FirstImage

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'
class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

    def get_clips(self, obj):
        output_dir = 'media/clips'
        video_clips = [f"{output_dir}/{clip}" for clip in os.listdir(output_dir) if clip.startswith(f"{obj.id}_")]
        return video_clips

class CheckpointSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Checkpoint
        fields = '__all__'

class FrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frame
        fields = ['image']
class HoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hold
        fields = '__all__'
        
class FirstImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstImage
        field = ['image']
    def get_bbox(self, img):
        output_dir = 'media/bbox'
        detected_bbox = []