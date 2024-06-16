import os

from rest_framework import serializers
from .models import Page, Video, Checkpoint, Frame, Hold
#FirstImage

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

class ClimbingTimeSerializer(serializers.Serializer):
    year = serializers.CharField(max_length=4)  # 연도 정보
    month = serializers.CharField(max_length=2, required=False)  # 월 정보, 연간 뷰에서는 필요 없음
    total_climbing_time = serializers.IntegerField()  # 총 시간

class ColorTriesSerializer(serializers.Serializer):
    color = serializers.CharField()
    tries = serializers.IntegerField()

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
        
"""class FirstImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstImage
        field = '__all__'
    def get_bbox(self, img):
        output_dir = 'media/bbox'
        detected_bbox = []
        return detected_bbox"""