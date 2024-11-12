import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from moviepy.editor import VideoFileClip
from datetime import *
from django.core.files.storage import default_storage
from django.utils import timezone
from .hold_utils import perform_object_detection, save_detection_results
import os

COLOR_CHOICES = [
    ('orange', 'orange'),
    ('yellow', 'yellow'),
    ('green', 'green'),
    ('blue', 'blue'),
    ('navy', 'navy'),
    ('red', 'red'),
    ('pink', 'pink'),
    ('purple', 'purple'),
    ('grey', 'grey'),
    ('brown', 'brown'),
    ('black', 'black'),
    ('white', 'white'),
]

TYPE_CHOICES = [
        (0, 'start'),
        (1, 'success'),
        (2, 'fail'),
    ]

def time_to_seconds(time_obj):
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

def seconds_to_time(seconds):
    # datetime.timedelta 객체 생성
    time_delta = timedelta(seconds=seconds)
    # 시간, 분, 초를 계산
    hours = time_delta.seconds // 3600
    minutes = (time_delta.seconds % 3600) // 60
    seconds = time_delta.seconds % 60
    # 시간 객체로 반환
    return time(hour=hours, minute=minutes, second=seconds)

# Create your models here.


class Page(models.Model):
    date = models.CharField(max_length=6, primary_key=True, editable=False)
    date_dateFieldValue = models.DateField(auto_now_add=True, verbose_name="date_dateFieldValue")
    climbing_center_name = models.CharField(max_length=20, verbose_name="center_name")
    bouldering_clear_color = ArrayField(models.CharField(max_length=10, choices=COLOR_CHOICES),null=True, blank=True, verbose_name='bcc') #이 페이지에 어떤 색깔들의 문제를 풀었는지.
    bouldering_clear_color_counter = ArrayField(models.IntegerField(), null=True, blank =True, verbose_name ='bcc_counter') #각 색깔 카운팅
    color_success_counter = ArrayField(models.IntegerField(), null=True, blank =True, verbose_name ='success_counter')
    color_fail_counter = ArrayField(models.IntegerField(), null=True, blank =True, verbose_name ='fail_counter')
    today_start_time = models.TimeField(blank=True, null=True, verbose_name="start")  #암장에서 첫번째 영상을 시작한 시간
    today_end_time = models.TimeField(blank=True, null=True, verbose_name="end")  #암장에서 마지막 영상을 끝낸 시간(암장에서 있던 시간을 기록)
    play_time = models.IntegerField(help_text="climbing total play time in seconds", null=True, blank=True)  #영상 촬영 시간
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = datetime.now().strftime('%y%m%d')  # YYMMDD 형식으로 저장
        extracted_date = datetime.strptime(self.date, '%y%m%d').date()
        self.date_dateFieldValue = extracted_date
        super(Page, self).save(*args, **kwargs)
        Page.objects.filter(pk=self.pk).update(date_dateFieldValue=extracted_date)
    def __str__(self):
        return self.date


class Video(models.Model):
    custom_id = models.CharField(max_length=12, primary_key=True, editable=False, unique=True)
    #비디오 키입니다. 형식 ex)240622-01
    page_id = models.ForeignKey(Page, related_name="video", null=True, on_delete=models.CASCADE)
    video_color = models.CharField(max_length=12, choices=COLOR_CHOICES, null=True, blank=True, verbose_name="Color of the hold")
    videofile = models.FileField(upload_to='videofiles/')
    end_time = models.DateTimeField(null=True, blank=True, editable=True, verbose_name="Recording End Time")
    start_time = models.DateTimeField(verbose_name="Recording Start Time", null=True, blank=True)
    duration = models.IntegerField(help_text="Duration of the video in seconds", null=True, blank=True)


class VideoClip(models.Model):
    video_clip_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID 필드
    video = models.ForeignKey(Video, related_name='video_clips', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='video_clips', on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    clip_color = models.CharField(max_length=10, choices=COLOR_CHOICES, null=True, blank=True, verbose_name="Color of the hold")
    type = models.IntegerField(choices=TYPE_CHOICES)  # 예: 'start', 'success', 'fail'
    output_path = models.CharField(max_length=255)  # 클립 파일 경로
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)

class Checkpoint(models.Model):
    video = models.ForeignKey(Video, related_name='checkpoints', on_delete=models.CASCADE)
    time = models.TimeField()
    type = models.IntegerField(choices=TYPE_CHOICES)

class Frame(models.Model):
    date = models.CharField(max_length=12, primary_key=True, editable=False, unique=True)
    image = models.ImageField(upload_to='Frame/')

    
class FirstImage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)
    IMG_date = models.CharField(max_length=12, editable=False, unique=True)
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.IMG_date:
            self.IMG_date = datetime.now().strftime('%y%m%d%H%M%S')
            
        super().save(*args, **kwargs)

        detections = perform_object_detection(self.image.path)
        
        frame_instance = Frame.objects.create(image=self.image,date=self.IMG_date)
        
        holds = []
        for index, detection in enumerate(detections, start=1): 
            box = detection['box']
            hold = Hold(
                first_image=self,
                y1=box[0][0], # x1
                x1=box[0][1], # y1
                y2=box[0][2], # x2
                x2=box[0][3], # y2
                frame=frame_instance,
                index_number=index
            )
            holds.append(hold)
        
        Hold.objects.bulk_create(holds)
        
        self.update_bottom_hold(frame_instance)

    def update_bottom_hold(self, frame_instance):
        if Hold.objects.filter(first_image=self, frame=frame_instance).exists():
            Hold.objects.filter(first_image=self, frame=frame_instance).update(is_bottom=False)

            bottom_hold = Hold.objects.filter(first_image=self, frame=frame_instance).order_by('y2').last()

            if bottom_hold:
                bottom_hold.is_bottom = True
                bottom_hold.save()
                
class Hold(models.Model):
    is_top = models.BooleanField(default=False, verbose_name="top")
    is_bottom = models.BooleanField(default=False, verbose_name="bottom")
    first_image = models.ForeignKey(FirstImage, on_delete=models.CASCADE)
    y1 = models.FloatField() #  [746.5261840820312, 1198.86669921875, 1176.798095703125, 1645.9112548828125]
    y2 = models.FloatField()    
    x1 = models.FloatField()
    x2 = models.FloatField()    
    frame = models.ForeignKey(Frame, related_name="holds", on_delete=models.CASCADE)
    index_number = models.PositiveIntegerField(default=0)