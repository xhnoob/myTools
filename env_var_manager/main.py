#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
环境变量管理器
用于查看和管理Windows系统环境变量的图形界面工具
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import winreg
import subprocess

class EnvVarManager:
    """环境变量管理器类"""
    
    def __init__(self, root=None):
        """初始化环境变量管理器"""
        self.is_standalone = root is None
        
        if self.is_standalone:
            # 作为独立应用运行时创建根窗口
            self.root = tk.Tk()
            self.root.title("环境变量管理器 by道相 抖音@慈悲剪辑")
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
        
        # 加载环境变量
        self.load_env_vars()
        
        if self.is_standalone:
            # 作为独立应用运行时启动主循环
            self.root.mainloop()
    
    def create_widgets(self):
        """创建UI组件"""
        # 创建页签控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 用户环境变量页签
        self.user_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.user_frame, text="用户环境变量")
        
        # 系统环境变量页签
        self.system_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.system_frame, text="系统环境变量")
        
        # 路径环境变量页签
        self.path_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.path_frame, text="PATH变量")
        
        # 设置各页签内容
        self.setup_user_vars_tab()
        self.setup_system_vars_tab()
        self.setup_path_tab()
        
        # 创建按钮框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # 刷新按钮
        self.refresh_button = ttk.Button(self.button_frame, text="刷新", command=self.load_env_vars)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 应用更改按钮
        self.apply_button = ttk.Button(self.button_frame, text="应用更改", command=self.apply_changes)
        self.apply_button.pack(side=tk.RIGHT, padx=5)
    
    def setup_user_vars_tab(self):
        """设置用户环境变量页签"""
        # 创建工具栏
        toolbar = ttk.Frame(self.user_frame)
        toolbar.pack(fill=tk.X, pady=5)
        
        # 添加按钮
        add_button = ttk.Button(toolbar, text="添加", command=lambda: self.add_env_var("user"))
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 编辑按钮
        edit_button = ttk.Button(toolbar, text="编辑", command=lambda: self.edit_env_var("user"))
        edit_button.pack(side=tk.LEFT, padx=5)
        
        # 删除按钮
        delete_button = ttk.Button(toolbar, text="删除", command=lambda: self.delete_env_var("user"))
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # 创建Treeview
        columns = ("name", "value")
        self.user_tree = ttk.Treeview(self.user_frame, columns=columns, show="headings")
        self.user_tree.heading("name", text="变量名")
        self.user_tree.heading("value", text="变量值")
        self.user_tree.column("name", width=200)
        self.user_tree.column("value", width=600)
        self.user_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.user_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        # 双击编辑
        self.user_tree.bind("<Double-1>", lambda event: self.edit_env_var("user"))
    
    def setup_system_vars_tab(self):
        """设置系统环境变量页签"""
        # 创建工具栏
        toolbar = ttk.Frame(self.system_frame)
        toolbar.pack(fill=tk.X, pady=5)
        
        # 添加按钮
        add_button = ttk.Button(toolbar, text="添加", command=lambda: self.add_env_var("system"))
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 编辑按钮
        edit_button = ttk.Button(toolbar, text="编辑", command=lambda: self.edit_env_var("system"))
        edit_button.pack(side=tk.LEFT, padx=5)
        
        # 删除按钮
        delete_button = ttk.Button(toolbar, text="删除", command=lambda: self.delete_env_var("system"))
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # 创建Treeview
        columns = ("name", "value")
        self.system_tree = ttk.Treeview(self.system_frame, columns=columns, show="headings")
        self.system_tree.heading("name", text="变量名")
        self.system_tree.heading("value", text="变量值")
        self.system_tree.column("name", width=200)
        self.system_tree.column("value", width=600)
        self.system_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.system_frame, orient=tk.VERTICAL, command=self.system_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.system_tree.configure(yscrollcommand=scrollbar.set)
        
        # 双击编辑
        self.system_tree.bind("<Double-1>", lambda event: self.edit_env_var("system"))
    
    def setup_path_tab(self):
        """设置PATH环境变量页签"""
        # 创建工具栏
        toolbar = ttk.Frame(self.path_frame)
        toolbar.pack(fill=tk.X, pady=5)
        
        # 路径类型选择
        self.path_type = tk.StringVar(value="user")
        user_radio = ttk.Radiobutton(toolbar, text="用户PATH", variable=self.path_type, 
                                    value="user", command=self.load_path_var)
        user_radio.pack(side=tk.LEFT, padx=5)
        
        system_radio = ttk.Radiobutton(toolbar, text="系统PATH", variable=self.path_type, 
                                      value="system", command=self.load_path_var)
        system_radio.pack(side=tk.LEFT, padx=5)
        
        # 添加按钮
        add_button = ttk.Button(toolbar, text="添加路径", command=self.add_path)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 编辑按钮
        edit_button = ttk.Button(toolbar, text="编辑路径", command=self.edit_path)
        edit_button.pack(side=tk.LEFT, padx=5)
        
        # 删除按钮
        delete_button = ttk.Button(toolbar, text="删除路径", command=self.delete_path)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # 上移按钮
        up_button = ttk.Button(toolbar, text="上移", command=lambda: self.move_path("up"))
        up_button.pack(side=tk.LEFT, padx=5)
        
        # 下移按钮
        down_button = ttk.Button(toolbar, text="下移", command=lambda: self.move_path("down"))
        down_button.pack(side=tk.LEFT, padx=5)
        
        # 创建Treeview
        columns = ("path",)
        self.path_tree = ttk.Treeview(self.path_frame, columns=columns, show="headings")
        self.path_tree.heading("path", text="路径")
        self.path_tree.column("path", width=800)
        self.path_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.path_frame, orient=tk.VERTICAL, command=self.path_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.path_tree.configure(yscrollcommand=scrollbar.set)
        
        # 双击编辑
        self.path_tree.bind("<Double-1>", lambda event: self.edit_path())
    
    def load_env_vars(self):
        """加载环境变量"""
        self.load_user_vars()
        self.load_system_vars()
        self.load_path_var()
    
    def load_user_vars(self):
        """加载用户环境变量"""
        # 清空树
        self.user_tree.delete(*self.user_tree.get_children())
        
        try:
            # 打开注册表
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
            
            # 遍历环境变量
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    # 只显示非PATH变量
                    if name.upper() != "PATH":
                        self.user_tree.insert("", tk.END, values=(name, value))
                    i += 1
                except WindowsError:
                    break
            
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("错误", f"加载用户环境变量时出错: {str(e)}")
    
    def load_system_vars(self):
        """加载系统环境变量"""
        # 清空树
        self.system_tree.delete(*self.system_tree.get_children())
        
        try:
            # 打开注册表
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
            
            # 遍历环境变量
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    # 只显示非PATH变量
                    if name.upper() != "PATH":
                        self.system_tree.insert("", tk.END, values=(name, value))
                    i += 1
                except WindowsError:
                    break
            
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("错误", f"加载系统环境变量时出错: {str(e)}")
    
    def load_path_var(self):
        """加载PATH环境变量"""
        # 清空树
        self.path_tree.delete(*self.path_tree.get_children())
        
        try:
            path_type = self.path_type.get()
            
            if path_type == "user":
                # 用户PATH
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
            else:
                # 系统PATH
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
            
            # 获取PATH值
            path, _ = winreg.QueryValueEx(key, "PATH")
            
            # 分割PATH
            paths = path.split(";")
            
            # 添加到树
            for p in paths:
                if p.strip():  # 不显示空路径
                    self.path_tree.insert("", tk.END, values=(p,))
            
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("错误", f"加载PATH变量时出错: {str(e)}")
    
    def add_env_var(self, var_type):
        """添加环境变量"""
        # 获取变量名和值
        name = simpledialog.askstring("添加环境变量", "请输入变量名:")
        if not name:
            return
        
        value = simpledialog.askstring("添加环境变量", "请输入变量值:")
        if value is None:  # 用户取消
            return
        
        try:
            # 根据类型选择注册表键
            if var_type == "user":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
                self.user_tree.insert("", tk.END, values=(name, value))
            else:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                    0, winreg.KEY_SET_VALUE)
                self.system_tree.insert("", tk.END, values=(name, value))
            
            # 设置环境变量
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
            
            # 广播环境变量更改消息
            self.broadcast_env_change()
            
            messagebox.showinfo("成功", f"环境变量 {name} 已添加")
        except Exception as e:
            messagebox.showerror("错误", f"添加环境变量时出错: {str(e)}")
    
    def edit_env_var(self, var_type):
        """编辑环境变量"""
        # 获取选中的项
        if var_type == "user":
            selected = self.user_tree.selection()
            if not selected:
                messagebox.showinfo("提示", "请先选择一个用户环境变量")
                return
            
            item = self.user_tree.item(selected[0])
            tree = self.user_tree
            key_path = r"Environment"
            root_key = winreg.HKEY_CURRENT_USER
        else:
            selected = self.system_tree.selection()
            if not selected:
                messagebox.showinfo("提示", "请先选择一个系统环境变量")
                return
            
            item = self.system_tree.item(selected[0])
            tree = self.system_tree
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            root_key = winreg.HKEY_LOCAL_MACHINE
        
        # 获取当前值
        name, old_value = item["values"]
        
        # 获取新值
        new_value = simpledialog.askstring("编辑环境变量", "请输入新的变量值:", initialvalue=old_value)
        if new_value is None:  # 用户取消
            return
        
        try:
            # 打开注册表
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_SET_VALUE)
            
            # 更新环境变量
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, new_value)
            winreg.CloseKey(key)
            
            # 更新树
            tree.item(selected[0], values=(name, new_value))
            
            # 广播环境变量更改消息
            self.broadcast_env_change()
            
            messagebox.showinfo("成功", f"环境变量 {name} 已更新")
        except Exception as e:
            messagebox.showerror("错误", f"更新环境变量时出错: {str(e)}")
    
    def delete_env_var(self, var_type):
        """删除环境变量"""
        # 获取选中的项
        if var_type == "user":
            selected = self.user_tree.selection()
            if not selected:
                messagebox.showinfo("提示", "请先选择一个用户环境变量")
                return
            
            item = self.user_tree.item(selected[0])
            tree = self.user_tree
            key_path = r"Environment"
            root_key = winreg.HKEY_CURRENT_USER
        else:
            selected = self.system_tree.selection()
            if not selected:
                messagebox.showinfo("提示", "请先选择一个系统环境变量")
                return
            
            item = self.system_tree.item(selected[0])
            tree = self.system_tree
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            root_key = winreg.HKEY_LOCAL_MACHINE
        
        # 获取变量名
        name = item["values"][0]
        
        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除环境变量 {name} 吗?"):
            return
        
        try:
            # 打开注册表
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_SET_VALUE)
            
            # 删除环境变量
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            
            # 从树中删除
            tree.delete(selected[0])
            
            # 广播环境变量更改消息
            self.broadcast_env_change()
            
            messagebox.showinfo("成功", f"环境变量 {name} 已删除")
        except Exception as e:
            messagebox.showerror("错误", f"删除环境变量时出错: {str(e)}")
    
    def add_path(self):
        """添加PATH路径"""
        # 获取路径
        path = simpledialog.askstring("添加路径", "请输入新的路径:")
        if not path:
            return
        
        try:
            path_type = self.path_type.get()
            
            if path_type == "user":
                key_path = r"Environment"
                root_key = winreg.HKEY_CURRENT_USER
            else:
                key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                root_key = winreg.HKEY_LOCAL_MACHINE
            
            # 打开注册表
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE)
            
            # 获取当前PATH
            current_path, _ = winreg.QueryValueEx(key, "PATH")
            
            # 添加新路径
            new_path = current_path
            if not new_path.endswith(";"):
                new_path += ";"
            new_path += path
            
            # 更新PATH
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            
            # 更新树
            self.path_tree.insert("", tk.END, values=(path,))
            
            # 广播环境变量更改消息
            self.broadcast_env_change()
            
            messagebox.showinfo("成功", "PATH路径已添加")
        except Exception as e:
            messagebox.showerror("错误", f"添加PATH路径时出错: {str(e)}")
    
    def edit_path(self):
        """编辑PATH路径"""
        # 获取选中的项
        selected = self.path_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个PATH路径")
            return
        
        item = self.path_tree.item(selected[0])
        old_path = item["values"][0]
        
        # 获取新路径
        new_path = simpledialog.askstring("编辑路径", "请输入新的路径:", initialvalue=old_path)
        if new_path is None:  # 用户取消
            return
        
        try:
            path_type = self.path_type.get()
            
            if path_type == "user":
                key_path = r"Environment"
                root_key = winreg.HKEY_CURRENT_USER
            else:
                key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                root_key = winreg.HKEY_LOCAL_MACHINE
            
            # 打开注册表
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE)
            
            # 获取当前PATH
            current_path, _ = winreg.QueryValueEx(key, "PATH")
            
            # 替换路径
            paths = current_path.split(";")
            for i, p in enumerate(paths):
                if p == old_path:
                    paths[i] = new_path
                    break
            
            # 更新PATH
            new_path_str = ";".join(paths)
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path_str)
            winreg.CloseKey(key)
            
            # 更新树
            self.path_tree.item(selected[0], values=(new_path,))
            
            # 广播环境变量更改消息
            self.broadcast_env_change()
            
            messagebox.showinfo("成功", "PATH路径已更新")
        except Exception as e:
            messagebox.showerror("错误", f"更新PATH路径时出错: {str(e)}")
    
    def delete_path(self):
        """删除PATH路径"""
        # 获取选中的项
        selected = self.path_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个PATH路径")
            return
        
        item = self.path_tree.item(selected[0])
        path = item["values"][0]
        
        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除PATH路径 {path} 吗?"):
            return
        
        try:
            path_type = self.path_type.get()
            
            if path_type == "user":
                key_path = r"Environment"
                root_key = winreg.HKEY_CURRENT_USER
            else:
                key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                root_key = winreg.HKEY_LOCAL_MACHINE
            
            # 打开注册表
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE)
            
            # 获取当前PATH
            current_path, _ = winreg.QueryValueEx(key, "PATH")
            
            # 删除路径
            paths = current_path.split(";")
            paths = [p for p in paths if p != path]
            
            # 更新PATH
            new_path = ";".join(paths)
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            
            # 从树中删除
            self.path_tree.delete(selected[0])
            
            # 广播环境变量更改消息
            self.broadcast_env_change()
            
            messagebox.showinfo("成功", "PATH路径已删除")
        except Exception as e:
            messagebox.showerror("错误", f"删除PATH路径时出错: {str(e)}")
    
    def move_path(self, direction):
        """移动PATH路径"""
        # 获取选中的项
        selected = self.path_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个PATH路径")
            return
        
        selected_id = selected[0]
        all_items = self.path_tree.get_children()
        current_index = all_items.index(selected_id)
        
        if direction == "up" and current_index > 0:
            new_index = current_index - 1
        elif direction == "down" and current_index < len(all_items) - 1:
            new_index = current_index + 1
        else:
            return  # 已经在顶部或底部
        
        try:
            path_type = self.path_type.get()
            
            if path_type == "user":
                key_path = r"Environment"
                root_key = winreg.HKEY_CURRENT_USER
            else:
                key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                root_key = winreg.HKEY_LOCAL_MACHINE
            
            # 打开注册表
            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE)
            
            # 获取所有路径
            paths = []
            for item_id in all_items:
                path = self.path_tree.item(item_id)["values"][0]
                paths.append(path)
            
            # 移动路径
            path = paths.pop(current_index)
            paths.insert(new_index, path)
            
            # 更新PATH
            new_path = ";".join(paths)
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            
            # 刷新显示
            self.load_path_var()
            
            # 重新选中移动后的项
            new_selected = self.path_tree.get_children()[new_index]
            self.path_tree.selection_set(new_selected)
            self.path_tree.see(new_selected)
            
            # 广播环境变量更改消息
            self.broadcast_env_change()
        except Exception as e:
            messagebox.showerror("错误", f"移动PATH路径时出错: {str(e)}")
    
    def apply_changes(self):
        """应用环境变量更改"""
        try:
            self.broadcast_env_change()
            messagebox.showinfo("成功", "环境变量更改已应用")
        except Exception as e:
            messagebox.showerror("错误", f"应用环境变量更改时出错: {str(e)}")
    
    def broadcast_env_change(self):
        """广播环境变量更改消息"""
        # 发送WM_SETTINGCHANGE消息
        import ctypes
        from ctypes import wintypes
        
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

def main():
    """主函数"""
    app = EnvVarManager()

if __name__ == "__main__":
    main() 