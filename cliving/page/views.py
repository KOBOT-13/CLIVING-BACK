from collections import Counter

from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Page, Video, Checkpoint, Frame, Hold, FirstImage, VideoClip
from .serializers import PageSerializer, VideoSerializer, CheckpointSerializer, FrameSerializer, HoldSerializer, \
    ColorTriesSerializer, ClimbingTimeSerializer, FirstImageSerializer, VideoClipSerializer, \
    VideoClipThumbnailSerializer
from rest_framework import viewsets, status
from .video_utils import generate_clip, generate_thumbnail
from django.db.models import Sum, Count, F
import os
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .hold_utils import perform_object_detection, save_detection_results

def time_to_seconds(time_obj):
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

# Create your views here.
class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
class AllPagesView(APIView):
    def get(self, request, year, month):
        # 'date' 필드가 YYMMDD 형식이므로 year와 month를 기반으로 필터링
        specific_month = f'{year}{month:02d}'
        pages = Page.objects.filter(date__startswith=specific_month)
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
                start_time_sec = time_to_seconds(start_checkpoint.time)
                end_time_sec = time_to_seconds(checkpoint.time)
                mid_time_sec = (start_time_sec + end_time_sec) / 2 - start_time_sec  # 중간 시간 계산

                output_dir = 'media/clips'
                if not os.path.exists(output_dir):  #디렉토리 없으면 만들어줌.
                    os.makedirs(output_dir)
                output_path = f'media/clips/{video.custom_id}_{start_time_sec}_{end_time_sec}.mp4' #클립 파일명 설정부분.
                print(f"Generating clip to path: {output_path}")
                print(f"Video file path: {video.videofile.path}")

                try:
                    generate_clip(video.videofile.path, start_time_sec, end_time_sec, output_path)
                except Exception as e:
                    print(f"Error generating clip: {e}")
                    continue

                # 썸네일 생성 및 저장
                thumbnail_path = f'{output_dir}/{video.custom_id}_{start_time_sec}_{end_time_sec}.jpg'
                print(f"Generating thumbnail to path: {thumbnail_path}")

                try:
                    generate_thumbnail(output_path, thumbnail_path, mid_time_sec)
                except Exception as e:
                    print(f"Error generating thumbnail: {e}")
                    continue

                try:
                    with open(thumbnail_path, 'rb') as thumbnail_file:
                        video_clip = VideoClip.objects.create(
                            video=video,
                            page=video.page_id,
                            clip_color=video.video_color,
                            start_time=start_checkpoint.time,
                            end_time=checkpoint.time,
                            type=checkpoint.type,
                            output_path=output_path,
                            thumbnail=ContentFile(thumbnail_file.read(), name=os.path.basename(thumbnail_path))
                        )
                        created_clips.append(video_clip)
                except Exception as e:
                    print(f"Error saving video clip: {e}")
                    continue
                start_checkpoint = None
        return Response({'status': 'Clips created', 'video_clips': VideoClipSerializer(created_clips, many=True).data})

class VideoClipViewSet(viewsets.ModelViewSet):
    queryset = VideoClip.objects.all()
    serializer_class = VideoClipSerializer

    @action(detail=False, methods=['get'])
    def by_page(self, request):
        page_id = request.query_params.get('page_id')
        if page_id:
            clips = VideoClip.objects.filter(page_id=page_id)
            serializer = VideoClipSerializer(clips, many=True)
            return Response(serializer.data)
        return Response({"error": "page_id not provided"}, status=400)

class VideoClipThumbnailsView(APIView):
    def get(self, request, page_id):
        clips = VideoClip.objects.filter(page_id=page_id)
        serializer = VideoClipThumbnailSerializer(clips, many=True)
        thumbnails = [clip['thumbnail'] for clip in serializer.data]
        return Response(thumbnails)

class VideoClipPathsView(APIView):
    def get(self, request, page_id):
        clips = VideoClip.objects.filter(page_id=page_id)
        serializer = VideoClipThumbnailSerializer(clips, many=True)
        paths = [clip['output_path'] for clip in serializer.data]
        return Response(paths)

class VideoFileView(APIView):
    def get(self, request, custom_id):
        video = get_object_or_404(Video, custom_id=custom_id)
        return Response({
            'videofile': video.videofile.url
        })

class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = Checkpoint.objects.all()
    serializer_class = CheckpointSerializer
class FrameViewSet(viewsets.ModelViewSet):
    queryset = Frame.objects.all()
    serializer_class = FrameSerializer
class HoldViewSet(viewsets.ModelViewSet):
    queryset = Hold.objects.all()
    serializer_class = HoldSerializer

class ImageUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FirstImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.save()
            image_path = image.image.path

            detections = perform_object_detection(image_path)

            save_detection_results(image.id, detections)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)