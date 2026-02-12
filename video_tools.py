import os
import subprocess
import config
from werkzeug.utils import secure_filename
import logging

# Get FFmpeg path from static-ffmpeg
try:
    from static_ffmpeg import run
    ffmpeg_path = run.get_or_download_version('latest')['ffmpeg']
    logging.info(f"Using static-ffmpeg: {ffmpeg_path}")
except Exception as e:
    ffmpeg_path = 'ffmpeg'  # Fallback to system FFmpeg
    logging.warning(f"Static-ffmpeg failed, using system FFmpeg: {e}")

class VideoTools:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.ffmpeg = ffmpeg_path
        
    def remove_watermark(self, video_path, x, y, width, height):
        """Remove watermark using FFmpeg delogo filter"""
        filename = os.path.basename(video_path)
        output_filename = f"nowm_{filename}"
        output_path = os.path.join(self.upload_folder, output_filename)
        
        cmd = [
            self.ffmpeg, '-y', '-i', video_path,
            '-vf', f'delogo=x={x}:y={y}:w={width}:h={height}',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-c:a', 'copy',
            '-max_muxing_queue_size', '1024',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=180)
            return output_filename
        except subprocess.TimeoutExpired:
            raise Exception("Processing timeout - video too large for free tier")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise Exception(f"FFmpeg error: {error_msg[:200]}")
    
    def remove_tiktok_watermark(self, video_path):
        """Remove TikTok watermark (bottom center)"""
        return self.remove_watermark(video_path, x=0, y=900, width=1080, height=100)
    
    def remove_instagram_watermark(self, video_path):
        """Remove Instagram watermark (top right)"""
        return self.remove_watermark(video_path, x=900, y=0, width=180, height=80)
    
    def video_to_gif(self, video_path, start_time, duration, fps=10):
        """Convert video to GIF"""
        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_filename = f"{filename}.gif"
        output_path = os.path.join(self.upload_folder, output_filename)
        
        cmd = [
            self.ffmpeg, '-y', '-ss', str(start_time), '-t', str(duration),
            '-i', video_path,
            '-vf', f'fps={fps},scale=320:-1:flags=lanczos',
            '-loop', '0',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
            return output_filename
        except subprocess.TimeoutExpired:
            raise Exception("Processing timeout - video too large")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise Exception(f"FFmpeg error: {error_msg[:200]}")
    
    def compress_video(self, video_path, quality='medium'):
        """Compress video - quality: low, medium, high"""
        filename = os.path.basename(video_path)
        output_filename = f"compressed_{filename}"
        output_path = os.path.join(self.upload_folder, output_filename)
        
        crf_values = {'high': '23', 'medium': '28', 'low': '35'}
        crf = crf_values.get(quality, '28')
        
        cmd = [
            self.ffmpeg, '-y', '-i', video_path,
            '-vcodec', 'libx264',
            '-crf', crf,
            '-preset', 'ultrafast',
            '-acodec', 'aac',
            '-b:a', '96k',
            '-max_muxing_queue_size', '1024',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=180)
            return output_filename
        except subprocess.TimeoutExpired:
            raise Exception("Processing timeout - video too large")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise Exception(f"FFmpeg error: {error_msg[:200]}")
    
    def convert_format(self, video_path, output_format):
        """Convert video format - mp4, avi, mkv, mov, webm"""
        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_filename = f"{filename}.{output_format}"
        output_path = os.path.join(self.upload_folder, output_filename)
        
        cmd = [
            self.ffmpeg, '-y', '-i', video_path,
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-c:a', 'aac',
            '-max_muxing_queue_size', '1024',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=180)
            return output_filename
        except subprocess.TimeoutExpired:
            raise Exception("Processing timeout - video too large")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise Exception(f"FFmpeg error: {error_msg[:200]}")
    
    def rotate_video(self, video_path, rotation):
        """Rotate video - 90, 180, 270 degrees or flip"""
        filename = os.path.basename(video_path)
        output_filename = f"rotated_{filename}"
        output_path = os.path.join(self.upload_folder, output_filename)
        
        filters = {
            '90': 'transpose=1',
            '180': 'transpose=1,transpose=1',
            '270': 'transpose=2',
            'flip_h': 'hflip',
            'flip_v': 'vflip'
        }
        
        vf = filters.get(rotation, 'transpose=1')
        
        cmd = [
            self.ffmpeg, '-y', '-i', video_path,
            '-vf', vf,
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-c:a', 'copy',
            '-max_muxing_queue_size', '1024',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=180)
            return output_filename
        except subprocess.TimeoutExpired:
            raise Exception("Processing timeout - video too large")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise Exception(f"FFmpeg error: {error_msg[:200]}")
