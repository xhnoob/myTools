#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
网络诊断工具
用于网络测试、IP查询、端口扫描和网络速度测试的图形界面工具
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import socket
import subprocess
import requests
import time
import json
from datetime import datetime

# 导入工具函数
from network_diagnostics.utils import *

class NetworkDiagnostics:
    """网络诊断工具类"""
    
    def __init__(self, root=None):
        """初始化网络诊断工具"""
        self.is_standalone = root is None
        
        if self.is_standalone:
            # 作为独立应用运行时创建根窗口
            self.root = tk.Tk()
            self.root.title("网络诊断工具")
            self.root.geometry("900x600")
            self.root.minsize(900, 600)
        else:
            # 作为工具箱的一部分运行时使用提供的根窗口
            self.root = root
            
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建UI组件
        self.create_widgets()
        
        # 初始化状态
        self.init_state()
        
        if self.is_standalone:
            # 作为独立应用运行时启动主循环
            self.root.mainloop()
            
    def create_widgets(self):
        """创建UI组件"""
        # 创建页签控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 网络信息页签
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="网络信息")
        
        # 网络测试页签
        self.test_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.test_frame, text="网络测试")
        
        # IP工具页签
        self.ip_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ip_frame, text="IP工具")
        
        # 端口扫描页签
        self.port_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.port_frame, text="端口扫描")
        
        # 设置各页签内容
        self.setup_info_tab()
        self.setup_test_tab()
        self.setup_ip_tab()
        self.setup_port_tab()
        
        # 创建按钮框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # 刷新按钮
        self.refresh_button = ttk.Button(self.button_frame, text="刷新网络信息", command=self.refresh_network_info)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 导出按钮
        self.export_button = ttk.Button(self.button_frame, text="导出结果", command=self.export_results)
        self.export_button.pack(side=tk.RIGHT, padx=5)
        
    def setup_info_tab(self):
        """设置网络信息页签"""
        # 创建信息框架
        info_frame = ttk.LabelFrame(self.info_frame, text="当前网络状态")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建滚动文本框
        self.info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.info_text.config(state=tk.DISABLED)
        
    def setup_test_tab(self):
        """设置网络测试页签"""
        # 测试控制框架
        control_frame = ttk.LabelFrame(self.test_frame, text="测试控制")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 测试目标
        ttk.Label(control_frame, text="测试目标:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.test_target = ttk.Combobox(control_frame, width=30)
        self.test_target.grid(row=0, column=1, padx=5, pady=5)
        self.test_target["values"] = ("www.baidu.com", "www.google.com", "www.microsoft.com", "www.github.com")
        self.test_target.current(0)
        
        # 测试选项框架
        options_frame = ttk.Frame(control_frame)
        options_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Ping测试选项
        self.ping_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Ping测试", variable=self.ping_var).pack(side=tk.LEFT, padx=5)
        
        # 路由跟踪选项
        self.tracert_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="路由跟踪", variable=self.tracert_var).pack(side=tk.LEFT, padx=5)
        
        # DNS查询选项
        self.dns_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="DNS查询", variable=self.dns_var).pack(side=tk.LEFT, padx=5)
        
        # HTTP测试选项
        self.http_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="HTTP测试", variable=self.http_var).pack(side=tk.LEFT, padx=5)
        
        # 开始测试按钮
        self.start_test_button = ttk.Button(control_frame, text="开始测试", command=self.start_network_test)
        self.start_test_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)
        
        # 测试结果框架
        result_frame = ttk.LabelFrame(self.test_frame, text="测试结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建滚动文本框
        self.test_result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
        self.test_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.test_result_text.config(state=tk.DISABLED)
    
    def setup_ip_tab(self):
        """设置IP工具页签"""
        # IP查询框架
        query_frame = ttk.LabelFrame(self.ip_frame, text="IP查询")
        query_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # IP输入
        ttk.Label(query_frame, text="IP或域名:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ip_input = ttk.Entry(query_frame, width=30)
        self.ip_input.grid(row=0, column=1, padx=5, pady=5)
        self.ip_input.insert(0, "")
        
        # 查询选项框架
        ip_options_frame = ttk.Frame(query_frame)
        ip_options_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # 地理位置查询选项
        self.geo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ip_options_frame, text="地理位置", variable=self.geo_var).pack(side=tk.LEFT, padx=5)
        
        # 运营商查询选项
        self.isp_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ip_options_frame, text="运营商", variable=self.isp_var).pack(side=tk.LEFT, padx=5)
        
        # 开始查询按钮
        self.start_ip_query_button = ttk.Button(query_frame, text="开始查询", command=self.start_ip_query)
        self.start_ip_query_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)
        
        # IP查询结果框架
        result_frame = ttk.LabelFrame(self.ip_frame, text="查询结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建滚动文本框
        self.ip_result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
        self.ip_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.ip_result_text.config(state=tk.DISABLED)
    
    def setup_port_tab(self):
        """设置端口扫描页签"""
        # 端口扫描框架
        scan_frame = ttk.LabelFrame(self.port_frame, text="端口扫描")
        scan_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 目标输入
        ttk.Label(scan_frame, text="目标地址:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_target = ttk.Entry(scan_frame, width=30)
        self.port_target.grid(row=0, column=1, padx=5, pady=5)
        self.port_target.insert(0, "127.0.0.1")
        
        # 端口范围
        ttk.Label(scan_frame, text="端口范围:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        port_range_frame = ttk.Frame(scan_frame)
        port_range_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.port_start = ttk.Spinbox(port_range_frame, from_=1, to=65535, width=10)
        self.port_start.pack(side=tk.LEFT, padx=5)
        self.port_start.set("1")
        
        ttk.Label(port_range_frame, text="-").pack(side=tk.LEFT)
        
        self.port_end = ttk.Spinbox(port_range_frame, from_=1, to=65535, width=10)
        self.port_end.pack(side=tk.LEFT, padx=5)
        self.port_end.set("1024")
        
        # 常用端口选项
        presets_frame = ttk.Frame(scan_frame)
        presets_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(presets_frame, text="端口预设:").pack(side=tk.LEFT, padx=5)
        
        self.port_preset = ttk.Combobox(presets_frame, width=20)
        self.port_preset.pack(side=tk.LEFT, padx=5)
        self.port_preset["values"] = ("常用端口", "Web服务端口", "邮件服务端口", "数据库端口", "远程端口")
        self.port_preset.current(0)
        self.port_preset.bind("<<ComboboxSelected>>", self.on_port_preset_selected)
        
        # 开始扫描按钮
        self.start_scan_button = ttk.Button(scan_frame, text="开始扫描", command=self.start_port_scan)
        self.start_scan_button.grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)
        
        # 扫描结果框架
        scan_result_frame = ttk.LabelFrame(self.port_frame, text="扫描结果")
        scan_result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建滚动文本框
        self.scan_result_text = scrolledtext.ScrolledText(scan_result_frame, wrap=tk.WORD)
        self.scan_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.scan_result_text.config(state=tk.DISABLED)
    
    def init_state(self):
        """初始化状态"""
        # 加载网络信息
        self.refresh_network_info()
    
    def refresh_network_info(self):
        """刷新网络信息"""
        # 创建线程执行网络信息获取，避免UI卡顿
        threading.Thread(target=self._refresh_network_info_thread, daemon=True).start()
    
    def _refresh_network_info_thread(self):
        """在后台线程中刷新网络信息"""
        try:
            # 获取网络信息
            network_info = get_network_info()
            
            # 更新UI（在主线程中）
            self.root.after(0, lambda: self._update_info_text(network_info))
        except Exception as e:
            # 更新UI（在主线程中）
            self.root.after(0, lambda: messagebox.showerror("错误", f"获取网络信息时出错:\n{str(e)}"))
    
    def _update_info_text(self, info_text):
        """更新信息文本"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info_text)
        self.info_text.config(state=tk.DISABLED)
    
    def export_results(self):
        """导出结果"""
        try:
            # 获取当前选中的页签
            current_tab = self.notebook.index(self.notebook.select())
            
            # 根据当前页签导出对应内容
            if current_tab == 0:  # 网络信息
                content = self.info_text.get(1.0, tk.END)
                filename = f"网络信息_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            elif current_tab == 1:  # 网络测试
                content = self.test_result_text.get(1.0, tk.END)
                filename = f"网络测试_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            elif current_tab == 2:  # IP工具
                content = self.ip_result_text.get(1.0, tk.END)
                filename = f"IP查询_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            elif current_tab == 3:  # 端口扫描
                content = self.scan_result_text.get(1.0, tk.END)
                filename = f"端口扫描_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            else:
                return
            
            # 保存文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 提示成功
            messagebox.showinfo("导出成功", f"结果已导出到:\n{os.path.abspath(filename)}")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出结果时出错:\n{str(e)}")
    
    def start_network_test(self):
        """开始网络测试"""
        # 获取测试目标
        target = self.test_target.get()
        if not target:
            messagebox.showwarning("提示", "请输入测试目标")
            return
        
        # 检查是否选择了测试项
        if not (self.ping_var.get() or self.tracert_var.get() or 
                self.dns_var.get() or self.http_var.get()):
            messagebox.showwarning("提示", "请选择至少一项测试")
            return
        
        # 禁用开始测试按钮
        self.start_test_button.config(state=tk.DISABLED)
        
        # 清空测试结果
        self.test_result_text.config(state=tk.NORMAL)
        self.test_result_text.delete(1.0, tk.END)
        self.test_result_text.insert(tk.END, f"开始测试 {target}...\n\n")
        self.test_result_text.config(state=tk.DISABLED)
        
        # 创建线程执行测试，避免UI卡顿
        threading.Thread(target=self._network_test_thread, args=(target,), daemon=True).start()
    
    def _network_test_thread(self, target):
        """在后台线程中执行网络测试"""
        try:
            # 执行测试
            results = []
            
            # 添加测试时间
            results.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append(f"测试目标: {target}")
            results.append("-" * 50)
            
            # Ping测试
            if self.ping_var.get():
                results.append("\n== Ping测试 ==")
                ping_result = self._execute_ping(target)
                results.append(ping_result)
            
            # 路由跟踪测试
            if self.tracert_var.get():
                results.append("\n== 路由跟踪 ==")
                tracert_result = self._execute_tracert(target)
                results.append(tracert_result)
            
            # DNS查询测试
            if self.dns_var.get():
                results.append("\n== DNS查询 ==")
                dns_result = self._execute_dns_query(target)
                results.append(dns_result)
            
            # HTTP测试
            if self.http_var.get():
                results.append("\n== HTTP测试 ==")
                http_result = self._execute_http_test(target)
                results.append(http_result)
            
            # 测试完成
            results.append("\n" + "-" * 50)
            results.append("测试完成!")
            
            # 更新UI（在主线程中）
            self.root.after(0, lambda: self._update_test_result_text("\n".join(results)))
            self.root.after(0, lambda: self.start_test_button.config(state=tk.NORMAL))
            
        except Exception as e:
            # 更新UI（在主线程中）
            error_msg = f"执行网络测试时出错:\n{str(e)}"
            self.root.after(0, lambda: self._update_test_result_text(error_msg))
            self.root.after(0, lambda: self.start_test_button.config(state=tk.NORMAL))
    
    def _execute_ping(self, target):
        """执行Ping测试"""
        try:
            result = subprocess.run(
                ["ping", target, "-n", "4"], 
                capture_output=True, 
                text=True,
                encoding='gbk'  # Windows命令行输出通常是GBK编码
            )
            return result.stdout
        except Exception as e:
            return f"Ping测试出错: {str(e)}"
    
    def _execute_tracert(self, target):
        """执行路由跟踪测试"""
        try:
            result = subprocess.run(
                ["tracert", target],
                capture_output=True,
                text=True,
                encoding='gbk'
            )
            return result.stdout
        except Exception as e:
            return f"路由跟踪测试出错: {str(e)}"
    
    def _execute_dns_query(self, target):
        """执行DNS查询测试"""
        try:
            # 尝试解析IP
            ip_addresses = socket.getaddrinfo(target, None)
            result = [f"DNS服务器: 系统默认"]
            result.append(f"查询域名: {target}")
            result.append("查询结果:")
            
            # 去重IP地址
            unique_ips = set()
            for ip_info in ip_addresses:
                ip = ip_info[4][0]
                unique_ips.add(ip)
            
            for ip in unique_ips:
                result.append(f"  {ip}")
            
            return "\n".join(result)
        except Exception as e:
            return f"DNS查询测试出错: {str(e)}"
    
    def _execute_http_test(self, target):
        """执行HTTP测试"""
        try:
            # 构建URL (如果没有指定协议，则默认使用http)
            if not target.startswith(('http://', 'https://')):
                url = f"http://{target}"
            else:
                url = target
            
            # 记录开始时间
            start_time = time.time()
            
            # 发送HTTP请求
            response = requests.get(url, timeout=10)
            
            # 计算耗时
            elapsed_time = time.time() - start_time
            
            result = [f"URL: {url}"]
            result.append(f"状态码: {response.status_code} {response.reason}")
            result.append(f"响应时间: {elapsed_time:.3f} 秒")
            result.append(f"服务器: {response.headers.get('Server', '未知')}")
            result.append(f"内容类型: {response.headers.get('Content-Type', '未知')}")
            result.append(f"内容长度: {len(response.content)} 字节")
            
            return "\n".join(result)
        except requests.exceptions.RequestException as e:
            return f"HTTP测试出错: {str(e)}"
    
    def _update_test_result_text(self, text):
        """更新测试结果文本"""
        self.test_result_text.config(state=tk.NORMAL)
        self.test_result_text.delete(1.0, tk.END)
        self.test_result_text.insert(tk.END, text)
        self.test_result_text.config(state=tk.DISABLED)
    
    def start_ip_query(self):
        """开始IP查询"""
        # 获取IP或域名
        ip_or_domain = self.ip_input.get()
        if not ip_or_domain:
            messagebox.showwarning("提示", "请输入IP地址或域名")
            return
        
        # 检查是否选择了查询项
        if not (self.geo_var.get() or self.isp_var.get()):
            messagebox.showwarning("提示", "请选择至少一项查询")
            return
        
        # 禁用开始查询按钮
        self.start_ip_query_button.config(state=tk.DISABLED)
        
        # 清空查询结果
        self.ip_result_text.config(state=tk.NORMAL)
        self.ip_result_text.delete(1.0, tk.END)
        self.ip_result_text.insert(tk.END, f"开始查询 {ip_or_domain}...\n\n")
        self.ip_result_text.config(state=tk.DISABLED)
        
        # 创建线程执行查询，避免UI卡顿
        threading.Thread(target=self._ip_query_thread, args=(ip_or_domain,), daemon=True).start()
    
    def _ip_query_thread(self, ip_or_domain):
        """在后台线程中执行IP查询"""
        try:
            # 查询结果
            results = []
            
            # 添加查询时间
            results.append(f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append(f"查询目标: {ip_or_domain}")
            results.append("-" * 50)
            
            # 解析IP（如果输入的是域名）
            try:
                ip = socket.gethostbyname(ip_or_domain)
                if ip != ip_or_domain:
                    results.append(f"\n域名解析: {ip_or_domain} -> {ip}")
                    ip_or_domain = ip
            except:
                pass
            
            # 获取IP信息
            ip_info = self._get_ip_info(ip_or_domain)
            
            # 地理位置查询
            if self.geo_var.get():
                results.append("\n== 地理位置信息 ==")
                if ip_info and "country" in ip_info:
                    results.append(f"国家/地区: {ip_info.get('country', '未知')}")
                    results.append(f"省/州: {ip_info.get('regionName', '未知')}")
                    results.append(f"城市: {ip_info.get('city', '未知')}")
                    results.append(f"经度: {ip_info.get('lon', '未知')}")
                    results.append(f"纬度: {ip_info.get('lat', '未知')}")
                    results.append(f"时区: {ip_info.get('timezone', '未知')}")
                else:
                    results.append("无法获取地理位置信息")
            
            # 运营商查询
            if self.isp_var.get():
                results.append("\n== 运营商信息 ==")
                if ip_info and "isp" in ip_info:
                    results.append(f"ISP: {ip_info.get('isp', '未知')}")
                    results.append(f"组织: {ip_info.get('org', '未知')}")
                    results.append(f"AS号: {ip_info.get('as', '未知')}")
                else:
                    results.append("无法获取运营商信息")
            
            # 查询完成
            results.append("\n" + "-" * 50)
            results.append("查询完成!")
            
            # 更新UI（在主线程中）
            self.root.after(0, lambda: self._update_ip_result_text("\n".join(results)))
            self.root.after(0, lambda: self.start_ip_query_button.config(state=tk.NORMAL))
            
        except Exception as e:
            # 更新UI（在主线程中）
            error_msg = f"执行IP查询时出错:\n{str(e)}"
            self.root.after(0, lambda: self._update_ip_result_text(error_msg))
            self.root.after(0, lambda: self.start_ip_query_button.config(state=tk.NORMAL))
    
    def _get_ip_info(self, ip):
        """获取IP信息"""
        try:
            # 使用IP-API获取IP信息
            url = f"http://ip-api.com/json/{ip}?fields=66846719&lang=zh-CN"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("status") == "success":
                return data
            return None
        except:
            return None
    
    def _update_ip_result_text(self, text):
        """更新IP查询结果文本"""
        self.ip_result_text.config(state=tk.NORMAL)
        self.ip_result_text.delete(1.0, tk.END)
        self.ip_result_text.insert(tk.END, text)
        self.ip_result_text.config(state=tk.DISABLED)
    
    def on_port_preset_selected(self, event):
        """端口预设选择事件"""
        preset = self.port_preset.get()
        
        # 根据预设设置端口范围
        if preset == "常用端口":
            self.port_start.set("1")
            self.port_end.set("1024")
        elif preset == "Web服务端口":
            self.port_start.set("80")
            self.port_end.set("443")
        elif preset == "邮件服务端口":
            self.port_start.set("25")
            self.port_end.set("587")
        elif preset == "数据库端口":
            self.port_start.set("1433")
            self.port_end.set("3306")
        elif preset == "远程端口":
            self.port_start.set("22")
            self.port_end.set("3389")
    
    def start_port_scan(self):
        """开始端口扫描"""
        # 获取目标地址
        target = self.port_target.get()
        if not target:
            messagebox.showwarning("提示", "请输入目标地址")
            return
        
        # 获取端口范围
        try:
            port_start = int(self.port_start.get())
            port_end = int(self.port_end.get())
            
            if port_start < 1 or port_start > 65535:
                messagebox.showwarning("提示", "起始端口范围必须在1-65535之间")
                return
            
            if port_end < 1 or port_end > 65535:
                messagebox.showwarning("提示", "结束端口范围必须在1-65535之间")
                return
            
            if port_start > port_end:
                messagebox.showwarning("提示", "起始端口不能大于结束端口")
                return
                
            # 限制端口扫描范围，避免过长时间
            if port_end - port_start > 1000:
                if not messagebox.askyesno("提示", "端口范围过大，扫描可能需要较长时间。是否继续？"):
                    return
                    
        except ValueError:
            messagebox.showwarning("提示", "端口必须是整数")
            return
        
        # 禁用开始扫描按钮
        self.start_scan_button.config(state=tk.DISABLED)
        
        # 清空扫描结果
        self.scan_result_text.config(state=tk.NORMAL)
        self.scan_result_text.delete(1.0, tk.END)
        self.scan_result_text.insert(tk.END, f"开始扫描 {target} 的端口 {port_start}-{port_end}...\n\n")
        self.scan_result_text.config(state=tk.DISABLED)
        
        # 创建线程执行扫描，避免UI卡顿
        threading.Thread(target=self._port_scan_thread, 
                        args=(target, port_start, port_end), 
                        daemon=True).start()
    
    def _port_scan_thread(self, target, port_start, port_end):
        """在后台线程中执行端口扫描"""
        try:
            # 扫描结果
            results = []
            open_ports = []
            
            # 添加扫描时间
            results.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append(f"扫描目标: {target}")
            results.append(f"端口范围: {port_start}-{port_end}")
            results.append("-" * 50 + "\n")
            
            # 尝试解析IP
            try:
                ip = socket.gethostbyname(target)
                if ip != target:
                    results.append(f"主机名解析: {target} -> {ip}\n")
                    target = ip
            except socket.gaierror:
                self.root.after(0, lambda: self._update_scan_result_text("\n".join(results) + "\n无法解析主机名，请检查输入"))
                self.root.after(0, lambda: self.start_scan_button.config(state=tk.NORMAL))
                return
            
            # 开始扫描
            results.append("开始扫描...")
            self.root.after(0, lambda: self._update_scan_result_text("\n".join(results)))
            
            # 扫描端口
            for port in range(port_start, port_end + 1):
                # 更新状态（每10个端口更新一次）
                if port % 10 == 0:
                    self.root.after(0, lambda p=port: self._update_scan_status(p, port_end))
                
                # 创建套接字
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)  # 设置超时时间
                
                # 尝试连接
                result = s.connect_ex((target, port))
                if result == 0:
                    # 端口开放
                    open_ports.append(port)
                    # 更新结果
                    service = self._get_service_name(port)
                    port_info = f"端口 {port} 开放 - {service}"
                    self.root.after(0, lambda p=port_info: self._append_scan_result(p))
                
                # 关闭套接字
                s.close()
            
            # 扫描完成
            if open_ports:
                summary = f"\n扫描完成! 发现 {len(open_ports)} 个开放端口: {', '.join(map(str, open_ports))}"
            else:
                summary = "\n扫描完成! 未发现开放端口"
                
            self.root.after(0, lambda: self._append_scan_result("\n" + "-" * 50))
            self.root.after(0, lambda: self._append_scan_result(summary))
            self.root.after(0, lambda: self.start_scan_button.config(state=tk.NORMAL))
            
        except Exception as e:
            # 更新UI（在主线程中）
            error_msg = f"\n执行端口扫描时出错:\n{str(e)}"
            self.root.after(0, lambda: self._append_scan_result(error_msg))
            self.root.after(0, lambda: self.start_scan_button.config(state=tk.NORMAL))
    
    def _get_service_name(self, port):
        """获取端口对应的服务名称"""
        common_ports = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            465: "SMTPS",
            587: "SMTP提交",
            993: "IMAPS",
            995: "POP3S",
            1433: "MSSQL",
            1521: "Oracle",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            8080: "HTTP代理",
            8443: "HTTPS备用"
        }
        return common_ports.get(port, "未知服务")
    
    def _update_scan_status(self, current_port, total_ports):
        """更新扫描状态"""
        self.scan_result_text.config(state=tk.NORMAL)
        # 查找状态行的位置
        text = self.scan_result_text.get(1.0, tk.END)
        if "正在扫描" in text:
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if "正在扫描" in line:
                    # 替换该行
                    self.scan_result_text.delete(f"{i+1}.0", f"{i+1}.end")
                    self.scan_result_text.insert(f"{i+1}.0", f"正在扫描: {current_port}/{total_ports} ({current_port/total_ports*100:.1f}%)")
                    break
        else:
            # 添加新行
            self.scan_result_text.insert(tk.END, f"\n正在扫描: {current_port}/{total_ports} ({current_port/total_ports*100:.1f}%)")
        self.scan_result_text.config(state=tk.DISABLED)
        self.scan_result_text.see(tk.END)
    
    def _append_scan_result(self, text):
        """追加扫描结果"""
        self.scan_result_text.config(state=tk.NORMAL)
        self.scan_result_text.insert(tk.END, f"\n{text}")
        self.scan_result_text.config(state=tk.DISABLED)
        self.scan_result_text.see(tk.END)
    
    def _update_scan_result_text(self, text):
        """更新扫描结果文本"""
        self.scan_result_text.config(state=tk.NORMAL)
        self.scan_result_text.delete(1.0, tk.END)
        self.scan_result_text.insert(tk.END, text)
        self.scan_result_text.config(state=tk.DISABLED)
        self.scan_result_text.see(tk.END)

def main():
    """主函数"""
    app = NetworkDiagnostics()

if __name__ == "__main__":
    main()
