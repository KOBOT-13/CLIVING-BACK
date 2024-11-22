from collections import Counter

from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Page, Video, Checkpoint, Frame, Hold, FirstImage, VideoClip
from .serializers import PageSerializer, VideoSerializer, CheckpointSerializer, FrameSerializer, HoldSerializer, \
    ColorTriesSerializer, ClimbingTimeSerializer, FirstImageSerializer, FirstImageCRUDSerializer, VideoClipSerializer, VideoClipThumbnailSerializer
from rest_framework import viewsets, status
from .video_utils import generate_clip, generate_thumbnail
from .pose_detect_utils import detect_pose
from django.db.models import Sum, Count, F
from datetime import *
from django.utils import timezone
import datetime
import os
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .hold_utils import perform_object_detection, save_detection_results
from moviepy.editor import VideoFileClip


def time_to_seconds(time_obj):
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second


class PageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PageSerializer

    def get_queryset(self):
        return Page.objects.filter(user=self.request.user)


class AllPagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, year):
        # 'date' 필드가 YYMMDD 형식이므로 year를 기반으로 필터링
        specific_year = f'{year}'
        pages = Page.objects.filter(user=self.request.user, date__startswith=specific_year)
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SpecificMonthClimbingTimeView(APIView): # 특정 달 클라이밍 시간 get (1월 ~12월 반복 불러오기로 사용하면 될 듯 함)
    permission_classes = [IsAuthenticated]

    def get(self, request, year, month):
        # 입력 받은 연월을 YYMM 형태로 포맷팅
        specific_month = f'{year}{month:02d}'
        total_time = Page.objects.filter(user=self.request.user, date__startswith=specific_month).aggregate(total_time=Sum('play_time'))
        # 플레이 시간이 없는 경우 0으로 반환
        total_time = total_time['total_time'] if total_time['total_time'] is not None else 0

        serializer = ClimbingTimeSerializer({
            'year': year,
            'month': month,
            'total_climbing_time': total_time
        })
        return Response(serializer.data)


class SpecificAnnualClimbingTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, year):
        specific_year = f'{year}'
        total_time = Page.objects.filter(user=self.request.user, date__startswith=specific_year).aggregate(total_time=Sum('play_time'))
        total_time = total_time['total_time'] if total_time['total_time'] is not None else 0

        serializer = ClimbingTimeSerializer({
            'year': year,
            'total_climbing_time': total_time
        })
        return Response(serializer.data)


# 이번달 클라이밍 시간 뷰
# 삭제 예정
class MonthlyClimbingTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_month = timezone.now().strftime('%y%m')
        total_time = Page.objects.filter(user=self.request.user, date__startswith=current_month).aggregate(total_time=Sum('play_time'))
        total_time = total_time['total_time'] if total_time['total_time'] is not None else 0

        # 시리얼라이저를 사용하여 데이터 포맷
        serializer = ClimbingTimeSerializer({
            'year': current_month[:2],
            'month': current_month[2:],
            'total_climbing_time': total_time
        })
        return Response(serializer.data)


# 올해 클라이밍 시간 뷰... 인데 특정년도가 필요하지 올해 클라이밍 시간 뷰가 필요한가??
# 삭제 예정
class AnnualClimbingTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_year = timezone.now().strftime('%y')
        total_time = Page.objects.filter(user= self.request.user, date__startswith=current_year).aggregate(total_time=Sum('play_time'))
        total_time = total_time['total_time'] if total_time['total_time'] is not None else 0

        # 시리얼라이저를 사용하여 데이터 포맷
        serializer = ClimbingTimeSerializer({
            'year': current_year,
            'total_climbing_time': total_time
        })
        return Response(serializer.data)


class SpecificMonthColorTriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, year, month):
        specific_month = f'{year}{month:02d}'
        monthly_pages = Page.objects.filter(user=self.request.user, date__startswith=specific_month)

        color_counter = Counter()

        for page in monthly_pages:
            if page.bouldering_clear_color and page.bouldering_clear_color_counter:
                for color, count in zip(page.bouldering_clear_color, page.bouldering_clear_color_counter):
                    color_counter[color] += count

        results = [ColorTriesSerializer({'color': color, 'tries': count}).data for color, count in
                   color_counter.items()]

        return Response(results)


class SpecificAnnualColorTriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, year):
        # user = request.user
        specific_year = f'{year}'
        yearly_pages = Page.objects.filter(user=self.request.user, date__startswith=specific_year)

        color_counter = Counter()

        for page in yearly_pages:
            if page.bouldering_clear_color and page.bouldering_clear_color_counter:
                for color, count in zip(page.bouldering_clear_color, page.bouldering_clear_color_counter):
                    color_counter[color] += count

        results = [ColorTriesSerializer({'color': color, 'tries': count}).data for color, count in
                   color_counter.items()]

        return Response(results)


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def create(self, request, *args, **kwargs):
        video_file = request.FILES.get('videofile')
        page_id = request.data.get('page_id')
        video_color = request.data.get('video_color')
        # end_time = timezone.now()
        end_time = datetime.datetime.now()
        with VideoFileClip(video_file.temporary_file_path()) as video:
            duration = int(video.duration)  # 비디오 길이 계산
            start_time = end_time - timedelta(seconds=duration)  # 시작 시간 계산
        page = Page.objects.get(date=page_id)

        if not page.bouldering_clear_color:
            page.bouldering_clear_color = []
            page.bouldering_clear_color_counter = []
            page.color_success_counter = []
            page.color_fail_counter = []

        if video_color not in page.bouldering_clear_color:
            page.bouldering_clear_color.append(video_color)
            page.bouldering_clear_color_counter.append(0)
            page.color_success_counter.append(0)
            page.color_fail_counter.append(0)
            this_color_index = page.bouldering_clear_color.index(video_color)


        if page.today_start_time is None:
            page.today_start_time = start_time  # 첫번째 영상을 시작한 시간

        page.today_end_time = end_time  # 마지막 영상을 끝낸 시간

        if page.play_time is None:
            page.play_time = duration
        else:
            page.play_time += duration
        page.save(update_fields=['play_time', 'bouldering_clear_color','bouldering_clear_color_counter',\
                  'color_success_counter','color_fail_counter', 'today_start_time', 'today_end_time'])

        date_str = page_id
        count = Video.objects.filter(custom_id__startswith=date_str).count() + 1
        sequence_str = f'{count:02d}'  # 두 자리 숫자 (01, 02, ...)
        custom_id = f'{date_str}-{sequence_str}'

        video = Video.objects.create(
            custom_id=custom_id,
            videofile=video_file,
            page_id=page,
            video_color=video_color,
            end_time=end_time,
            start_time=start_time,
            duration=duration
        )

        return Response({'message': 'Video uploaded successfully', 'custom_id': custom_id}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def create_checkpoint(self, request, pk=None):
        try:
            video = self.get_object()
        except Video.DoesNotExist:
            return Response({'error': 'Invalid video ID'}, status=status.HTTP_400_BAD_REQUEST)

        result = detect_pose(video)

        return Response(result, status=status.HTTP_200_OK)

    @action(detail = True, methods = ['post'])
    def create_clip(self, request, pk=None):
        video = self.get_object()
        checkpoints = video.checkpoints.order_by('time') #체크포인트를 시간순으로 정렬
        page = Page.objects.get(date=video.page_id)

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

                this_color_index = page.bouldering_clear_color.index(video.video_color)

                page.bouldering_clear_color_counter[this_color_index] += 1
                if(checkpoint.type == 1):
                    page.color_success_counter[this_color_index] += 1
                elif(checkpoint.type == 2):
                    page.color_fail_counter[this_color_index] += 1
                page.save(update_fields=['bouldering_clear_color_counter','color_success_counter', 'color_fail_counter'])

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

class VideoClipColorsView(APIView):
    def get(self, request, page_id):
        clips = VideoClip.objects.filter(page_id=page_id)
        serializer = VideoClipThumbnailSerializer(clips, many=True)
        color = [clip['clip_color'] for clip in serializer.data]
        return Response(color)

class VideoClipTypesView(APIView):
    def get(self, request, page_id):
        clips = VideoClip.objects.filter(page_id=page_id)
        serializer = VideoClipThumbnailSerializer(clips, many=True)
        type = [clip['type'] for clip in serializer.data]
        return Response(type)

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
    def first_image_and_index_number(self, request, first_image=None, index_number=None):
        try:
            hold = Hold.objects.get(first_image_id=first_image, index_number=index_number)
            serializer = HoldSerializer(hold)
            return Response(serializer.data)
        except Hold.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        
    def put(self, request, first_image=None, index_number=None):
        try:
            hold = Hold.objects.get(first_image_id=first_image, index_number=index_number)
            hold.is_top = True
            hold.save()
            serializer = HoldSerializer(hold)
            return Response(serializer.data)
        except Hold.DoesNotExist:
            return Response({'error': 'Hold not found'}, status=status.HTTP_404_NOT_FOUND)
        
    def start_hold(self, request, first_image=None, index_number=None):
        try:
            hold = Hold.objects.get(first_image_id=first_image, index_number=index_number)
            hold.is_start = True
            hold.save()
            serializer = HoldSerializer(hold)
            return Response(serializer.data)
        except Hold.DoesNotExist:
            return Response({'error': 'Hold not found'}, status=status.HTTP_404_NOT_FOUND)

class FirstImageView(viewsets.ModelViewSet):
    queryset = FirstImage.objects.all()
    serializer_class = FirstImageCRUDSerializer
    
    
class ImageUploadView(APIView):
    serializer_class = FirstImageSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = FirstImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.save()
            image_path = image.image.path
            detections, width, height = perform_object_detection(image_path)
            save_detection_results(image.id, detections)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)