from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import *
from moviepy.video.fx.resize import resize


def generate_clip(original_video_path, start_time, end_time, output_path, width=None, height=None):
    with VideoFileClip(original_video_path) as video:
        new_clip = video.subclip(start_time, end_time)
        new_clip = new_clip.resize(newsize=(1080,1920))

        new_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            bitrate="5000k",
            ffmpeg_params=['-crf', '18', '-preset', 'veryfast']
        )



def generate_thumbnail(video_path, thumbnail_path, time):
    with VideoFileClip(video_path) as video:
        video.save_frame(thumbnail_path, t=time)