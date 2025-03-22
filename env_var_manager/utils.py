#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
环境变量管理器的工具函数
"""

import os
import winreg
import ctypes
from ctypes import wintypes

def get_env_var(name, user=True):
    """
    获取环境变量的值
    
    参数:
    name (str): 环境变量名
    user (bool): 是否是用户环境变量，False表示系统环境变量
    
    返回:
    str: 环境变量的值，如果不存在则返回None
    """
    try:
        if user:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
        else:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
        
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    except WindowsError:
        return None

def set_env_var(name, value, user=True):
    """
    设置环境变量
    
    参数:
    name (str): 环境变量名
    value (str): 环境变量值
    user (bool): 是否是用户环境变量，False表示系统环境变量
    
    返回:
    bool: 是否设置成功
    """
    try:
        if user:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
        else:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                               0, winreg.KEY_SET_VALUE)
        
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        
        # 广播环境变量更改消息
        broadcast_env_change()
        return True
    except Exception:
        return False

def delete_env_var(name, user=True):
    """
    删除环境变量
    
    参数:
    name (str): 环境变量名
    user (bool): 是否是用户环境变量，False表示系统环境变量
    
    返回:
    bool: 是否删除成功
    """
    try:
        if user:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
        else:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                               0, winreg.KEY_SET_VALUE)
        
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        
        # 广播环境变量更改消息
        broadcast_env_change()
        return True
    except Exception:
        return False

def get_path_var(user=True):
    """
    获取PATH环境变量
    
    参数:
    user (bool): 是否是用户环境变量，False表示系统环境变量
    
    返回:
    list: PATH环境变量中的路径列表
    """
    path = get_env_var("PATH", user)
    if path:
        return [p for p in path.split(";") if p.strip()]
    return []

def set_path_var(paths, user=True):
    """
    设置PATH环境变量
    
    参数:
    paths (list): PATH环境变量中的路径列表
    user (bool): 是否是用户环境变量，False表示系统环境变量
    
    返回:
    bool: 是否设置成功
    """
    path = ";".join(paths)
    
    try:
        if user:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
        else:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                               0, winreg.KEY_SET_VALUE)
        
        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, path)
        winreg.CloseKey(key)
        
        # 广播环境变量更改消息
        broadcast_env_change()
        return True
    except Exception:
        return False

def add_to_path(path, user=True, prepend=False):
    """
    将路径添加到PATH环境变量
    
    参数:
    path (str): 要添加的路径
    user (bool): 是否是用户环境变量，False表示系统环境变量
    prepend (bool): 是否添加到PATH的开头，False表示添加到末尾
    
    返回:
    bool: 是否添加成功
    """
    paths = get_path_var(user)
    
    # 如果路径已存在，则移除
    if path in paths:
        paths.remove(path)
    
    # 添加到开头或末尾
    if prepend:
        paths.insert(0, path)
    else:
        paths.append(path)
    
    return set_path_var(paths, user)

def remove_from_path(path, user=True):
    """
    从PATH环境变量中移除路径
    
    参数:
    path (str): 要移除的路径
    user (bool): 是否是用户环境变量，False表示系统环境变量
    
    返回:
    bool: 是否移除成功
    """
    paths = get_path_var(user)
    
    if path in paths:
        paths.remove(path)
        return set_path_var(paths, user)
    
    return True  # 路径不存在，视为移除成功

def broadcast_env_change():
    """
    广播环境变量更改消息
    """
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    
    # 定义SendMessageTimeout函数
    SendMessageTimeout = user32.SendMessageTimeoutW
    SendMessageTimeout.argtypes = (
        wintypes.HWND,   # hWnd
        wintypes.UINT,   # Msg
        wintypes.WPARAM, # wParam
        wintypes.LPCWSTR,# lParam
        wintypes.UINT,   # fuFlags
        wintypes.UINT,   # uTimeout
        wintypes.LPVOID  # lpdwResult
    )
    
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    SMTO_ABORTIFHUNG = 0x0002
    
    result = ctypes.c_void_p()
    SendMessageTimeout(
        HWND_BROADCAST,
        WM_SETTINGCHANGE,
        0,
        "Environment",
        SMTO_ABORTIFHUNG,
        5000,
        ctypes.byref(result)
    )
    
    # 更新当前进程的环境变量
    for name, value in os.environ.items():
        try:
            new_value = get_env_var(name, True) or get_env_var(name, False)
            if new_value:
                os.environ[name] = new_value
        except:
            pass 