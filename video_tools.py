import os
import subprocess
import config
from werkzeug.utils import secure_filename

# Get FFmpeg path from static-ffmpeg
try:
    from static_ffmpeg import run
    ffmpeg_path = run.get_or_download_version('latest')['ffmpeg']
except:
    ffmpeg_path = 'ffmpeg'  # Fallback to system FFmpeg

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
            self.ffmpeg, '-i', video_path,
            '-vf', f'delogo=x={x}:y={y}:w={width}:h={height}',
            '-c:a', 'copy',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_filename
    
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
            self.ffmpeg, '-ss', str(start_time), '-t', str(duration),
            '-i', video_path,
            '-vf', f'fps={fps},scale=480:-1:flags=lanczos',
            '-loop', '0',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_filename
    
    def compress_video(self, video_path, quality='medium'):
        """Compress video - quality: low, medium, high"""
        filename = os.path.basename(video_path)
        output_filename = f"compressed_{filename}"
        output_path = os.path.join(self.upload_folder, output_filename)
        
        # CRF values: lower = better quality, higher = smaller size
        crf_values = {'high': '23', 'medium': '28', 'low': '35'}
        crf = crf_values.get(quality, '28')
        
        cmd = [
            self.ffmpeg, '-i', video_path,
            '-vcodec', 'libx264',
            '-crf', crf,
            '-preset', 'fast',
            '-acodec', 'aac',
            '-b:a', '128k',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_filename
    
    def convert_format(self, video_path, output_format):
        """Convert video format - mp4, avi, mkv, mov, webm"""
        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_filename = f"{filename}.{output_format}"
        output_path = os.path.join(self.upload_folder, output_filename)
        
        cmd = [
            self.ffmpeg, '-i', video_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_filename
    
    def rotate_video(self, video_path, rotation):
        """Rotate video - 90, 180, 270 degrees or flip"""
        filename = os.path.basename(video_path)
        output_filename = f"rotated_{filename}"
        output_path = os.path.join(self.upload_folder, output_filename)
        
        # Rotation filters
        filters = {
            '90': 'transpose=1',
            '180': 'transpose=1,transpose=1',
            '270': 'transpose=2',
            'flip_h': 'hflip',
            'flip_v': 'vflip'
        }
        
        vf = filters.get(rotation, 'transpose=1')
        
        cmd = [
            self.ffmpeg, '-i', video_path,
            '-vf', vf,
            '-c:a', 'copy',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_filename
