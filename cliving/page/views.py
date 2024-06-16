from collections import Counter

from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.views import APIView
from django.utils import timezone
from .models import Page, Video, Checkpoint, Frame, Hold
#FirstImage
from .serializers import PageSerializer, VideoSerializer, CheckpointSerializer, FrameSerializer, HoldSerializer, ColorTriesSerializer, ClimbingTimeSerializer
#FirstImageSerializer

from rest_framework import viewsets, status

from .video_utils import generate_clip
from django.db.models import Sum, Count, F
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


class SpecificMonthClimbingTimeView(APIView): # 특정 달 클라이밍 시간 get (1월 ~12월 반복 불러오기로 사용하면 될 듯 함)
    def get(self, request, year, month):
        # 입력 받은 연월을 YYMM 형태로 포맷팅
        specific_month = f'{year}{month:02d}'
        total_time = Page.objects.filter(date__startswith=specific_month).aggregate(total_time=Sum('play_time'))
        # 플레이 시간이 없는 경우 0으로 반환
        total_time = total_time['total_time'] if total_time['total_time'] is not None else 0

        # 시리얼라이저를 사용하여 데이터 포맷
        serializer = ClimbingTimeSerializer({
            'year': year,
            'month': month,
            'total_climbing_time': total_time
        })
        return Response(serializer.data)

class MonthlyClimbingTimeView(APIView):
    def get(self, request):
        current_month = timezone.now().strftime('%y%m')
        total_time = Page.objects.filter(date__startswith=current_month).aggregate(total_time=Sum('play_time'))
        total_time = total_time['total_time'] if total_time['total_time'] is not None else 0

        # 시리얼라이저를 사용하여 데이터 포맷
        serializer = ClimbingTimeSerializer({
            'year': current_month[:2],
            'month': current_month[2:],
            'total_climbing_time': total_time
        })
        return Response(serializer.data)


class AnnualClimbingTimeView(APIView):
    def get(self, request):
        current_year = timezone.now().strftime('%y')
        total_time = Page.objects.filter(date__startswith=current_year).aggregate(total_time=Sum('play_time'))
        total_time = total_time['total_time'] if total_time['total_time'] is not None else 0

        # 시리얼라이저를 사용하여 데이터 포맷
        serializer = ClimbingTimeSerializer({
            'year': current_year,
            'total_climbing_time': total_time
        })
        return Response(serializer.data)


class MonthlyColorTriesView(APIView):
    def get(self, request):
        current_month = timezone.now().strftime('%y%m')
        monthly_pages = Page.objects.filter(date__startswith=current_month)

        color_counter = Counter()
        for page in monthly_pages:
            color_counter.update(page.bouldering_clear_color)

        results = [ColorTriesSerializer({'color': color, 'tries': count}).data for color, count in color_counter.items()]
        return Response(results)

class AnnualColorTriesView(APIView):
    def get(self, request):
        current_year = timezone.now().strftime('%y')
        yearly_pages = Page.objects.filter(date__startswith=current_year)

        color_counter = Counter()
        for page in yearly_pages:
            color_counter.update(page.bouldering_clear_color)

        results = [ColorTriesSerializer({'color': color, 'tries': count}).data for color, count in color_counter.items()]
        return Response(results)

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
    
"""class Yolov8ViewSet(viewsets.ModelViewSet):
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
"""