#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
网络诊断工具的工具函数模块
提供获取网络信息和执行网络操作的功能
"""

import os
import sys
import socket
import subprocess
import platform
import re
import time
from datetime import datetime

def get_network_info():
    """
    获取完整的网络信息
    返回格式化的网络信息文本
    """
    info = []
    
    # 添加时间和系统信息
    info.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    info.append(f"系统信息: {platform.system()} {platform.version()}")
    info.append(f"主机名: {socket.gethostname()}")
    info.append("-" * 60)
    
    # 获取网络接口信息
    info.append("\n== 网络接口信息 ==")
    iface_info = get_network_interfaces()
    info.append(iface_info)
    
    # 获取DNS配置
    info.append("\n== DNS配置 ==")
    dns_info = get_dns_config()
    info.append(dns_info)
    
    # 获取路由表
    info.append("\n== 路由表 ==")
    route_info = get_routing_table()
    info.append(route_info)
    
    # 网络连接测试
    info.append("\n== 网络连接测试 ==")
    conn_info = test_network_connection()
    info.append(conn_info)
    
    return "\n".join(info)

def get_network_interfaces():
    """获取网络接口信息"""
    try:
        if platform.system() == "Windows":
            # 在Windows上使用ipconfig命令
            result = subprocess.run(
                ["ipconfig", "/all"], 
                capture_output=True, 
                text=True,
                encoding='gbk'  # Windows命令行输出通常是GBK编码
            )
            return result.stdout
        else:
            # 在Linux/Unix上使用ifconfig命令
            result = subprocess.run(
                ["ifconfig"], 
                capture_output=True, 
                text=True
            )
            return result.stdout
    except Exception as e:
        return f"获取网络接口信息失败: {str(e)}"

def get_dns_config():
    """获取DNS配置"""
    try:
        if platform.system() == "Windows":
            # 在Windows上使用ipconfig /displaydns命令
            result = subprocess.run(
                ["ipconfig", "/displaydns"], 
                capture_output=True, 
                text=True,
                encoding='gbk'
            )
            
            # 截取部分内容，因为完整输出可能非常大
            output = result.stdout.split("\n")
            # 只取前30行
            return "\n".join(output[:30]) + "\n... (更多DNS记录已省略) ..."
        else:
            # 在Linux/Unix上，读取/etc/resolv.conf文件
            result = subprocess.run(
                ["cat", "/etc/resolv.conf"], 
                capture_output=True, 
                text=True
            )
            return result.stdout
    except Exception as e:
        return f"获取DNS配置失败: {str(e)}"

def get_routing_table():
    """获取路由表"""
    try:
        if platform.system() == "Windows":
            # 在Windows上使用route print命令
            result = subprocess.run(
                ["route", "print"], 
                capture_output=True, 
                text=True,
                encoding='gbk'
            )
            return result.stdout
        else:
            # 在Linux/Unix上使用netstat -r命令
            result = subprocess.run(
                ["netstat", "-r"], 
                capture_output=True, 
                text=True
            )
            return result.stdout
    except Exception as e:
        return f"获取路由表失败: {str(e)}"

def test_network_connection():
    """测试网络连接"""
    results = []
    
    # 测试常用网站连接
    test_targets = [
        ("www.baidu.com", "百度"),
        ("www.qq.com", "腾讯"),
        ("www.microsoft.com", "微软"),
        ("www.google.com", "谷歌")
    ]
    
    # 测试每个目标的连接性
    for target, name in test_targets:
        try:
            # 获取IP地址
            start_time = time.time()
            ip = socket.gethostbyname(target)
            dns_time = time.time() - start_time
            
            # 测试连接
            start_time = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((ip, 80))
            connect_time = time.time() - start_time
            s.close()
            
            if result == 0:
                results.append(f"{name} ({target}): 可连接 [DNS解析: {dns_time:.3f}秒, 连接: {connect_time:.3f}秒]")
            else:
                results.append(f"{name} ({target}): 无法连接 [DNS解析成功: {dns_time:.3f}秒]")
        except socket.gaierror:
            results.append(f"{name} ({target}): DNS解析失败")
        except Exception as e:
            results.append(f"{name} ({target}): 测试出错 - {str(e)}")
    
    return "\n".join(results)

def get_external_ip():
    """获取外部IP地址"""
    try:
        # 尝试多个提供外部IP查询的服务
        services = [
            "http://ifconfig.me/ip",
            "http://api.ipify.org",
            "http://ipinfo.io/ip"
        ]
        
        for service in services:
            try:
                import requests
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        
        return "无法获取外部IP地址"
    except Exception as e:
        return f"获取外部IP地址失败: {str(e)}"

if __name__ == "__main__":
    # 测试函数
    print(get_network_info())
