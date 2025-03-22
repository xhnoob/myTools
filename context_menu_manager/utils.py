#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
右键菜单管理器工具类
提供Windows右键菜单的读取、添加、修改和删除功能
"""

import os
import sys
import winreg
import ctypes
import subprocess
from typing import List, Dict, Tuple, Optional, Union, Any

def is_admin() -> bool:
    """
    检查当前程序是否以管理员权限运行
    
    Returns:
        bool: 如果是管理员权限返回True，否则返回False
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def refresh_explorer() -> None:
    """
    刷新Windows资源管理器，使右键菜单更改立即生效
    """
    try:
        # 通知Windows资源管理器更新
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        # 重新启动资源管理器
        subprocess.Popen("explorer.exe")
    except Exception as e:
        print(f"刷新资源管理器失败: {str(e)}")

class RegistryManager:
    """注册表管理类，提供注册表操作的基本方法"""
    
    # 注册表根键映射
    ROOT_KEYS = {
        "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
        "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
        "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
        "HKEY_USERS": winreg.HKEY_USERS,
        "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
        "HKCR": winreg.HKEY_CLASSES_ROOT,
        "HKCU": winreg.HKEY_CURRENT_USER,
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKU": winreg.HKEY_USERS,
        "HKCC": winreg.HKEY_CURRENT_CONFIG
    }
    
    # 注册表值类型映射
    VALUE_TYPES = {
        "REG_SZ": winreg.REG_SZ,
        "REG_MULTI_SZ": winreg.REG_MULTI_SZ,
        "REG_DWORD": winreg.REG_DWORD,
        "REG_QWORD": winreg.REG_QWORD,
        "REG_BINARY": winreg.REG_BINARY,
        "REG_EXPAND_SZ": winreg.REG_EXPAND_SZ
    }
    
    @staticmethod
    def get_root_key(root_key: str) -> int:
        """
        获取注册表根键的句柄
        
        Args:
            root_key: 注册表根键的名称
            
        Returns:
            int: 根键句柄
            
        Raises:
            ValueError: 如果根键名称无效
        """
        if root_key in RegistryManager.ROOT_KEYS:
            return RegistryManager.ROOT_KEYS[root_key]
        raise ValueError(f"无效的注册表根键: {root_key}")
    
    @staticmethod
    def get_value_type(value_type: str) -> int:
        """
        获取注册表值类型
        
        Args:
            value_type: 注册表值类型名称
            
        Returns:
            int: 值类型常量
            
        Raises:
            ValueError: 如果值类型名称无效
        """
        if value_type in RegistryManager.VALUE_TYPES:
            return RegistryManager.VALUE_TYPES[value_type]
        raise ValueError(f"无效的注册表值类型: {value_type}")
    
    @staticmethod
    def create_key(root_key: Union[str, int], sub_key: str) -> bool:
        """
        创建注册表键
        
        Args:
            root_key: 注册表根键的名称或句柄
            sub_key: 要创建的子键路径
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            if isinstance(root_key, str):
                root_key = RegistryManager.get_root_key(root_key)
            
            key, _ = winreg.CreateKeyEx(root_key, sub_key, 0, winreg.KEY_WRITE)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"创建注册表键失败: {str(e)}")
            return False
    
    @staticmethod
    def delete_key(root_key: Union[str, int], sub_key: str) -> bool:
        """
        删除注册表键
        
        Args:
            root_key: 注册表根键的名称或句柄
            sub_key: 要删除的子键路径
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            if isinstance(root_key, str):
                root_key = RegistryManager.get_root_key(root_key)
            
            winreg.DeleteKey(root_key, sub_key)
            return True
        except Exception as e:
            print(f"删除注册表键失败: {str(e)}")
            return False
    
    @staticmethod
    def set_value(root_key: Union[str, int], sub_key: str, value_name: str, 
                 value_data: Any, value_type: Union[str, int] = winreg.REG_SZ) -> bool:
        """
        设置注册表值
        
        Args:
            root_key: 注册表根键的名称或句柄
            sub_key: 子键路径
            value_name: 值名称
            value_data: 值数据
            value_type: 值类型
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            if isinstance(root_key, str):
                root_key = RegistryManager.get_root_key(root_key)
            
            if isinstance(value_type, str):
                value_type = RegistryManager.get_value_type(value_type)
            
            key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"设置注册表值失败: {str(e)}")
            return False
    
    @staticmethod
    def get_value(root_key: Union[str, int], sub_key: str, value_name: str = "") -> Tuple[Any, int]:
        """
        获取注册表值
        
        Args:
            root_key: 注册表根键的名称或句柄
            sub_key: 子键路径
            value_name: 值名称，默认为空字符串(默认值)
            
        Returns:
            tuple: (值数据, 值类型)，如果失败则返回(None, -1)
        """
        try:
            if isinstance(root_key, str):
                root_key = RegistryManager.get_root_key(root_key)
            
            key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ)
            value_data, value_type = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return (value_data, value_type)
        except Exception as e:
            print(f"获取注册表值失败: {str(e)}")
            return (None, -1)
    
    @staticmethod
    def delete_value(root_key: Union[str, int], sub_key: str, value_name: str) -> bool:
        """
        删除注册表值
        
        Args:
            root_key: 注册表根键的名称或句柄
            sub_key: 子键路径
            value_name: 值名称
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            if isinstance(root_key, str):
                root_key = RegistryManager.get_root_key(root_key)
            
            key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, value_name)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"删除注册表值失败: {str(e)}")
            return False
    
    @staticmethod
    def enum_keys(root_key: Union[str, int], sub_key: str) -> List[str]:
        """
        枚举注册表子键
        
        Args:
            root_key: 注册表根键的名称或句柄
            sub_key: 子键路径
            
        Returns:
            list: 子键名称列表，如果失败则返回空列表
        """
        result = []
        try:
            if isinstance(root_key, str):
                root_key = RegistryManager.get_root_key(root_key)
            
            key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ)
            
            i = 0
            while True:
                try:
                    sub_key_name = winreg.EnumKey(key, i)
                    result.append(sub_key_name)
                    i += 1
                except WindowsError:
                    break
            
            winreg.CloseKey(key)
        except Exception as e:
            print(f"枚举注册表子键失败: {str(e)}")
        
        return result
    
    @staticmethod
    def enum_values(root_key: Union[str, int], sub_key: str) -> List[Tuple[str, Any, int]]:
        """
        枚举注册表值
        
        Args:
            root_key: 注册表根键的名称或句柄
            sub_key: 子键路径
            
        Returns:
            list: 值信息列表 [(名称, 数据, 类型)...]，如果失败则返回空列表
        """
        result = []
        try:
            if isinstance(root_key, str):
                root_key = RegistryManager.get_root_key(root_key)
            
            key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ)
            
            i = 0
            while True:
                try:
                    value_name, value_data, value_type = winreg.EnumValue(key, i)
                    result.append((value_name, value_data, value_type))
                    i += 1
                except WindowsError:
                    break
            
            winreg.CloseKey(key)
        except Exception as e:
            print(f"枚举注册表值失败: {str(e)}")
        
        return result

