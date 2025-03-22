#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
格式转换工具主界面
提供用户友好的界面来进行各种文件格式转换
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import time
from typing import Dict, List, Any, Callable, Optional, Union, Tuple

# 导入工具类
from .utils import FormatConverter, VideoTimestampExtractor

class FormatConverterApp:
    """格式转换工具主应用程序类"""
    
    def __init__(self, root: tk.Tk):
        """
        初始化格式转换工具应用程序
        
        Args:
            root: Tkinter根窗口对象
        """
        self.root = root
        self.root.title("格式转换工具by道相 抖音@慈悲剪辑")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # 设置图标
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # 初始化格式转换器
        self.converter = FormatConverter()
        self.timestamp_extractor = VideoTimestampExtractor(self.converter)
        
        # 一些状态变量
        self.current_tab = None
        self.conversion_thread = None
        self.is_converting = False
        
        # 输入和输出文件路径
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        
        # 创建UI元素
        self._create_widgets()
        self._bind_events()
        
        # 显示FFmpeg状态
        self._check_ffmpeg_status()
    
    def _create_widgets(self):
        """创建UI部件"""
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建顶部框架（输入和输出文件选择）
        self.top_frame = ttk.LabelFrame(self.main_frame, text="文件选择")
        self.top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 输入文件选择
        ttk.Label(self.top_frame, text="输入文件:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.input_entry = ttk.Entry(self.top_frame, textvariable=self.input_file, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.browse_input_btn = ttk.Button(self.top_frame, text="浏览...", command=self._browse_input_file)
        self.browse_input_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 输出文件选择
        ttk.Label(self.top_frame, text="输出文件:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_entry = ttk.Entry(self.top_frame, textvariable=self.output_file, width=50)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.browse_output_btn = ttk.Button(self.top_frame, text="浏览...", command=self._browse_output_file)
        self.browse_output_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # 配置列权重
        self.top_frame.columnconfigure(1, weight=1)
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 视频到GIF选项卡
        self.video_to_gif_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.video_to_gif_tab, text="视频转GIF")
        self._create_video_to_gif_tab()
        
        # 视频格式转换选项卡
        self.video_format_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.video_format_tab, text="视频格式转换")
        self._create_video_format_tab()
        
        # 音频格式转换选项卡
        self.audio_format_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.audio_format_tab, text="音频格式转换")
        self._create_audio_format_tab()
        
        # 图片格式转换选项卡
        self.image_format_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.image_format_tab, text="图片格式转换")
        self._create_image_format_tab()
        
        # 视频提取音频选项卡
        self.extract_audio_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.extract_audio_tab, text="提取音频")
        self._create_extract_audio_tab()
        
        # 视频提取帧选项卡
        self.extract_frames_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.extract_frames_tab, text="提取视频帧")
        self._create_extract_frames_tab()
        
        # 创建底部框架
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 状态标签
        self.status_label = ttk.Label(self.bottom_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)
        
        # FFmpeg状态标签
        self.ffmpeg_status_label = ttk.Label(self.bottom_frame, text="检查FFmpeg...")
        self.ffmpeg_status_label.pack(side=tk.RIGHT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.bottom_frame, 
            variable=self.progress_var, 
            mode='determinate',
            length=200
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=10)
        
        # 转换按钮
        self.convert_btn = ttk.Button(self.bottom_frame, text="开始转换", command=self._start_conversion)
        self.convert_btn.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮（初始禁用）
        self.cancel_btn = ttk.Button(self.bottom_frame, text="取消", command=self._cancel_conversion, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def _bind_events(self):
        """绑定事件处理器"""
        # 选项卡切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # 关闭窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _check_ffmpeg_status(self):
        """检查FFmpeg状态并更新UI"""
        if self.converter.is_ffmpeg_available():
            self.ffmpeg_status_label.config(text=f"FFmpeg可用: {self.converter.ffmpeg_path}")
        else:
            self.ffmpeg_status_label.config(text="警告: FFmpeg未安装或未找到")
            messagebox.showwarning(
                "FFmpeg未找到",
                "未能找到FFmpeg，部分功能将无法使用。\n\n"
                "请安装FFmpeg并确保其在系统PATH中，或将其放在程序同一目录下。"
            )
    
    def _create_video_to_gif_tab(self):
        """创建视频转GIF选项卡"""
        frame = ttk.Frame(self.video_to_gif_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # FPS设置
        ttk.Label(frame, text="帧率 (FPS):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.fps_var = tk.IntVar(value=10)
        fps_spinbox = ttk.Spinbox(frame, from_=1, to=60, textvariable=self.fps_var, width=10)
        fps_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 质量设置
        ttk.Label(frame, text="质量 (1-100):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.quality_var = tk.IntVar(value=85)
        quality_spinbox = ttk.Spinbox(frame, from_=1, to=100, textvariable=self.quality_var, width=10)
        quality_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 缩放比例
        ttk.Label(frame, text="缩放比例:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.scale_var = tk.DoubleVar(value=1.0)
        scale_combobox = ttk.Combobox(frame, textvariable=self.scale_var, values=[0.25, 0.5, 0.75, 1.0, 1.5, 2.0], width=10)
        scale_combobox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 起始时间
        ttk.Label(frame, text="起始时间 (秒):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_time_var = tk.DoubleVar(value=0)
        start_time_spinbox = ttk.Spinbox(frame, from_=0, to=9999, increment=0.5, textvariable=self.start_time_var, width=10)
        start_time_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 持续时间
        ttk.Label(frame, text="持续时间 (秒, 0=全部):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.duration_var = tk.DoubleVar(value=0)
        duration_spinbox = ttk.Spinbox(frame, from_=0, to=9999, increment=0.5, textvariable=self.duration_var, width=10)
        duration_spinbox.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 配置列权重
        frame.columnconfigure(1, weight=1)
    
    def _create_video_format_tab(self):
        """创建视频格式转换选项卡"""
        frame = ttk.Frame(self.video_format_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 视频编码选择
        ttk.Label(frame, text="视频编码:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.video_codec_var = tk.StringVar()
        video_codec_combobox = ttk.Combobox(frame, textvariable=self.video_codec_var, width=15)
        video_codec_combobox['values'] = ["", "libx264", "libx265", "h264_nvenc", "hevc_nvenc", "mpeg4", "libvpx", "libvpx-vp9"]
        video_codec_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(留空使用默认编码)").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 音频编码选择
        ttk.Label(frame, text="音频编码:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.audio_codec_var = tk.StringVar()
        audio_codec_combobox = ttk.Combobox(frame, textvariable=self.audio_codec_var, width=15)
        audio_codec_combobox['values'] = ["", "aac", "libmp3lame", "libvorbis", "libopus", "copy"]
        audio_codec_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(留空使用默认编码)").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 视频比特率
        ttk.Label(frame, text="视频比特率:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.video_bitrate_var = tk.StringVar()
        video_bitrate_combobox = ttk.Combobox(frame, textvariable=self.video_bitrate_var, width=15)
        video_bitrate_combobox['values'] = ["", "500k", "1M", "2M", "5M", "10M", "20M"]
        video_bitrate_combobox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(留空使用默认比特率)").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 音频比特率
        ttk.Label(frame, text="音频比特率:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.audio_bitrate_var = tk.StringVar()
        audio_bitrate_combobox = ttk.Combobox(frame, textvariable=self.audio_bitrate_var, width=15)
        audio_bitrate_combobox['values'] = ["", "64k", "128k", "192k", "256k", "320k"]
        audio_bitrate_combobox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(留空使用默认比特率)").grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 分辨率
        ttk.Label(frame, text="分辨率:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.resolution_var = tk.StringVar()
        resolution_combobox = ttk.Combobox(frame, textvariable=self.resolution_var, width=15)
        resolution_combobox['values'] = ["", "640x480", "1280x720", "1920x1080", "3840x2160"]
        resolution_combobox.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(留空保持原始分辨率)").grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 帧率
        ttk.Label(frame, text="帧率:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.video_fps_var = tk.IntVar(value=0)
        fps_spinbox = ttk.Spinbox(frame, from_=0, to=120, textvariable=self.video_fps_var, width=15)
        fps_spinbox.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(0 = 保持原始帧率)").grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 配置列权重
        frame.columnconfigure(2, weight=1)
    
    def _create_audio_format_tab(self):
        """创建音频格式转换选项卡"""
        frame = ttk.Frame(self.audio_format_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 音频编码选择
        ttk.Label(frame, text="音频编码:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.audio_only_codec_var = tk.StringVar()
        audio_codec_combobox = ttk.Combobox(frame, textvariable=self.audio_only_codec_var, width=15)
        audio_codec_combobox['values'] = ["", "aac", "libmp3lame", "libvorbis", "libopus", "flac", "pcm_s16le"]
        audio_codec_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(留空使用默认编码)").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 音频比特率
        ttk.Label(frame, text="音频比特率:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.audio_only_bitrate_var = tk.StringVar()
        audio_bitrate_combobox = ttk.Combobox(frame, textvariable=self.audio_only_bitrate_var, width=15)
        audio_bitrate_combobox['values'] = ["", "64k", "128k", "192k", "256k", "320k"]
        audio_bitrate_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(留空使用默认比特率)").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 采样率
        ttk.Label(frame, text="采样率 (Hz):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.sample_rate_var = tk.IntVar(value=0)
        sample_rate_combobox = ttk.Combobox(frame, textvariable=self.sample_rate_var, width=15)
        sample_rate_combobox['values'] = [0, 8000, 11025, 22050, 44100, 48000, 96000]
        sample_rate_combobox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(0 = 保持原始采样率)").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 声道数
        ttk.Label(frame, text="声道数:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.channels_var = tk.IntVar(value=0)
        channels_combobox = ttk.Combobox(frame, textvariable=self.channels_var, width=15)
        channels_combobox['values'] = [0, 1, 2]
        channels_combobox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(0 = 保持原始声道数, 1 = 单声道, 2 = 立体声)").grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 配置列权重
        frame.columnconfigure(2, weight=1)
    
    def _create_image_format_tab(self):
        """创建图片格式转换选项卡"""
        frame = ttk.Frame(self.image_format_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 质量设置
        ttk.Label(frame, text="质量 (1-100):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.image_quality_var = tk.IntVar(value=90)
        image_quality_spinbox = ttk.Spinbox(frame, from_=1, to=100, textvariable=self.image_quality_var, width=10)
        image_quality_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 调整大小
        ttk.Label(frame, text="调整大小:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 宽度
        self.resize_frame = ttk.Frame(frame)
        self.resize_frame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(self.resize_frame, text="宽度:").pack(side=tk.LEFT, padx=2)
        self.width_var = tk.IntVar(value=0)
        width_spinbox = ttk.Spinbox(self.resize_frame, from_=0, to=10000, textvariable=self.width_var, width=6)
        width_spinbox.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(self.resize_frame, text="高度:").pack(side=tk.LEFT, padx=2)
        self.height_var = tk.IntVar(value=0)
        height_spinbox = ttk.Spinbox(self.resize_frame, from_=0, to=10000, textvariable=self.height_var, width=6)
        height_spinbox.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(self.resize_frame, text="(0 = 保持原始尺寸)").pack(side=tk.LEFT, padx=2)
        
        # 旋转角度
        ttk.Label(frame, text="旋转角度:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.rotation_var = tk.IntVar(value=0)
        rotation_combobox = ttk.Combobox(frame, textvariable=self.rotation_var, width=10)
        rotation_combobox['values'] = [0, 90, 180, 270]
        rotation_combobox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 翻转选项
        ttk.Label(frame, text="翻转选项:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.flip_var = tk.BooleanVar(value=False)
        self.flip_check = ttk.Checkbutton(frame, text="上下翻转", variable=self.flip_var)
        self.flip_check.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.mirror_var = tk.BooleanVar(value=False)
        self.mirror_check = ttk.Checkbutton(frame, text="左右镜像", variable=self.mirror_var)
        self.mirror_check.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 配置列权重
        frame.columnconfigure(2, weight=1)
    
    def _create_extract_audio_tab(self):
        """创建提取音频选项卡"""
        frame = ttk.Frame(self.extract_audio_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 音频编码选择
        ttk.Label(frame, text="音频编码:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.extract_audio_codec_var = tk.StringVar()
        audio_codec_combobox = ttk.Combobox(frame, textvariable=self.extract_audio_codec_var, width=15)
        audio_codec_combobox['values'] = ["", "aac", "libmp3lame", "libvorbis", "libopus", "flac", "pcm_s16le"]
        audio_codec_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(留空使用默认编码)").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 音频比特率
        ttk.Label(frame, text="音频比特率:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.extract_audio_bitrate_var = tk.StringVar()
        audio_bitrate_combobox = ttk.Combobox(frame, textvariable=self.extract_audio_bitrate_var, width=15)
        audio_bitrate_combobox['values'] = ["", "64k", "128k", "192k", "256k", "320k"]
        audio_bitrate_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(frame, text="(留空使用默认比特率)").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 提示信息
        ttk.Label(frame, text="将从视频文件中提取音频轨道，不包含视频内容").grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        # 配置列权重
        frame.columnconfigure(2, weight=1)
    
    def _create_extract_frames_tab(self):
        """创建提取视频帧选项卡"""
        frame = ttk.Frame(self.extract_frames_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 选择输出目录
        ttk.Label(frame, text="输出目录:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_dir_var = tk.StringVar()
        output_dir_entry = ttk.Entry(frame, textvariable=self.output_dir_var, width=50)
        output_dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        browse_output_dir_btn = ttk.Button(frame, text="浏览...", command=self._browse_output_dir)
        browse_output_dir_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 抽取模式
        ttk.Label(frame, text="抽取模式:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.extract_mode_var = tk.StringVar(value="单帧")
        extract_mode_radio1 = ttk.Radiobutton(frame, text="单帧", variable=self.extract_mode_var, value="单帧", command=self._update_extract_frames_ui)
        extract_mode_radio1.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        extract_mode_radio2 = ttk.Radiobutton(frame, text="多帧序列", variable=self.extract_mode_var, value="多帧序列", command=self._update_extract_frames_ui)
        extract_mode_radio2.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 单帧参数框架
        self.single_frame_frame = ttk.LabelFrame(frame, text="单帧参数")
        self.single_frame_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
        
        # 时间点
        ttk.Label(self.single_frame_frame, text="时间点 (秒):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.timestamp_var = tk.DoubleVar(value=0)
        timestamp_spinbox = ttk.Spinbox(self.single_frame_frame, from_=0, to=9999, increment=0.1, textvariable=self.timestamp_var, width=10)
        timestamp_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 多帧参数框架
        self.multi_frame_frame = ttk.LabelFrame(frame, text="多帧序列参数")
        self.multi_frame_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
        
        # 起始时间
        ttk.Label(self.multi_frame_frame, text="起始时间 (秒):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.frame_start_time_var = tk.DoubleVar(value=0)
        frame_start_time_spinbox = ttk.Spinbox(self.multi_frame_frame, from_=0, to=9999, increment=0.5, textvariable=self.frame_start_time_var, width=10)
        frame_start_time_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 持续时间
        ttk.Label(self.multi_frame_frame, text="持续时间 (秒, 0=全部):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.frame_duration_var = tk.DoubleVar(value=0)
        frame_duration_spinbox = ttk.Spinbox(self.multi_frame_frame, from_=0, to=9999, increment=0.5, textvariable=self.frame_duration_var, width=10)
        frame_duration_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 抽取帧率
        ttk.Label(self.multi_frame_frame, text="抽取帧率 (每秒):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.extract_fps_var = tk.DoubleVar(value=1)
        extract_fps_spinbox = ttk.Spinbox(self.multi_frame_frame, from_=0.1, to=30, increment=0.1, textvariable=self.extract_fps_var, width=10)
        extract_fps_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 输出格式
        ttk.Label(self.multi_frame_frame, text="输出格式:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_format_var = tk.StringVar(value="jpg")
        output_format_combobox = ttk.Combobox(self.multi_frame_frame, textvariable=self.output_format_var, width=10)
        output_format_combobox['values'] = ["jpg", "png", "bmp", "webp"]
        output_format_combobox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 初始化UI状态
        self._update_extract_frames_ui()
        
        # 配置列权重
        frame.columnconfigure(1, weight=1)
    
    def _update_extract_frames_ui(self):
        """根据当前选择的提取模式更新UI状态"""
        mode = self.extract_mode_var.get()
        
        if mode == "单帧":
            self.single_frame_frame.grid()
            self.multi_frame_frame.grid_remove()
        else:  # 多帧序列
            self.single_frame_frame.grid_remove()
            self.multi_frame_frame.grid()
    
    def _browse_input_file(self):
        """浏览并选择输入文件"""
        current_tab = self.notebook.index(self.notebook.select())
        
        filetypes = []
        if current_tab == 0:  # 视频转GIF
            filetypes = [("视频文件", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm")]
        elif current_tab == 1:  # 视频格式转换
            filetypes = [("视频文件", "*" + " *".join(self.converter.get_supported_video_formats()))]
        elif current_tab == 2:  # 音频格式转换
            filetypes = [("音频文件", "*" + " *".join(self.converter.get_supported_audio_formats()))]
        elif current_tab == 3:  # 图片格式转换
            filetypes = [("图片文件", "*" + " *".join(self.converter.get_supported_image_formats()))]
        elif current_tab == 4:  # 提取音频
            filetypes = [("视频文件", "*" + " *".join(self.converter.get_supported_video_formats()))]
        elif current_tab == 5:  # 提取视频帧
            filetypes = [("视频文件", "*" + " *".join(self.converter.get_supported_video_formats()))]
        
        filetypes.append(("所有文件", "*.*"))
        
        filepath = filedialog.askopenfilename(
            title="选择输入文件",
            filetypes=filetypes
        )
        
        if filepath:
            self.input_file.set(filepath)
            # 根据输入文件自动生成输出文件路径
            self._suggest_output_file(filepath)
    
    def _browse_output_file(self):
        """浏览并选择输出文件"""
        current_tab = self.notebook.index(self.notebook.select())
        
        filetypes = []
        defaultext = ""
        
        if current_tab == 0:  # 视频转GIF
            filetypes = [("GIF图片", "*.gif")]
            defaultext = ".gif"
        elif current_tab == 1:  # 视频格式转换
            filetypes = [
                ("MP4视频", "*.mp4"), 
                ("AVI视频", "*.avi"), 
                ("MKV视频", "*.mkv"), 
                ("MOV视频", "*.mov"), 
                ("WebM视频", "*.webm"),
                ("所有视频文件", "*" + " *".join(self.converter.get_supported_video_formats()))
            ]
            defaultext = ".mp4"
        elif current_tab == 2:  # 音频格式转换
            filetypes = [
                ("MP3音频", "*.mp3"), 
                ("WAV音频", "*.wav"), 
                ("FLAC音频", "*.flac"), 
                ("AAC音频", "*.aac"), 
                ("OGG音频", "*.ogg"),
                ("所有音频文件", "*" + " *".join(self.converter.get_supported_audio_formats()))
            ]
            defaultext = ".mp3"
        elif current_tab == 3:  # 图片格式转换
            filetypes = [
                ("JPEG图片", "*.jpg *.jpeg"), 
                ("PNG图片", "*.png"), 
                ("BMP图片", "*.bmp"), 
                ("WebP图片", "*.webp"),
                ("所有图片文件", "*" + " *".join(self.converter.get_supported_image_formats()))
            ]
            defaultext = ".jpg"
        elif current_tab == 4:  # 提取音频
            filetypes = [
                ("MP3音频", "*.mp3"), 
                ("WAV音频", "*.wav"), 
                ("FLAC音频", "*.flac"), 
                ("AAC音频", "*.aac"), 
                ("OGG音频", "*.ogg"),
                ("所有音频文件", "*" + " *".join(self.converter.get_supported_audio_formats()))
            ]
            defaultext = ".mp3"
        
        # 如果是提取视频帧，则不需要这个按钮
        if current_tab == 5:  # 提取视频帧
            return
        
        filepath = filedialog.asksaveasfilename(
            title="选择输出文件",
            filetypes=filetypes,
            defaultextension=defaultext
        )
        
        if filepath:
            self.output_file.set(filepath)
    
    def _browse_output_dir(self):
        """浏览并选择输出目录"""
        directory = filedialog.askdirectory(
            title="选择输出目录"
        )
        
        if directory:
            self.output_dir_var.set(directory)
    
    def _suggest_output_file(self, input_filepath):
        """根据输入文件路径自动生成输出文件路径"""
        if not input_filepath:
            return
        
        current_tab = self.notebook.index(self.notebook.select())
        
        # 获取输入文件的目录和基本名称（不含扩展名）
        dirname = os.path.dirname(input_filepath)
        basename = os.path.splitext(os.path.basename(input_filepath))[0]
        
        output_filepath = ""
        
        if current_tab == 0:  # 视频转GIF
            output_filepath = os.path.join(dirname, basename + ".gif")
        elif current_tab == 1:  # 视频格式转换
            output_filepath = os.path.join(dirname, basename + "_converted.mp4")
        elif current_tab == 2:  # 音频格式转换
            output_filepath = os.path.join(dirname, basename + "_converted.mp3")
        elif current_tab == 3:  # 图片格式转换
            output_filepath = os.path.join(dirname, basename + "_converted.jpg")
        elif current_tab == 4:  # 提取音频
            output_filepath = os.path.join(dirname, basename + "_audio.mp3")
        elif current_tab == 5:  # 提取视频帧
            # 对于视频帧，设置默认输出目录
            output_dir = os.path.join(dirname, basename + "_frames")
            self.output_dir_var.set(output_dir)
            return
        
        self.output_file.set(output_filepath)
    
    def _on_tab_changed(self, event):
        """选项卡切换事件处理器"""
        # 获取当前选中的选项卡索引
        current_tab = self.notebook.index(self.notebook.select())
        self.current_tab = current_tab
        
        # 重置输入和输出文件路径
        input_file = self.input_file.get()
        if input_file:
            self._suggest_output_file(input_file)
        
        # 特殊处理提取视频帧选项卡
        if current_tab == 5:  # 提取视频帧
            self.output_entry.grid_remove()
            self.browse_output_btn.grid_remove()
            ttk.Label(self.top_frame, text="输出文件:").grid_remove()
        else:
            self.output_entry.grid()
            self.browse_output_btn.grid()
            ttk.Label(self.top_frame, text="输出文件:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    
    def _on_close(self):
        """窗口关闭事件处理器"""
        # 取消正在进行的转换
        if self.is_converting:
            self._cancel_conversion()
        
        # 关闭窗口
        self.root.destroy()

    def _start_conversion(self):
        """开始转换"""
        # 检查输入文件是否存在
        input_file = self.input_file.get()
        if not input_file or not os.path.isfile(input_file):
            messagebox.showerror("错误", "请选择有效的输入文件")
            return
        
        # 获取当前选中的选项卡
        current_tab = self.notebook.index(self.notebook.select())
        
        # 提取视频帧需要检查输出目录
        if current_tab == 5:  # 提取视频帧
            output_dir = self.output_dir_var.get()
            if not output_dir:
                messagebox.showerror("错误", "请选择输出目录")
                return
                
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
        else:
            # 其他选项卡需要检查输出文件
            output_file = self.output_file.get()
            if not output_file:
                messagebox.showerror("错误", "请指定输出文件")
                return
                
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
        
        # 如果已经在转换中，则不再触发新的转换任务
        if self.is_converting:
            return
        
        # 禁用转换按钮，启用取消按钮
        self.convert_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        
        # 设置状态和进度条
        self.is_converting = True
        self.progress_var.set(0)
        self.status_label.config(text="正在转换...")
        
        # 根据不同选项卡启动不同的转换任务
        if current_tab == 0:  # 视频转GIF
            self.conversion_thread = threading.Thread(
                target=self._convert_video_to_gif_task, 
                args=(input_file, self.output_file.get())
            )
        elif current_tab == 1:  # 视频格式转换
            self.conversion_thread = threading.Thread(
                target=self._convert_video_format_task, 
                args=(input_file, self.output_file.get())
            )
        elif current_tab == 2:  # 音频格式转换
            self.conversion_thread = threading.Thread(
                target=self._convert_audio_format_task, 
                args=(input_file, self.output_file.get())
            )
        elif current_tab == 3:  # 图片格式转换
            self.conversion_thread = threading.Thread(
                target=self._convert_image_format_task, 
                args=(input_file, self.output_file.get())
            )
        elif current_tab == 4:  # 提取音频
            self.conversion_thread = threading.Thread(
                target=self._extract_audio_task, 
                args=(input_file, self.output_file.get())
            )
        elif current_tab == 5:  # 提取视频帧
            mode = self.extract_mode_var.get()
            if mode == "单帧":
                self.conversion_thread = threading.Thread(
                    target=self._extract_single_frame_task, 
                    args=(input_file, self.output_dir_var.get())
                )
            else:  # 多帧序列
                self.conversion_thread = threading.Thread(
                    target=self._extract_frames_sequence_task, 
                    args=(input_file, self.output_dir_var.get())
                )
        
        # 启动线程
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
    
    def _cancel_conversion(self):
        """取消转换"""
        if self.is_converting:
            self.is_converting = False
            self.status_label.config(text="已取消转换")
            
            # 由于我们直接结束线程可能会导致资源泄漏，我们通过标志位来控制
            # 让转换任务自己检查标志位并正常退出
            # 线程会在下一个检查点通过self.is_converting检测到取消信号
            
            # 禁用取消按钮，启用转换按钮
            self.cancel_btn.config(state=tk.DISABLED)
            self.convert_btn.config(state=tk.NORMAL)
    
    def _update_progress(self, progress):
        """更新进度条和UI"""
        if not self.is_converting:
            return
        
        # 更新进度条，确保进度值在0-1之间
        progress = max(0, min(1, progress))
        self.progress_var.set(progress * 100)
        
        # 更新UI
        self.root.update_idletasks()
    
    def _conversion_completed(self, success=True, error_message=""):
        """转换完成后的处理"""
        self.is_converting = False
        
        # 启用转换按钮，禁用取消按钮
        self.convert_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        
        # 更新状态和进度条
        if success:
            self.status_label.config(text="转换完成")
            self.progress_var.set(100)
            messagebox.showinfo("完成", "转换成功完成")
        else:
            self.status_label.config(text="转换失败")
            messagebox.showerror("错误", f"转换失败: {error_message}")
    
    def _convert_video_to_gif_task(self, input_file, output_file):
        """视频转GIF任务"""
        try:
            result = self.converter.convert_mp4_to_gif(
                input_file, 
                output_file,
                fps=self.fps_var.get(),
                quality=self.quality_var.get(),
                scale=self.scale_var.get(),
                start_time=self.start_time_var.get(),
                duration=self.duration_var.get(),
                progress_callback=self._update_progress
            )
            
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, result, "" if result else "转换失败，请检查输入文件格式和参数")
            
        except Exception as e:
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, False, str(e))
    
    def _convert_video_format_task(self, input_file, output_file):
        """视频格式转换任务"""
        try:
            result = self.converter.convert_video_format(
                input_file, 
                output_file,
                video_codec=self.video_codec_var.get(),
                audio_codec=self.audio_codec_var.get(),
                video_bitrate=self.video_bitrate_var.get(),
                audio_bitrate=self.audio_bitrate_var.get(),
                resolution=self.resolution_var.get(),
                fps=self.video_fps_var.get(),
                progress_callback=self._update_progress
            )
            
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, result, "" if result else "转换失败，请检查输入文件格式和参数")
            
        except Exception as e:
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, False, str(e))
    
    def _convert_audio_format_task(self, input_file, output_file):
        """音频格式转换任务"""
        try:
            result = self.converter.convert_audio_format(
                input_file, 
                output_file,
                audio_codec=self.audio_only_codec_var.get(),
                audio_bitrate=self.audio_only_bitrate_var.get(),
                sample_rate=self.sample_rate_var.get(),
                channels=self.channels_var.get(),
                progress_callback=self._update_progress
            )
            
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, result, "" if result else "转换失败，请检查输入文件格式和参数")
            
        except Exception as e:
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, False, str(e))
    
    def _convert_image_format_task(self, input_file, output_file):
        """图片格式转换任务"""
        try:
            # 准备调整大小参数
            resize = None
            width = self.width_var.get()
            height = self.height_var.get()
            if width > 0 and height > 0:
                resize = (width, height)
            
            result = self.converter.convert_image_format(
                input_file, 
                output_file,
                quality=self.image_quality_var.get(),
                resize=resize,
                rotate=self.rotation_var.get(),
                flip=self.flip_var.get(),
                mirror=self.mirror_var.get(),
                progress_callback=self._update_progress
            )
            
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, result, "" if result else "转换失败，请检查输入文件格式和参数")
            
        except Exception as e:
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, False, str(e))
    
    def _extract_audio_task(self, input_file, output_file):
        """提取音频任务"""
        try:
            result = self.converter.extract_audio_from_video(
                input_file, 
                output_file,
                audio_codec=self.extract_audio_codec_var.get(),
                audio_bitrate=self.extract_audio_bitrate_var.get(),
                progress_callback=self._update_progress
            )
            
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, result, "" if result else "提取失败，请检查输入文件格式和参数")
            
        except Exception as e:
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, False, str(e))
    
    def _extract_single_frame_task(self, input_file, output_dir):
        """提取单帧任务"""
        try:
            # 确定输出文件路径
            basename = os.path.splitext(os.path.basename(input_file))[0]
            timestamp = self.timestamp_var.get()
            output_file = os.path.join(output_dir, f"{basename}_frame_{timestamp:.1f}s.jpg")
            
            # 提取帧
            result = self.timestamp_extractor.extract_frame(
                input_file, 
                output_file, 
                timestamp
            )
            
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, result, "" if result else "提取失败，请检查输入文件格式和参数")
            
        except Exception as e:
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, False, str(e))
    
    def _extract_frames_sequence_task(self, input_file, output_dir):
        """提取多帧序列任务"""
        try:
            # 提取帧序列
            frames = self.timestamp_extractor.extract_frames_sequence(
                input_file, 
                output_dir,
                start_time=self.frame_start_time_var.get(),
                duration=self.frame_duration_var.get(),
                fps=self.extract_fps_var.get(),
                output_format=self.output_format_var.get()
            )
            
            # 在主线程中执行UI更新
            result = len(frames) > 0
            self.root.after(100, self._conversion_completed, result, "" if result else "提取失败，请检查输入文件格式和参数")
            
        except Exception as e:
            # 在主线程中执行UI更新
            self.root.after(100, self._conversion_completed, False, str(e))

def main():
    """格式转换工具主函数"""
    root = tk.Tk()
    app = FormatConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 