#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
格式转换工具实用函数
提供各种文件格式之间的转换功能
"""

import os
import sys
import threading
import tempfile
import shutil
import subprocess
from typing import List, Dict, Tuple, Optional, Union, Callable, Any
from PIL import Image

class FormatConverter:
    """格式转换工具类，提供各种格式转换功能"""
    
    def __init__(self):
        """初始化格式转换工具"""
        self.ffmpeg_path = self._find_ffmpeg()
        self.temp_dir = tempfile.mkdtemp(prefix="format_converter_")
    
    def __del__(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def _find_ffmpeg(self) -> str:
        """
        查找系统中的FFmpeg可执行文件路径
        
        Returns:
            str: FFmpeg可执行文件路径，如果未找到则返回空字符串
        """
        # 尝试在系统路径中查找
        if os.name == 'nt':  # Windows系统
            for path in os.environ["PATH"].split(os.pathsep):
                ffmpeg_path = os.path.join(path, "ffmpeg.exe")
                if os.path.isfile(ffmpeg_path):
                    return ffmpeg_path
                
            # 检查常见的安装路径
            common_paths = [
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
                r"C:\ffmpeg\bin\ffmpeg.exe",
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "ffmpeg.exe")
            ]
            
            for path in common_paths:
                if os.path.isfile(path):
                    return path
        else:  # Linux/Mac系统
            for path in os.environ["PATH"].split(os.pathsep):
                ffmpeg_path = os.path.join(path, "ffmpeg")
                if os.path.isfile(ffmpeg_path) and os.access(ffmpeg_path, os.X_OK):
                    return ffmpeg_path
        
        return ""
    
    def is_ffmpeg_available(self) -> bool:
        """
        检查是否可以使用FFmpeg
        
        Returns:
            bool: 如果FFmpeg可用返回True，否则返回False
        """
        return bool(self.ffmpeg_path)
    
    def convert_mp4_to_gif(self, input_path: str, output_path: str, 
                          fps: int = 10, quality: int = 85, scale: float = 1.0,
                          start_time: float = 0, duration: float = 0,
                          progress_callback: Callable[[float], None] = None) -> bool:
        """
        将MP4视频转换为GIF动画
        
        Args:
            input_path: 输入MP4文件路径
            output_path: 输出GIF文件路径
            fps: 输出GIF帧率，默认10帧/秒
            quality: 输出GIF质量，0-100之间的整数，默认85
            scale: 输出GIF缩放比例，默认1.0(原始大小)
            start_time: 开始时间（秒），默认0
            duration: 持续时间（秒），默认0表示转换整个视频
            progress_callback: 进度回调函数，参数为0-1之间的浮点数表示进度
            
        Returns:
            bool: 转换成功返回True，失败返回False
        """
        if not self.is_ffmpeg_available():
            print("错误：未找到FFmpeg。请确保FFmpeg已安装并添加到系统路径。")
            return False
        
        if not os.path.isfile(input_path):
            print(f"错误：输入文件 {input_path} 不存在。")
            return False
        
        try:
            # 创建临时目录
            frames_dir = os.path.join(self.temp_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)
            
            # 构建FFmpeg命令参数
            cmd = [self.ffmpeg_path, "-y"]
            
            # 添加起始时间
            if start_time > 0:
                cmd.extend(["-ss", str(start_time)])
            
            # 输入文件
            cmd.extend(["-i", input_path])
            
            # 添加持续时间
            if duration > 0:
                cmd.extend(["-t", str(duration)])
            
            # 设置帧率和缩放
            filters = []
            if fps != 0:
                filters.append(f"fps={fps}")
            if scale != 1.0:
                filters.append(f"scale=iw*{scale}:ih*{scale}")
            
            if filters:
                cmd.extend(["-vf", ",".join(filters)])
            
            # 输出临时帧序列
            frames_path = os.path.join(frames_dir, "frame_%04d.png")
            cmd.append(frames_path)
            
            # 执行FFmpeg
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            
            # 读取输出以更新进度
            if progress_callback:
                progress_callback(0.1)  # 初始进度10%
            
            # 等待命令完成
            process.wait()
            
            if process.returncode != 0:
                stderr = process.stderr.read()
                print(f"FFmpeg错误: {stderr}")
                return False
            
            # 获取所有帧
            frame_files = sorted([
                os.path.join(frames_dir, f) for f in os.listdir(frames_dir)
                if f.endswith(".png")
            ])
            
            if not frame_files:
                print("错误：未能生成帧序列。")
                return False
            
            # 更新进度
            if progress_callback:
                progress_callback(0.6)  # 进度60%
            
            # 使用PIL创建GIF
            frames = []
            for i, file in enumerate(frame_files):
                img = Image.open(file)
                frames.append(img)
                
                # 更新进度
                if progress_callback and i % 10 == 0:
                    progress = 0.6 + 0.3 * (i / len(frame_files))
                    progress_callback(progress)
            
            # 保存GIF
            frames[0].save(
                output_path,
                format="GIF",
                append_images=frames[1:],
                save_all=True,
                duration=1000/fps,
                loop=0,
                optimize=True,
                quality=quality
            )
            
            # 完成
            if progress_callback:
                progress_callback(1.0)
            
            return True
            
        except Exception as e:
            print(f"转换MP4到GIF出错: {str(e)}")
            return False
        finally:
            # 清理临时文件
            frames_dir = os.path.join(self.temp_dir, "frames")
            if os.path.exists(frames_dir):
                shutil.rmtree(frames_dir)
    
    def convert_video_format(self, input_path: str, output_path: str,
                           video_codec: str = "", audio_codec: str = "",
                           video_bitrate: str = "", audio_bitrate: str = "",
                           resolution: str = "", fps: int = 0,
                           progress_callback: Callable[[float], None] = None) -> bool:
        """
        转换视频格式
        
        Args:
            input_path: 输入视频文件路径
            output_path: 输出视频文件路径
            video_codec: 视频编码器，默认使用输出格式的默认编码器
            audio_codec: 音频编码器，默认使用输出格式的默认编码器
            video_bitrate: 视频比特率，例如"1M"
            audio_bitrate: 音频比特率，例如"128k"
            resolution: 分辨率，格式为"宽x高"，例如"1280x720"
            fps: 帧率，默认0表示保持原帧率
            progress_callback: 进度回调函数
            
        Returns:
            bool: 转换成功返回True，失败返回False
        """
        if not self.is_ffmpeg_available():
            print("错误：未找到FFmpeg。请确保FFmpeg已安装并添加到系统路径。")
            return False
        
        if not os.path.isfile(input_path):
            print(f"错误：输入文件 {input_path} 不存在。")
            return False
        
        try:
            # 构建FFmpeg命令参数
            cmd = [self.ffmpeg_path, "-y", "-i", input_path]
            
            # 添加视频编码参数
            if video_codec:
                cmd.extend(["-c:v", video_codec])
            
            # 添加音频编码参数
            if audio_codec:
                cmd.extend(["-c:a", audio_codec])
            
            # 添加视频比特率
            if video_bitrate:
                cmd.extend(["-b:v", video_bitrate])
            
            # 添加音频比特率
            if audio_bitrate:
                cmd.extend(["-b:a", audio_bitrate])
            
            # 添加分辨率和帧率滤镜
            filters = []
            if resolution:
                filters.append(f"scale={resolution.replace('x', ':')}")
            if fps > 0:
                filters.append(f"fps={fps}")
            
            if filters:
                cmd.extend(["-vf", ",".join(filters)])
            
            # 输出文件
            cmd.append(output_path)
            
            # 执行FFmpeg
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            
            # 读取输出以更新进度
            if progress_callback:
                progress_callback(0.1)  # 初始进度10%
            
            # 等待命令完成
            process.wait()
            
            # 完成
            if progress_callback:
                progress_callback(1.0)
            
            if process.returncode != 0:
                stderr = process.stderr.read()
                print(f"FFmpeg错误: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"视频格式转换出错: {str(e)}")
            return False
    
    def convert_audio_format(self, input_path: str, output_path: str,
                           audio_codec: str = "", audio_bitrate: str = "",
                           sample_rate: int = 0, channels: int = 0,
                           progress_callback: Callable[[float], None] = None) -> bool:
        """
        转换音频格式
        
        Args:
            input_path: 输入音频文件路径
            output_path: 输出音频文件路径
            audio_codec: 音频编码器，默认使用输出格式的默认编码器
            audio_bitrate: 音频比特率，例如"128k"
            sample_rate: 采样率，例如44100
            channels: 声道数，例如2表示立体声
            progress_callback: 进度回调函数
            
        Returns:
            bool: 转换成功返回True，失败返回False
        """
        if not self.is_ffmpeg_available():
            print("错误：未找到FFmpeg。请确保FFmpeg已安装并添加到系统路径。")
            return False
        
        if not os.path.isfile(input_path):
            print(f"错误：输入文件 {input_path} 不存在。")
            return False
        
        try:
            # 构建FFmpeg命令参数
            cmd = [self.ffmpeg_path, "-y", "-i", input_path]
            
            # 添加音频编码参数
            if audio_codec:
                cmd.extend(["-c:a", audio_codec])
            
            # 添加音频比特率
            if audio_bitrate:
                cmd.extend(["-b:a", audio_bitrate])
            
            # 添加采样率
            if sample_rate > 0:
                cmd.extend(["-ar", str(sample_rate)])
            
            # 添加声道数
            if channels > 0:
                cmd.extend(["-ac", str(channels)])
            
            # 输出文件
            cmd.append(output_path)
            
            # 执行FFmpeg
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            
            # 读取输出以更新进度
            if progress_callback:
                progress_callback(0.1)  # 初始进度10%
            
            # 等待命令完成
            process.wait()
            
            # 完成
            if progress_callback:
                progress_callback(1.0)
            
            if process.returncode != 0:
                stderr = process.stderr.read()
                print(f"FFmpeg错误: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"音频格式转换出错: {str(e)}")
            return False
    
    def convert_image_format(self, input_path: str, output_path: str,
                           quality: int = 90, resize: Optional[Tuple[int, int]] = None,
                           rotate: int = 0, flip: bool = False, mirror: bool = False,
                           progress_callback: Callable[[float], None] = None) -> bool:
        """
        转换图片格式
        
        Args:
            input_path: 输入图片文件路径
            output_path: 输出图片文件路径
            quality: 图片质量，0-100之间的整数
            resize: 调整大小，格式为(宽, 高)的元组
            rotate: 旋转角度，正数表示顺时针旋转
            flip: 是否上下翻转
            mirror: 是否左右镜像
            progress_callback: 进度回调函数
            
        Returns:
            bool: 转换成功返回True，失败返回False
        """
        if not os.path.isfile(input_path):
            print(f"错误：输入文件 {input_path} 不存在。")
            return False
        
        try:
            if progress_callback:
                progress_callback(0.1)
            
            # 打开图片
            img = Image.open(input_path)
            
            if progress_callback:
                progress_callback(0.3)
            
            # 调整大小
            if resize:
                img = img.resize(resize, Image.LANCZOS)
            
            if progress_callback:
                progress_callback(0.5)
            
            # 旋转
            if rotate:
                img = img.rotate(-rotate, expand=True)
            
            # 翻转和镜像
            if flip:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            if mirror:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            
            if progress_callback:
                progress_callback(0.7)
            
            # 保存图片
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                img.save(output_path, quality=quality, optimize=True)
            elif output_path.lower().endswith('.png'):
                img.save(output_path, optimize=True)
            elif output_path.lower().endswith('.webp'):
                img.save(output_path, quality=quality)
            else:
                img.save(output_path)
            
            if progress_callback:
                progress_callback(1.0)
            
            return True
            
        except Exception as e:
            print(f"图片格式转换出错: {str(e)}")
            return False
    
    def extract_audio_from_video(self, input_path: str, output_path: str,
                               audio_codec: str = "", audio_bitrate: str = "",
                               progress_callback: Callable[[float], None] = None) -> bool:
        """
        从视频中提取音频
        
        Args:
            input_path: 输入视频文件路径
            output_path: 输出音频文件路径
            audio_codec: 音频编码器，默认使用输出格式的默认编码器
            audio_bitrate: 音频比特率，例如"128k"
            progress_callback: 进度回调函数
            
        Returns:
            bool: 转换成功返回True，失败返回False
        """
        if not self.is_ffmpeg_available():
            print("错误：未找到FFmpeg。请确保FFmpeg已安装并添加到系统路径。")
            return False
        
        if not os.path.isfile(input_path):
            print(f"错误：输入文件 {input_path} 不存在。")
            return False
        
        try:
            # 构建FFmpeg命令参数
            cmd = [self.ffmpeg_path, "-y", "-i", input_path, "-vn"]  # -vn表示无视频
            
            # 添加音频编码参数
            if audio_codec:
                cmd.extend(["-c:a", audio_codec])
            
            # 添加音频比特率
            if audio_bitrate:
                cmd.extend(["-b:a", audio_bitrate])
            
            # 输出文件
            cmd.append(output_path)
            
            # 执行FFmpeg
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            
            # 读取输出以更新进度
            if progress_callback:
                progress_callback(0.1)  # 初始进度10%
            
            # 等待命令完成
            process.wait()
            
            # 完成
            if progress_callback:
                progress_callback(1.0)
            
            if process.returncode != 0:
                stderr = process.stderr.read()
                print(f"FFmpeg错误: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"从视频提取音频出错: {str(e)}")
            return False
    
    def get_media_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取媒体文件信息
        
        Args:
            file_path: 媒体文件路径
            
        Returns:
            dict: 包含媒体信息的字典，出错则返回空字典
        """
        if not self.is_ffmpeg_available():
            print("错误：未找到FFmpeg。请确保FFmpeg已安装并添加到系统路径。")
            return {}
        
        if not os.path.isfile(file_path):
            print(f"错误：文件 {file_path} 不存在。")
            return {}
        
        try:
            # 使用FFprobe获取媒体信息
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
            if not os.path.isfile(ffprobe_path):
                print("错误：未找到FFprobe。")
                return {}
            
            cmd = [
                ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"FFprobe错误: {result.stderr}")
                return {}
            
            import json
            info = json.loads(result.stdout)
            
            # 提取常用信息
            media_info = {
                "format": info.get("format", {}).get("format_name", ""),
                "duration": float(info.get("format", {}).get("duration", 0)),
                "size": int(info.get("format", {}).get("size", 0)),
                "bit_rate": int(info.get("format", {}).get("bit_rate", 0)),
                "streams": []
            }
            
            # 处理音视频流信息
            for stream in info.get("streams", []):
                stream_type = stream.get("codec_type", "")
                
                if stream_type == "video":
                    stream_info = {
                        "type": "video",
                        "codec": stream.get("codec_name", ""),
                        "width": stream.get("width", 0),
                        "height": stream.get("height", 0),
                        "frame_rate": eval(stream.get("r_frame_rate", "0/1")),
                        "bit_rate": int(stream.get("bit_rate", 0))
                    }
                elif stream_type == "audio":
                    stream_info = {
                        "type": "audio",
                        "codec": stream.get("codec_name", ""),
                        "channels": stream.get("channels", 0),
                        "sample_rate": int(stream.get("sample_rate", 0)),
                        "bit_rate": int(stream.get("bit_rate", 0))
                    }
                else:
                    stream_info = {
                        "type": stream_type,
                        "codec": stream.get("codec_name", "")
                    }
                
                media_info["streams"].append(stream_info)
            
            return media_info
            
        except Exception as e:
            print(f"获取媒体信息出错: {str(e)}")
            return {}
    
    @staticmethod
    def get_supported_video_formats() -> List[str]:
        """
        获取支持的视频格式列表
        
        Returns:
            list: 支持的视频文件扩展名列表
        """
        return [
            ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v",
            ".3gp", ".mpeg", ".mpg", ".vob", ".ts", ".mts", ".m2ts"
        ]
    
    @staticmethod
    def get_supported_audio_formats() -> List[str]:
        """
        获取支持的音频格式列表
        
        Returns:
            list: 支持的音频文件扩展名列表
        """
        return [
            ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus",
            ".ac3", ".amr", ".ape", ".au", ".mid", ".midi"
        ]
    
    @staticmethod
    def get_supported_image_formats() -> List[str]:
        """
        获取支持的图片格式列表
        
        Returns:
            list: 支持的图片文件扩展名列表
        """
        return [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
            ".ico", ".svg", ".raw", ".heic", ".heif"
        ]