class ContextMenuManager:
    """
    右键菜单管理类，提供右键菜单的查询、添加、修改和删除功能
    """
    
    # 右键菜单的主要注册表路径
    CLASSES_ROOT = "HKEY_CLASSES_ROOT"
    CURRENT_USER_CLASSES = r"HKEY_CURRENT_USER\Software\Classes"
    
    # 常见右键菜单上下文
    CONTEXTS = {
        "文件": "*\\shell",
        "文件夹": "Directory\\shell",
        "桌面背景": "Directory\\Background\\shell",
        "驱动器": "Drive\\shell",
        "所有对象": "*\\shell",
        "文本文件": "txtfile\\shell",
        "可执行文件": "exefile\\shell",
        "图片文件": "SystemFileAssociations\\.jpg\\shell",
    }
    
    def __init__(self):
        """初始化右键菜单管理器"""
        self.reg_manager = RegistryManager()
    
    def get_context_menu_items(self, context: str = "文件") -> List[Dict[str, Any]]:
        """
        获取指定上下文的右键菜单项
        
        Args:
            context: 右键菜单上下文，如"文件"、"文件夹"等
            
        Returns:
            list: 菜单项列表，每个菜单项为一个字典
        """
        result = []
        
        if context not in self.CONTEXTS:
            print(f"不支持的上下文: {context}")
            return result
        
        registry_path = self.CONTEXTS[context]
        
        # 先检查HKCU
        hkcu_items = self._get_items_from_path(self.CURRENT_USER_CLASSES, registry_path)
        for item in hkcu_items:
            item["source"] = "HKCU"
            result.append(item)
        
        # 再检查HKCR
        hkcr_items = self._get_items_from_path(self.CLASSES_ROOT, registry_path)
        for item in hkcr_items:
            # 跳过已经在HKCU中存在的项
            if any(r["name"] == item["name"] for r in result):
                continue
            item["source"] = "HKCR"
            result.append(item)
        
        return result
    
    def _get_items_from_path(self, root_key: str, registry_path: str) -> List[Dict[str, Any]]:
        """
        从指定注册表路径获取菜单项
        
        Args:
            root_key: 注册表根键
            registry_path: 注册表路径
            
        Returns:
            list: 菜单项列表
        """
        result = []
        
        try:
            # 获取所有子键
            menu_items = self.reg_manager.enum_keys(root_key, registry_path)
            
            # 解析每个菜单项
            for item_name in menu_items:
                # 跳过特殊项
                if item_name.startswith("Extended"):
                    continue
                
                item_path = f"{registry_path}\\{item_name}"
                
                # 获取菜单项信息
                item_info = {
                    "name": item_name,
                    "display_name": item_name,
                    "command": "",
                    "icon": "",
                    "position": "",
                    "extended": False,
                    "no_working_dir": False
                }
                
                # 获取显示名称
                display_name, _ = self.reg_manager.get_value(root_key, item_path)
                if display_name:
                    item_info["display_name"] = display_name
                
                # 检查是否有扩展菜单标记
                extended_value, _ = self.reg_manager.get_value(root_key, item_path, "Extended")
                if extended_value is not None:
                    item_info["extended"] = True
                
                # 获取位置
                position_value, _ = self.reg_manager.get_value(root_key, item_path, "Position")
                if position_value:
                    item_info["position"] = position_value
                
                # 获取图标
                icon_value, _ = self.reg_manager.get_value(root_key, item_path, "Icon")
                if icon_value:
                    item_info["icon"] = icon_value
                
                # 获取命令
                command_path = f"{item_path}\\command"
                try:
                    command_value, _ = self.reg_manager.get_value(root_key, command_path)
                    if command_value:
                        item_info["command"] = command_value
                except:
                    pass
                
                result.append(item_info)
        except Exception as e:
            print(f"获取菜单项失败: {str(e)}")
        
        return result
    
    def add_menu_item(self, context: str, name: str, command: str, 
                     display_name: str = None, icon: str = None, 
                     position: str = None, extended: bool = False) -> bool:
        """
        添加右键菜单项
        
        Args:
            context: 上下文，如"文件"、"文件夹"等
            name: 菜单项名称(注册表键名)
            command: 执行的命令
            display_name: 显示名称，默认与name相同
            icon: 图标路径，默认为空
            position: 位置，如"Top"或"Bottom"，默认为空
            extended: 是否为扩展菜单(Shift+右键)，默认为False
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        if not is_admin():
            print("添加菜单项需要管理员权限")
            return False
        
        if context not in self.CONTEXTS:
            print(f"不支持的上下文: {context}")
            return False
        
        if not display_name:
            display_name = name
        
        registry_path = self.CONTEXTS[context]
        item_path = f"{registry_path}\\{name}"
        command_path = f"{item_path}\\command"
        
        try:
            # 创建菜单项键
            if not self.reg_manager.create_key(self.CURRENT_USER_CLASSES, item_path):
                return False
            
            # 设置默认值(显示名称)
            if not self.reg_manager.set_value(self.CURRENT_USER_CLASSES, item_path, "", display_name):
                return False
            
            # 设置扩展菜单标记
            if extended:
                if not self.reg_manager.set_value(self.CURRENT_USER_CLASSES, item_path, "Extended", ""):
                    return False
            
            # 设置位置
            if position:
                if not self.reg_manager.set_value(self.CURRENT_USER_CLASSES, item_path, "Position", position):
                    return False
            
            # 设置图标
            if icon:
                if not self.reg_manager.set_value(self.CURRENT_USER_CLASSES, item_path, "Icon", icon):
                    return False
            
            # 创建命令键并设置命令
            if not self.reg_manager.create_key(self.CURRENT_USER_CLASSES, command_path):
                return False
            
            if not self.reg_manager.set_value(self.CURRENT_USER_CLASSES, command_path, "", command):
                return False
            
            # 刷新资源管理器
            refresh_explorer()
            
            return True
        except Exception as e:
            print(f"添加菜单项失败: {str(e)}")
            return False
    
    def delete_menu_item(self, context: str, name: str, source: str = "HKCU") -> bool:
        """
        删除右键菜单项
        
        Args:
            context: 上下文，如"文件"、"文件夹"等
            name: 菜单项名称(注册表键名)
            source: 菜单项来源，"HKCU"或"HKCR"
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        if not is_admin():
            print("删除菜单项需要管理员权限")
            return False
        
        if context not in self.CONTEXTS:
            print(f"不支持的上下文: {context}")
            return False
        
        registry_path = self.CONTEXTS[context]
        item_path = f"{registry_path}\\{name}"
        
        try:
            # 根据来源选择根键
            root_key = self.CURRENT_USER_CLASSES if source == "HKCU" else self.CLASSES_ROOT
            
            # 删除菜单项
            if not self.reg_manager.delete_key(root_key, f"{item_path}\\command"):
                return False
            
            if not self.reg_manager.delete_key(root_key, item_path):
                return False
            
            # 刷新资源管理器
            refresh_explorer()
            
            return True
        except Exception as e:
            print(f"删除菜单项失败: {str(e)}")
            return False
    
    def modify_menu_item(self, context: str, name: str, source: str,
                         new_command: str = None, new_display_name: str = None,
                         new_icon: str = None, new_position: str = None,
                         extended: bool = None) -> bool:
        """
        修改右键菜单项
        
        Args:
            context: 上下文，如"文件"、"文件夹"等
            name: 菜单项名称(注册表键名)
            source: 菜单项来源，"HKCU"或"HKCR"
            new_command: 新命令，为None则不修改
            new_display_name: 新显示名称，为None则不修改
            new_icon: 新图标路径，为None则不修改
            new_position: 新位置，为None则不修改
            extended: 是否为扩展菜单，为None则不修改
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        if not is_admin():
            print("修改菜单项需要管理员权限")
            return False
        
        if context not in self.CONTEXTS:
            print(f"不支持的上下文: {context}")
            return False
        
        registry_path = self.CONTEXTS[context]
        item_path = f"{registry_path}\\{name}"
        command_path = f"{item_path}\\command"
        
        try:
            # 根据来源选择根键
            root_key = self.CURRENT_USER_CLASSES if source == "HKCU" else self.CLASSES_ROOT
            
            # 修改显示名称
            if new_display_name is not None:
                if not self.reg_manager.set_value(root_key, item_path, "", new_display_name):
                    return False
            
            # 修改扩展菜单标记
            if extended is not None:
                if extended:
                    if not self.reg_manager.set_value(root_key, item_path, "Extended", ""):
                        return False
                else:
                    self.reg_manager.delete_value(root_key, item_path, "Extended")
            
            # 修改位置
            if new_position is not None:
                if new_position:
                    if not self.reg_manager.set_value(root_key, item_path, "Position", new_position):
                        return False
                else:
                    self.reg_manager.delete_value(root_key, item_path, "Position")
            
            # 修改图标
            if new_icon is not None:
                if new_icon:
                    if not self.reg_manager.set_value(root_key, item_path, "Icon", new_icon):
                        return False
                else:
                    self.reg_manager.delete_value(root_key, item_path, "Icon")
            
            # 修改命令
            if new_command is not None:
                if not self.reg_manager.set_value(root_key, command_path, "", new_command):
                    return False
            
            # 刷新资源管理器
            refresh_explorer()
            
            return True
        except Exception as e:
            print(f"修改菜单项失败: {str(e)}")
            return False
    
    def get_file_associations(self) -> List[str]:
        """
        获取已注册的文件类型列表
        
        Returns:
            list: 文件类型列表
        """
        extensions = []
        
        try:
            # 从HKEY_CLASSES_ROOT获取所有以点开头的子键
            all_keys = self.reg_manager.enum_keys(self.CLASSES_ROOT, "")
            extensions = [key for key in all_keys if key.startswith(".")]
        except Exception as e:
            print(f"获取文件类型失败: {str(e)}")
        
        return sorted(extensions) 