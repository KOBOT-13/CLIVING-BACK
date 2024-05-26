from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Page, Video, Checkpoint, Frame, Hold
from .serializers import PageSerializer, VideoSerializer, CheckpointSerializer, FrameSerializer, HoldSerializer
from rest_framework import viewsets
from .video_utils import generate_clip
import os

def time_to_seconds(time_obj):
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

# Create your views here.
class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    # 클립 생성 요청하는 방법 : http://127.0.0.1:8000/v1/video/<custom_id>/create_clip/ (POST or GET)
    # 클립 확인하는 방법(디렉토리 위치로 -> 나중에 클립 확인 api 만들 예정임) : http://127.0.0.1:8000/media/clips/240526-01_7_15.mp4
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
                output_path = f'media/clips/{video.custom_id}_{start_time}_{end_time}.mp4' #클립 파일명 설정부분.
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