class VideoTimestampExtractor:
    """从视频中提取指定时间点的帧"""
    
    def __init__(self, converter: FormatConverter):
        """
        初始化视频时间戳提取器
        
        Args:
            converter: 格式转换器实例
        """
        self.converter = converter
    
    def extract_frame(self, video_path: str, output_path: str, timestamp: float) -> bool:
        """
        从视频中提取指定时间点的帧
        
        Args:
            video_path: 视频文件路径
            output_path: 输出图片路径
            timestamp: 时间点（秒）
            
        Returns:
            bool: 提取成功返回True，失败返回False
        """
        if not self.converter.is_ffmpeg_available():
            print("错误：未找到FFmpeg。请确保FFmpeg已安装并添加到系统路径。")
            return False
        
        if not os.path.isfile(video_path):
            print(f"错误：视频文件 {video_path} 不存在。")
            return False
        
        try:
            # 构建FFmpeg命令参数
            cmd = [
                self.converter.ffmpeg_path,
                "-y",
                "-ss", str(timestamp),
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "2",
                output_path
            ]
            
            # 执行FFmpeg
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                print(f"FFmpeg错误: {process.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"从视频提取帧出错: {str(e)}")
            return False
    
    def extract_frames_sequence(self, video_path: str, output_dir: str,
                               start_time: float = 0, duration: float = 0,
                               fps: int = 1, output_format: str = "jpg") -> List[str]:
        """
        从视频中提取一系列帧
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录路径
            start_time: 开始时间（秒）
            duration: 持续时间（秒），0表示到视频结束
            fps: 每秒提取的帧数
            output_format: 输出图片格式，默认jpg
            
        Returns:
            list: 输出图片路径列表，出错则返回空列表
        """
        if not self.converter.is_ffmpeg_available():
            print("错误：未找到FFmpeg。请确保FFmpeg已安装并添加到系统路径。")
            return []
        
        if not os.path.isfile(video_path):
            print(f"错误：视频文件 {video_path} 不存在。")
            return []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # 构建FFmpeg命令参数
            cmd = [self.converter.ffmpeg_path, "-y"]
            
            # 添加起始时间
            if start_time > 0:
                cmd.extend(["-ss", str(start_time)])
            
            # 输入文件
            cmd.extend(["-i", video_path])
            
            # 添加持续时间
            if duration > 0:
                cmd.extend(["-t", str(duration)])
            
            # 设置帧率
            cmd.extend(["-vf", f"fps={fps}"])
            
            # 输出帧序列
            output_pattern = os.path.join(output_dir, f"frame_%04d.{output_format}")
            cmd.append(output_pattern)
            
            # 执行FFmpeg
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                print(f"FFmpeg错误: {process.stderr}")
                return []
            
            # 获取所有输出帧
            frames = sorted([
                os.path.join(output_dir, f) for f in os.listdir(output_dir)
                if f.startswith("frame_") and f.endswith(f".{output_format}")
            ])
            
            return frames
            
        except Exception as e:
            print(f"从视频提取帧序列出错: {str(e)}")
            return [] 