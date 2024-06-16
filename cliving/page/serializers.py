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