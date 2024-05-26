from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Page, Video, Checkpoint, Frame, Hold, FirstImage
from .serializers import PageSerializer, VideoSerializer, CheckpointSerializer, FrameSerializer, HoldSerializer, FirstImageSerializer
from rest_framework import viewsets
from .video_utils import generate_clip
import os
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .hold_utils import perform_object_detection

def time_to_seconds(time_obj):
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

# Create your views here.
class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    @action(detail = True, methods = ['post'])
    def create_clip(self, request, pk=None):
        video = self.get_object()
        checkpoints = video.checkpoints.order_by('time') #체크포인트를 시간순으로 정렬

        start_checkpoint = None
        created_clips = []

        for checkpoint in checkpoints:
            if checkpoint.type == 0:
                start_checkpoint = checkpoint
            elif checkpoint.type in [1, 2] and start_checkpoint:
                start_time = time_to_seconds(start_checkpoint.time)
                end_time = time_to_seconds(checkpoint.time)
                output_dir = 'media/clips'
                if not os.path.exists(output_dir):  #디렉토리 없으면 만들어줌.
                    os.makedirs(output_dir)
                output_path = f'media/clips/{video.id}_{start_time}_{end_time}.mp4' #클립 파일명 설정부분.
                generate_clip(video.videofile.path, start_time, end_time, output_path)
                created_clips.append(output_path)
                start_checkpoint = None

        return Response({'status': 'clips created', 'clips': created_clips})


class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = Checkpoint.objects.all()
    serializer_class = CheckpointSerializer

class FrameViewSet(viewsets.ModelViewSet):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer

class HoldViewSet(viewsets.ModelViewSet):
    queryset = Hold.objects.all()
    serializer_class = HoldSerializer
    
class Yolov8ViewSet(viewsets.ModelViewSet):
    queryset = FirstImage.objects.all()
    serializer_class = FirstImageSerializer

    @action(detail = True, methods = ['post'])
    def detect_image(self, request):
        image_file = self.get_object()
        image_path = default_storage.save(image_file.name, image_file)
        image_path = os.path.join(default_storage.location, image_path)

        detected_objects = perform_object_detection(image_path)

        default_storage.delete(image_path)

        return JsonResponse({'status': 'bboxes created', 'bboxes': detected_objects})
