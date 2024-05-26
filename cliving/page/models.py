from django.db import models
from django.contrib.postgres.fields import ArrayField
from moviepy.editor import VideoFileClip
from datetime import *
from django.core.files.storage import default_storage
from django.utils import timezone
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
    date = models.DateField(auto_now_add=True)
    climbing_center_name = models.CharField(max_length=20, verbose_name="name")
    bouldering_clear_color = ArrayField(models.CharField(max_length=10, choices=COLOR_CHOICES),null=True, verbose_name='bcc') #이 페이지에 어떤 색깔들의 문제를 풀었는지.
    start_time = models.TimeField(blank=True, null=True, verbose_name="start")  #암장에서 첫번째 영상을 시작한 시간
    end_time = models.TimeField(blank=True, null=True, verbose_name="end")  #암장에서 마지막 영상을 끝낸 시간(암장에서 있던 시간을 기록)
    play_time = models.IntegerField(help_text="climbing total play time in seconds", null=True, blank=True)  #영상 촬영 시간


class Video(models.Model):
    page_id = models.ForeignKey(Page, related_name="page", null=True, on_delete=models.CASCADE)
    videofile = models.FileField(upload_to='videofiles/')
    end_time = models.DateTimeField(null=True, blank=True, editable=True, verbose_name="Recording End Time")
    start_time = models.DateTimeField(verbose_name="Recording Start Time", null=True, blank=True)
    duration = models.IntegerField(help_text="Duration of the video in seconds", null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # 비디오 객체가 새로 생성되는지 여부 판단
        super().save(*args, **kwargs)  # 먼저 모델 저장하여 파일이 시스템에 확실히 쓰여지게 함

        if not self.end_time:
            self.end_time = timezone.now()
            self.save(update_fields=['end_time'])

        super(Video, self).save(*args, **kwargs)

        # 파일의 실제 저장 경로를 구하고, 해당 파일이 존재하는지 확인
        file_path = self.videofile.path
        if default_storage.exists(file_path):  # 파일 존재 여부를 확인
            try:
                with VideoFileClip(file_path) as video:
                    self.duration = int(video.duration)  # 비디오 길이 계산
                    self.start_time = self.end_time - timedelta(seconds=self.duration)  # 시작 시간 계산
                    super().save(*args, **kwargs)  # 변경된 정보를 다시 저장
            except Exception as e:
                print(f"Error processing video file {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")
        if is_new and self.end_time:
            if self.page_id.play_time is None:
                self.page_id.play_time = self.duration
            else:
                self.page_id.play_time += self.duration
            self.page_id.save()
class Checkpoint(models.Model):
    TYPE_CHOICES = [
        (0, 'start'),
        (1, 'success'),
        (2, 'fail'),
    ]
    video = models.ForeignKey(Video, related_name='checkpoints', on_delete=models.CASCADE)
    time = models.TimeField()
    type = models.IntegerField(choices=TYPE_CHOICES)

class Frame(models.Model):
    image = models.ImageField(upload_to='Frame/')

class Hold(models.Model):
    color = ArrayField(models.IntegerField(choices=COLOR_CHOICES))
    is_top = models.BooleanField(default=False, verbose_name="top")
    x1 = models.FloatField()
    x2 = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()
    frame_id = models.ForeignKey(Frame, related_name="frame", on_delete=models.CASCADE)
    
class FirstImage(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)