import os
import json

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

class ClimbingTimeSerializer(serializers.Serializer):
    year = serializers.CharField(max_length=4)  # 연도 정보
    month = serializers.CharField(max_length=2, required=False)  # 월 정보, 연간 뷰에서는 필요 없음
    total_climbing_time = serializers.IntegerField()  # 총 시간
    total_climbing_time_hhmm = serializers.SerializerMethodField()  # 총 시간을 hh:mm 형식으로 반환

    def get_total_climbing_time_hhmm(self, obj):
        total_seconds = obj.get('total_climbing_time', 0)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}"

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
        


class FirstImageSerializer(serializers.ModelSerializer):
    bbox = serializers.SerializerMethodField()
    
    class Meta:
        model = FirstImage
        field = ['image', 'bbox']
    def get_bbox(self, obj):
        output_dir = 'media/bbox'
        bbox_file_path = os.path.join(output_dir, f"{obj.id}_bbox.json")

        if os.path.exists(bbox_file_path):
            with open(bbox_file_path, 'r') as bbox_file:
                detected_bbox = json.load(bbox_file)
        else:
            detected_bbox = []

        return detected_bbox
