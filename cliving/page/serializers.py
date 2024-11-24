import os
import json
from rest_framework import serializers
from .models import Page, Video, Checkpoint, Frame, Hold, FirstImage, VideoClip


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class VideoClipSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoClip
        fields = '__all__'


class VideoClipThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoClip
        fields = ['output_path', 'thumbnail', 'clip_color', 'type']


class ClimbingTimeSerializer(serializers.Serializer):
    year = serializers.CharField(max_length=4)  # 연도 정보
    month = serializers.CharField(max_length=2, required=False)  # 월 정보, 연간 뷰에서는 필요 없음
    total_climbing_time = serializers.IntegerField()  # 총 시간
    total_climbing_time_hhmm = serializers.SerializerMethodField()  # 총 시간을 hh:mm 형식으로 반환

    def get_total_climbing_time_hhmm(self, obj):
        total_seconds = obj.get('total_climbing_time', 0)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}시간 {int(minutes)}분"

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
        

class FirstImageCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstImage
        fields = '__all__'

class FirstImageSerializer(serializers.ModelSerializer):
    holds = serializers.SerializerMethodField()
    
    class Meta:
        model = FirstImage
        fields = ['image', 'holds']

    def get_holds(self, obj):
        holds = Hold.objects.filter(first_image=obj)
        return HoldSerializer(holds, many=True).data