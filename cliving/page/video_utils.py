from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import *
from moviepy.video.fx.resize import resize


def generate_clip(original_video_path, start_time, end_time, output_path, width=None, height=None):
    with VideoFileClip(original_video_path) as video:
        new_clip = video.subclip(start_time, end_time)
        new_clip = new_clip.resize(newsize=(1080,1920))

        try:
            new_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                bitrate="5000k",
                ffmpeg_params=['-crf', '18', '-preset', 'veryfast']
            )
        except Exception as e:
            print(f"Error generating clip: {e}")
        finally:
            if new_clip.reader:
                new_clip.reader.close()
            if new_clip.audio and new_clip.audio.reader:
                new_clip.audio.reader.close_proc()



def generate_thumbnail(video_path, thumbnail_path, time):
    with VideoFileClip(video_path) as video:
        try:
            video.save_frame(thumbnail_path, t=time)
        except Exception as e:
            print(f"Error generating thumbnail for {video_path} at {time} seconds: {e}")
        finally:
            if video.reader:
                video.reader.close()
            if video.audio and video.audio.reader:
                video.audio.reader.close_proc()