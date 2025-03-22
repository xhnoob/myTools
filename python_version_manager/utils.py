#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
实用工具函数
用于扫描Python版本、切换版本和管理包
"""

import os
import sys
import subprocess
import re
import glob
import winreg
from pathlib import Path
import ctypes
import configparser
import json

# 常用的PyPI镜像源列表
COMMON_PYPI_MIRRORS = [
    {"name": "PyPI官方源", "url": "https://pypi.org/simple"},
    {"name": "清华大学源", "url": "https://pypi.tuna.tsinghua.edu.cn/simple"},
    {"name": "阿里云源", "url": "https://mirrors.aliyun.com/pypi/simple"},
    {"name": "腾讯云源", "url": "https://mirrors.cloud.tencent.com/pypi/simple"},
    {"name": "华为云源", "url": "https://repo.huaweicloud.com/repository/pypi/simple"},
    {"name": "中国科学技术大学源", "url": "https://pypi.mirrors.ustc.edu.cn/simple"},
    {"name": "豆瓣源", "url": "https://pypi.douban.com/simple"},
]

# 常用包的中文描述对照表
PACKAGE_DESCRIPTIONS = {
    "numpy": "强大的科学计算库，提供多维数组对象和各种派生对象",
    "pandas": "强大的数据分析和处理库，提供DataFrame等数据结构",
    "matplotlib": "强大的绘图库，用于创建静态、动态或交互式可视化",
    "scikit-learn": "机器学习库，提供各种分类、回归和聚类算法",
    "tensorflow": "谷歌开发的开源机器学习框架，用于深度学习研究和应用",
    "torch": "Facebook开发的深度学习框架，用于研究和生产环境",
    "django": "高级Python Web框架，鼓励快速开发和简洁设计",
    "flask": "轻量级Web应用框架，易于上手且高度可定制",
    "requests": "简单易用的HTTP库，用于发送HTTP/1.1请求",
    "beautifulsoup4": "用于解析HTML和XML文件的库，提取数据更加方便",
    "selenium": "自动化Web浏览器测试工具，用于模拟用户操作",
    "pillow": "Python图像处理库，提供广泛的文件格式支持和图像处理功能",
    "sqlalchemy": "SQL工具包和对象关系映射(ORM)库，用于数据库操作",
    "pytest": "简单而强大的Python测试框架，支持单元测试和功能测试",
    "openpyxl": "用于读写Excel 2010+ (.xlsx)文件的Python库",
    "scrapy": "高级Web爬虫框架，用于提取结构化数据",
    "pymysql": "MySQL数据库连接器，纯Python实现的MySQL客户端",
    "psycopg2": "PostgreSQL数据库适配器，最流行的PostgreSQL数据库接口",
    "redis": "Redis数据库的Python接口",
    "celery": "分布式任务队列，支持实时处理和任务调度",
    "fastapi": "现代、快速的Web框架，用于构建API，基于Python 3.6+类型提示",
    "pyyaml": "YAML解析器和生成器，支持YAML 1.1规范",
    "jinja2": "现代设计师友好的Python模板语言",
    "setuptools": "Python包管理工具，用于分发Python包",
    "wheel": "Python打包格式，替代传统的.egg文件",
    "pip": "Python包安装器，用于安装和管理Python包",
    "virtualenv": "创建隔离的Python环境工具",
    "tqdm": "快速、可扩展的进度条工具，可用于循环和CLI",
    "twine": "用于上传Python包到PyPI的工具",
    "black": "无情的Python代码格式化工具，遵循PEP 8风格",
    "flake8": "Python代码风格检查工具，集成了pyflakes, pycodestyle和McCabe复杂度检查",
}

def is_admin():
    """检查程序是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_python_installations():
    """
    扫描系统中安装的Python版本
    
    返回:
        list: 包含每个Python安装的字典列表，每个字典包含路径和版本
    """
    python_installations = []
    
    # 检查常见安装路径
    common_paths = [
        r"C:\Python*",
        r"C:\Program Files\Python*",
        r"C:\Program Files (x86)\Python*",
        os.path.expanduser("~") + r"\AppData\Local\Programs\Python\Python*",
    ]
    
    for path_pattern in common_paths:
        for path in glob.glob(path_pattern):
            if os.path.isdir(path):
                # 检查python.exe是否存在
                python_exe = os.path.join(path, "python.exe")
                if os.path.isfile(python_exe):
                    try:
                        # 获取版本
                        result = subprocess.run([python_exe, "--version"], 
                                               stdout=subprocess.PIPE, 
                                               stderr=subprocess.PIPE,
                                               text=True,
                                               creationflags=subprocess.CREATE_NO_WINDOW)
                        version = result.stdout.strip() or result.stderr.strip()
                        if version:
                            # 提取版本号，例如从 "Python 3.9.5" 中提取 "3.9.5"
                            version_match = re.search(r"Python\s+(\d+\.\d+\.\d+)", version)
                            if version_match:
                                version = version_match.group(1)
                                python_installations.append({
                                    "path": python_exe,
                                    "version": version
                                })
                    except Exception as e:
                        print(f"Error getting version for {python_exe}: {e}")
    
    # 检查系统中的PATH环境变量
    paths = os.environ["PATH"].split(os.pathsep)
    for path in paths:
        python_exe = os.path.join(path, "python.exe")
        if os.path.isfile(python_exe) and not any(inst["path"] == python_exe for inst in python_installations):
            try:
                result = subprocess.run([python_exe, "--version"], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE,
                                       text=True,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
                version = result.stdout.strip() or result.stderr.strip()
                if version:
                    version_match = re.search(r"Python\s+(\d+\.\d+\.\d+)", version)
                    if version_match:
                        version = version_match.group(1)
                        python_installations.append({
                            "path": python_exe,
                            "version": version
                        })
            except Exception as e:
                print(f"Error getting version for {python_exe}: {e}")
    
    return python_installations

def get_current_python_version():
    """获取当前正在使用的Python版本"""
    try:
        # 获取系统环境变量中的python
        result = subprocess.run(["python", "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
        version = result.stdout.strip() or result.stderr.strip()
        if version:
            version_match = re.search(r"Python\s+(\d+\.\d+\.\d+)", version)
            if version_match:
                version = version_match.group(1)
                
                # 获取python.exe的路径
                which_result = subprocess.run(["where", "python"], 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE,
                                            text=True,
                                            creationflags=subprocess.CREATE_NO_WINDOW)
                path = which_result.stdout.strip().split("\n")[0]
                
                return {
                    "path": path,
                    "version": version
                }
    except Exception as e:
        print(f"Error getting current Python version: {e}")
    
    return {"path": "未找到", "version": "未找到"}

def set_python_version(python_path):
    """
    设置系统当前的Python版本
    
    参数:
        python_path (str): Python可执行文件的路径
    
    返回:
        bool: 是否成功设置
    """
    if not is_admin():
        return False, "需要管理员权限才能更改系统环境变量"
    
    try:
        # 获取Python目录
        python_dir = os.path.dirname(python_path)
        scripts_dir = os.path.join(python_dir, "Scripts")
        
        # 打开环境变量注册表项
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS)
        
        # 获取当前PATH
        path, _ = winreg.QueryValueEx(key, "PATH")
        
        # 过滤掉其他Python目录
        paths = path.split(os.pathsep)
        new_paths = [p for p in paths if not (re.search(r"\\Python\d+", p) or re.search(r"\\Python\d+\\Scripts", p))]
        
        # 添加新的Python目录到PATH
        new_paths.insert(0, scripts_dir)
        new_paths.insert(0, python_dir)
        
        # 更新PATH
        new_path = os.pathsep.join(new_paths)
        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        winreg.CloseKey(key)
        
        # 通知系统环境变量已更改
        win32con = ctypes.windll.user32.SendMessageTimeoutW
        win32con(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None)
        
        return True, "成功设置Python版本，请重启终端以使更改生效"
    except Exception as e:
        return False, f"设置Python版本时出错: {str(e)}"

def get_package_description(python_path, package_name):
    """
    获取包的中文描述
    
    参数:
        python_path (str): Python可执行文件的路径
        package_name (str): 包名
    
    返回:
        str: 包的中文描述
    """
    # 先检查是否有预定义的中文描述
    if package_name.lower() in PACKAGE_DESCRIPTIONS:
        return PACKAGE_DESCRIPTIONS[package_name.lower()]
    
    # 如果没有预定义描述，则尝试获取pip的描述并翻译
    try:
        result = subprocess.run(
            [python_path, "-m", "pip", "show", package_name], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            return "无法获取描述"
        
        # 解析输出以找到Summary字段
        match = re.search(r"Summary:\s*(.+)", result.stdout)
        if match:
            description = match.group(1).strip()
            # 这里可以添加简单的翻译或描述修改逻辑
            # 为了示例，我们简单地返回英文描述
            return f"[英] {description}"
        
        return "无描述"
    except Exception as e:
        print(f"获取包描述时出错: {e}")
        return "获取描述出错"

def list_installed_packages(python_path):
    """
    列出指定Python版本中已安装的包
    
    参数:
        python_path (str): Python可执行文件的路径
    
    返回:
        list: 包含已安装包信息的列表
    """
    try:
        result = subprocess.run([python_path, "-m", "pip", "list", "--format=json"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode != 0:
            return []
        
        packages = json.loads(result.stdout)
        
        # 为每个包添加描述
        for package in packages:
            package["description"] = get_package_description(python_path, package["name"])
            
        return packages
    except Exception as e:
        print(f"列出已安装包时出错: {e}")
        return []

def install_package(python_path, package_name):
    """
    使用指定的Python版本安装包
    
    参数:
        python_path (str): Python可执行文件的路径
        package_name (str): 要安装的包名
    
    返回:
        tuple: (成功与否, 消息)
    """
    try:
        result = subprocess.run([python_path, "-m", "pip", "install", package_name], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            return True, f"成功安装: {package_name}"
        else:
            return False, f"安装失败: {result.stderr}"
    except Exception as e:
        return False, f"安装包时出错: {str(e)}"

def uninstall_package(python_path, package_name):
    """
    使用指定的Python版本卸载包
    
    参数:
        python_path (str): Python可执行文件的路径
        package_name (str): 要卸载的包名
    
    返回:
        tuple: (成功与否, 消息)
    """
    try:
        result = subprocess.run([python_path, "-m", "pip", "uninstall", "-y", package_name], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            return True, f"成功卸载: {package_name}"
        else:
            return False, f"卸载失败: {result.stderr}"
    except Exception as e:
        return False, f"卸载包时出错: {str(e)}"

def update_package(python_path, package_name):
    """
    使用指定的Python版本更新包
    
    参数:
        python_path (str): Python可执行文件的路径
        package_name (str): 要更新的包名
    
    返回:
        tuple: (成功与否, 消息)
    """
    try:
        result = subprocess.run([python_path, "-m", "pip", "install", "--upgrade", package_name], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            return True, f"成功更新: {package_name}"
        else:
            return False, f"更新失败: {result.stderr}"
    except Exception as e:
        return False, f"更新包时出错: {str(e)}"

def get_pip_config_path(python_path):
    """
    获取指定Python版本的pip配置文件路径
    
    参数:
        python_path (str): Python可执行文件的路径
    
    返回:
        str: pip配置文件的路径
    """
    try:
        # 获取pip配置文件路径
        result = subprocess.run(
            [python_path, "-m", "pip", "config", "list"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # 查找配置文件路径
        match = re.search(r"global\.config\s*=\s*(.+)", result.stdout)
        if match:
            return match.group(1).strip()
        
        # 如果找不到配置文件，返回默认路径
        user_dir = os.path.expanduser("~")
        return os.path.join(user_dir, "pip", "pip.ini")
    except Exception as e:
        print(f"获取pip配置文件路径时出错: {e}")
        # 返回默认路径
        user_dir = os.path.expanduser("~")
        return os.path.join(user_dir, "pip", "pip.ini")

def get_current_pip_index(python_path):
    """
    获取当前pip使用的镜像源
    
    参数:
        python_path (str): Python可执行文件的路径
    
    返回:
        str: 当前镜像源URL
    """
    try:
        # 获取pip当前配置
        result = subprocess.run(
            [python_path, "-m", "pip", "config", "list"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # 解析输出以找到index-url
        match = re.search(r"global\.index-url\s*=\s*(.+)", result.stdout)
        if match:
            return match.group(1).strip()
        
        # 默认使用PyPI官方源
        return "https://pypi.org/simple"
    except Exception as e:
        print(f"获取当前pip镜像源时出错: {e}")
        return "未知"

def set_pip_index(python_path, index_url, trusted=True):
    """
    设置pip使用的镜像源
    
    参数:
        python_path (str): Python可执行文件的路径
        index_url (str): 镜像源URL
        trusted (bool): 是否信任此源（对于HTTPS验证）
    
    返回:
        tuple: (成功与否, 消息)
    """
    try:
        # 设置index-url
        cmd = [python_path, "-m", "pip", "config", "set", "global.index-url", index_url]
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            return False, f"设置镜像源失败: {result.stderr}"
        
        # 如果需要信任此源
        if trusted and "https" in index_url:
            trusted_cmd = [python_path, "-m", "pip", "config", "set", "global.trusted-host", index_url.split("//")[1].split("/")[0]]
            subprocess.run(
                trusted_cmd,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        
        return True, f"成功设置镜像源为: {index_url}"
    except Exception as e:
        return False, f"设置镜像源时出错: {str(e)}"

def list_pip_indices():
    """
    列出常用的PyPI镜像源
    
    返回:
        list: 包含镜像源信息的列表
    """
    return COMMON_PYPI_MIRRORS

def add_custom_pip_index(name, url):
    """
    添加自定义PyPI镜像源到列表
    
    参数:
        name (str): 镜像源名称
        url (str): 镜像源URL
    
    返回:
        bool: 是否成功添加
    """
    # 检查URL是否有效
    if not url.startswith("http://") and not url.startswith("https://"):
        return False, "URL必须以http://或https://开头"
    
    # 检查是否已存在
    for mirror in COMMON_PYPI_MIRRORS:
        if mirror["url"] == url:
            return False, "此镜像源已存在"
    
    # 添加到列表
    COMMON_PYPI_MIRRORS.append({"name": name, "url": url})
    return True, f"成功添加镜像源: {name}" 