#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
Python版本管理器的UI界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import json
from utils import (
    find_python_installations,
    get_current_python_version,
    set_python_version,
    list_installed_packages,
    install_package,
    uninstall_package,
    update_package,
    is_admin,
    get_current_pip_index,
    set_pip_index,
    list_pip_indices,
    add_custom_pip_index
)

class PyVersionManagerApp:
    """Python版本管理器的主应用类"""
    
    def __init__(self, root):
        """初始化应用"""
        self.root = root
        self.root.title("Python版本管理器 by道相 抖音@慈悲剪辑")
        self.root.geometry("850x600")
        self.root.minsize(800, 500)
        
        # 设置应用图标
        try:
            self.root.iconbitmap("python.ico")
        except:
            pass  # 如果图标文件不存在，则忽略
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use("clam")  # 使用clam主题
        
        # 创建并配置框架
        self.setup_frames()
        
        # 创建控件
        self.setup_widgets()
        
        # 绑定事件
        self.bind_events()
        
        # 加载数据
        self.load_data()
        
        # 检查当前用户是否为管理员
        if not is_admin():
            messagebox.showwarning(
                "权限警告", 
                "程序没有以管理员权限运行。\n"
                "切换Python版本可能需要管理员权限。\n"
                "请以管理员身份重新启动程序。"
            )
    
    def setup_frames(self):
        """设置应用的框架"""
        # 顶部框架
        self.top_frame = ttk.Frame(self.root, padding=10)
        self.top_frame.pack(fill=tk.X)
        
        # 中间框架 - 使用Notebook创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 版本管理标签页
        self.version_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.version_frame, text="Python版本管理")
        
        # 包管理标签页
        self.package_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.package_frame, text="包管理")
        
        # 新增：源管理标签页
        self.source_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.source_frame, text="源管理")
        
        # 底部框架
        self.bottom_frame = ttk.Frame(self.root, padding=10)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 分割版本管理框架
        self.version_left_frame = ttk.Frame(self.version_frame)
        self.version_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.version_right_frame = ttk.Frame(self.version_frame)
        self.version_right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # 分割包管理框架
        self.package_top_frame = ttk.Frame(self.package_frame)
        self.package_top_frame.pack(fill=tk.X)
        
        self.package_middle_frame = ttk.Frame(self.package_frame)
        self.package_middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.package_bottom_frame = ttk.Frame(self.package_frame)
        self.package_bottom_frame.pack(fill=tk.X)
        
        # 新增：分割源管理框架
        self.source_top_frame = ttk.Frame(self.source_frame)
        self.source_top_frame.pack(fill=tk.X)
        
        self.source_middle_frame = ttk.Frame(self.source_frame)
        self.source_middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.source_bottom_frame = ttk.Frame(self.source_frame)
        self.source_bottom_frame.pack(fill=tk.X)
    
    def setup_widgets(self):
        """设置应用的控件"""
        # 顶部框架控件
        self.current_version_label = ttk.Label(self.top_frame, text="当前系统Python版本: 检测中...")
        self.current_version_label.pack(side=tk.LEFT)
        
        self.refresh_button = ttk.Button(self.top_frame, text="刷新", command=self.load_data)
        self.refresh_button.pack(side=tk.RIGHT)
        
        # ------------ 版本管理标签页控件 ------------
        # 左侧 - 版本列表
        self.version_listbox_label = ttk.Label(self.version_left_frame, text="系统中检测到的Python版本:")
        self.version_listbox_label.pack(anchor=tk.W)
        
        # 使用Treeview替代Listbox以显示更多信息
        self.version_tree = ttk.Treeview(self.version_left_frame, columns=("版本", "路径"), show="headings")
        self.version_tree.heading("版本", text="版本")
        self.version_tree.heading("路径", text="路径")
        self.version_tree.column("版本", width=100)
        self.version_tree.column("路径", width=400)
        self.version_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        version_scrollbar = ttk.Scrollbar(self.version_left_frame, orient=tk.VERTICAL, command=self.version_tree.yview)
        version_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.version_tree.configure(yscrollcommand=version_scrollbar.set)
        
        # 右侧 - 操作按钮
        self.scan_button = ttk.Button(self.version_right_frame, text="扫描版本", command=self.scan_versions)
        self.scan_button.pack(fill=tk.X, pady=5)
        
        self.switch_button = ttk.Button(self.version_right_frame, text="切换到所选版本", command=self.switch_version)
        self.switch_button.pack(fill=tk.X, pady=5)
        
        # ------------ 包管理标签页控件 ------------
        # 顶部 - 选择Python版本
        self.package_version_label = ttk.Label(self.package_top_frame, text="选择Python版本:")
        self.package_version_label.pack(side=tk.LEFT)
        
        self.package_version_combobox = ttk.Combobox(self.package_top_frame, state="readonly")
        self.package_version_combobox.pack(side=tk.LEFT, padx=5)
        
        self.load_packages_button = ttk.Button(self.package_top_frame, text="加载包列表", command=self.load_packages)
        self.load_packages_button.pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        self.search_label = ttk.Label(self.package_top_frame, text="搜索:")
        self.search_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.search_entry = ttk.Entry(self.package_top_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_button = ttk.Button(self.package_top_frame, text="搜索", command=self.search_packages)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        # 中间 - 包列表
        # 使用Treeview显示包信息
        self.package_tree = ttk.Treeview(self.package_middle_frame, columns=("名称", "版本", "描述"), show="headings")
        self.package_tree.heading("名称", text="名称")
        self.package_tree.heading("版本", text="版本")
        self.package_tree.heading("描述", text="描述")
        self.package_tree.column("名称", width=150)
        self.package_tree.column("版本", width=80)
        self.package_tree.column("描述", width=300)
        self.package_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        package_scrollbar = ttk.Scrollbar(self.package_middle_frame, orient=tk.VERTICAL, command=self.package_tree.yview)
        package_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.package_tree.configure(yscrollcommand=package_scrollbar.set)
        
        # 底部 - 操作按钮
        self.install_button = ttk.Button(self.package_bottom_frame, text="安装新包", command=self.install_new_package)
        self.install_button.pack(side=tk.LEFT, padx=5)
        
        self.uninstall_button = ttk.Button(self.package_bottom_frame, text="卸载所选包", command=self.uninstall_package)
        self.uninstall_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = ttk.Button(self.package_bottom_frame, text="更新所选包", command=self.update_package)
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        # ------------ 新增：源管理标签页控件 ------------
        # 顶部 - 选择Python版本
        self.source_version_label = ttk.Label(self.source_top_frame, text="选择Python版本:")
        self.source_version_label.pack(side=tk.LEFT)
        
        self.source_version_combobox = ttk.Combobox(self.source_top_frame, state="readonly")
        self.source_version_combobox.pack(side=tk.LEFT, padx=5)
        
        self.check_source_button = ttk.Button(self.source_top_frame, text="检查当前源", command=self.check_current_source)
        self.check_source_button.pack(side=tk.LEFT, padx=5)
        
        # 当前源显示
        self.current_source_label = ttk.Label(self.source_top_frame, text="当前源: ")
        self.current_source_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.current_source_value = ttk.Label(self.source_top_frame, text="未检测")
        self.current_source_value.pack(side=tk.LEFT)
        
        # 中间 - 源列表
        # 使用Treeview显示源信息
        self.source_tree = ttk.Treeview(self.source_middle_frame, columns=("名称", "URL"), show="headings")
        self.source_tree.heading("名称", text="名称")
        self.source_tree.heading("URL", text="URL")
        self.source_tree.column("名称", width=150)
        self.source_tree.column("URL", width=400)
        self.source_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        source_scrollbar = ttk.Scrollbar(self.source_middle_frame, orient=tk.VERTICAL, command=self.source_tree.yview)
        source_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.source_tree.configure(yscrollcommand=source_scrollbar.set)
        
        # 底部 - 操作按钮
        self.switch_source_button = ttk.Button(self.source_bottom_frame, text="切换到所选源", command=self.switch_source)
        self.switch_source_button.pack(side=tk.LEFT, padx=5)
        
        self.add_source_button = ttk.Button(self.source_bottom_frame, text="添加自定义源", command=self.add_custom_source)
        self.add_source_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_source_button = ttk.Button(self.source_bottom_frame, text="刷新源列表", command=self.refresh_source_list)
        self.refresh_source_button.pack(side=tk.LEFT, padx=5)
        
        # 底部框架控件
        self.status_label = ttk.Label(self.bottom_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)
    
    def bind_events(self):
        """绑定事件"""
        # 当包版本下拉框选择改变时，自动加载包列表
        self.package_version_combobox.bind("<<ComboboxSelected>>", lambda e: self.load_packages())
        
        # 当搜索框按下回车键时，触发搜索
        self.search_entry.bind("<Return>", lambda e: self.search_packages())
        
        # 双击版本列表中的版本时切换到该版本
        self.version_tree.bind("<Double-1>", lambda e: self.switch_version())
        
        # 双击包列表中的包时，显示详细信息
        self.package_tree.bind("<Double-1>", lambda e: self.show_package_info())
        
        # 新增：当源版本下拉框选择改变时，自动检查当前源
        self.source_version_combobox.bind("<<ComboboxSelected>>", lambda e: self.check_current_source())
        
        # 新增：双击源列表中的源时切换到该源
        self.source_tree.bind("<Double-1>", lambda e: self.switch_source())
    
    def load_data(self):
        """加载应用数据"""
        self.status_label.config(text="正在加载数据...")
        self.root.update()
        
        # 创建线程加载数据，避免UI卡顿
        threading.Thread(target=self._load_data_thread, daemon=True).start()
    
    def _load_data_thread(self):
        """在后台线程中加载数据"""
        # 获取当前Python版本
        current_version = get_current_python_version()
        
        # 获取系统中的所有Python版本
        python_installations = find_python_installations()
        
        # 更新UI（在主线程中）
        self.root.after(0, lambda: self._update_ui_with_data(current_version, python_installations))
    
    def _update_ui_with_data(self, current_version, python_installations):
        """在主线程中更新UI"""
        # 更新当前版本标签
        self.current_version_label.config(text=f"当前系统Python版本: {current_version['version']} ({current_version['path']})")
        
        # 清空版本树
        for item in self.version_tree.get_children():
            self.version_tree.delete(item)
        
        # 填充版本树
        for i, installation in enumerate(python_installations):
            self.version_tree.insert("", tk.END, values=(installation["version"], installation["path"]))
        
        # 更新包管理标签页的下拉框
        versions = [f"{inst['version']} ({inst['path']})" for inst in python_installations]
        self.package_version_combobox["values"] = versions
        if self.package_version_combobox["values"]:
            self.package_version_combobox.current(0)
        
        # 新增：更新源管理标签页的下拉框
        self.source_version_combobox["values"] = versions
        if self.source_version_combobox["values"]:
            self.source_version_combobox.current(0)
            # 自动检查当前源
            self.check_current_source()
        
        # 新增：加载常用源列表
        self.refresh_source_list()
        
        self.status_label.config(text="数据加载完成")
    
    def scan_versions(self):
        """扫描系统中的Python版本"""
        self.status_label.config(text="正在扫描Python版本...")
        self.root.update()
        
        # 创建线程扫描版本，避免UI卡顿
        threading.Thread(target=self._scan_versions_thread, daemon=True).start()
    
    def _scan_versions_thread(self):
        """在后台线程中扫描版本"""
        # 获取系统中的所有Python版本
        python_installations = find_python_installations()
        
        # 更新UI（在主线程中）
        self.root.after(0, lambda: self._update_ui_with_versions(python_installations))
    
    def _update_ui_with_versions(self, python_installations):
        """在主线程中更新UI的版本信息"""
        # 清空版本树
        for item in self.version_tree.get_children():
            self.version_tree.delete(item)
        
        # 填充版本树
        for i, installation in enumerate(python_installations):
            self.version_tree.insert("", tk.END, values=(installation["version"], installation["path"]))
        
        # 更新包管理标签页的下拉框
        self.package_version_combobox["values"] = [f"{inst['version']} ({inst['path']})" for inst in python_installations]
        if self.package_version_combobox["values"]:
            self.package_version_combobox.current(0)
        
        self.status_label.config(text=f"扫描完成，找到 {len(python_installations)} 个Python安装")
    
    def switch_version(self):
        """切换到所选Python版本"""
        # 获取所选版本
        selected_items = self.version_tree.selection()
        if not selected_items:
            messagebox.showwarning("未选择版本", "请先选择一个Python版本")
            return
        
        item = selected_items[0]
        version, path = self.version_tree.item(item, "values")
        
        # 确认切换
        if not messagebox.askyesno("确认切换", f"确定要将系统Python版本切换到 {version} ({path})？\n\n这将修改系统环境变量。"):
            return
        
        self.status_label.config(text=f"正在切换Python版本到 {version}...")
        self.root.update()
        
        # 创建线程切换版本，避免UI卡顿
        threading.Thread(target=self._switch_version_thread, args=(path,), daemon=True).start()
    
    def _switch_version_thread(self, python_path):
        """在后台线程中切换版本"""
        # 切换版本
        success, message = set_python_version(python_path)
        
        # 更新UI（在主线程中）
        self.root.after(0, lambda: self._update_ui_after_switch(success, message))
    
    def _update_ui_after_switch(self, success, message):
        """在主线程中更新切换版本后的UI"""
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)
        
        # 重新加载数据
        self.load_data()
    
    def load_packages(self):
        """加载所选Python版本的已安装包列表"""
        # 获取所选版本
        version_str = self.package_version_combobox.get()
        if not version_str:
            messagebox.showwarning("未选择版本", "请先选择一个Python版本")
            return
        
        # 从下拉框的显示文本中提取路径
        path = version_str.split("(")[1].rstrip(")")
        
        self.status_label.config(text=f"正在加载 {path} 的包列表...")
        self.root.update()
        
        # 创建线程加载包列表，避免UI卡顿
        threading.Thread(target=self._load_packages_thread, args=(path,), daemon=True).start()
    
    def _load_packages_thread(self, python_path):
        """在后台线程中加载包列表"""
        # 获取包列表
        packages = list_installed_packages(python_path)
        
        # 更新UI（在主线程中）
        self.root.after(0, lambda: self._update_ui_with_packages(packages))
    
    def _update_ui_with_packages(self, packages):
        """在主线程中更新UI的包列表"""
        # 清空包树
        for item in self.package_tree.get_children():
            self.package_tree.delete(item)
        
        # 填充包树
        for package in packages:
            self.package_tree.insert("", tk.END, values=(
                package["name"], 
                package["version"], 
                package.get("description", "无描述")
            ))
        
        self.status_label.config(text=f"已加载 {len(packages)} 个包")
    
    def search_packages(self):
        """搜索包"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            # 如果搜索词为空，则显示所有包
            self.load_packages()
            return
        
        # 遍历包树中的所有项
        for item in self.package_tree.get_children():
            values = self.package_tree.item(item, "values")
            name = values[0].lower()
            description = values[2].lower() if len(values) > 2 else ""
            
            # 如果包名或描述包含搜索词，则显示；否则隐藏
            if search_term in name or search_term in description:
                self.package_tree.item(item, tags=())
            else:
                self.package_tree.detach(item)  # 从树中分离但不删除
        
        self.status_label.config(text=f"显示搜索结果: {search_term}")
    
    def install_new_package(self):
        """安装新包"""
        # 获取所选版本
        version_str = self.package_version_combobox.get()
        if not version_str:
            messagebox.showwarning("未选择版本", "请先选择一个Python版本")
            return
        
        # 从下拉框的显示文本中提取路径
        path = version_str.split("(")[1].rstrip(")")
        
        # 询问要安装的包名
        package_name = simpledialog.askstring("安装新包", "请输入要安装的包名:")
        if not package_name:
            return
        
        self.status_label.config(text=f"正在安装包: {package_name}...")
        self.root.update()
        
        # 创建线程安装包，避免UI卡顿
        threading.Thread(target=self._install_package_thread, args=(path, package_name), daemon=True).start()
    
    def _install_package_thread(self, python_path, package_name):
        """在后台线程中安装包"""
        # 安装包
        success, message = install_package(python_path, package_name)
        
        # 更新UI（在主线程中）
        self.root.after(0, lambda: self._update_ui_after_package_operation(success, message))
    
    def uninstall_package(self):
        """卸载所选包"""
        # 获取所选版本
        version_str = self.package_version_combobox.get()
        if not version_str:
            messagebox.showwarning("未选择版本", "请先选择一个Python版本")
            return
        
        # 获取所选包
        selected_items = self.package_tree.selection()
        if not selected_items:
            messagebox.showwarning("未选择包", "请先选择一个要卸载的包")
            return
        
        item = selected_items[0]
        package_name = self.package_tree.item(item, "values")[0]
        
        # 从下拉框的显示文本中提取路径
        path = version_str.split("(")[1].rstrip(")")
        
        # 确认卸载
        if not messagebox.askyesno("确认卸载", f"确定要卸载 {package_name}？"):
            return
        
        self.status_label.config(text=f"正在卸载包: {package_name}...")
        self.root.update()
        
        # 创建线程卸载包，避免UI卡顿
        threading.Thread(target=self._uninstall_package_thread, args=(path, package_name), daemon=True).start()
    
    def _uninstall_package_thread(self, python_path, package_name):
        """在后台线程中卸载包"""
        # 卸载包
        success, message = uninstall_package(python_path, package_name)
        
        # 更新UI（在主线程中）
        self.root.after(0, lambda: self._update_ui_after_package_operation(success, message))
    
    def update_package(self):
        """更新所选包"""
        # 获取所选版本
        version_str = self.package_version_combobox.get()
        if not version_str:
            messagebox.showwarning("未选择版本", "请先选择一个Python版本")
            return
        
        # 获取所选包
        selected_items = self.package_tree.selection()
        if not selected_items:
            messagebox.showwarning("未选择包", "请先选择一个要更新的包")
            return
        
        item = selected_items[0]
        package_name = self.package_tree.item(item, "values")[0]
        
        # 从下拉框的显示文本中提取路径
        path = version_str.split("(")[1].rstrip(")")
        
        self.status_label.config(text=f"正在更新包: {package_name}...")
        self.root.update()
        
        # 创建线程更新包，避免UI卡顿
        threading.Thread(target=self._update_package_thread, args=(path, package_name), daemon=True).start()
    
    def _update_package_thread(self, python_path, package_name):
        """在后台线程中更新包"""
        # 更新包
        success, message = update_package(python_path, package_name)
        
        # 更新UI（在主线程中）
        self.root.after(0, lambda: self._update_ui_after_package_operation(success, message))
    
    def _update_ui_after_package_operation(self, success, message):
        """在主线程中更新包操作后的UI"""
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)
        
        # 重新加载包列表
        self.load_packages()
    
    def show_package_info(self):
        """显示所选包的详细信息"""
        # 获取所选包
        selected_items = self.package_tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        values = self.package_tree.item(item, "values")
        package_name = values[0]
        package_version = values[1]
        package_description = values[2] if len(values) > 2 else "无描述"
        
        # 显示包信息对话框
        messagebox.showinfo(
            f"{package_name} 信息", 
            f"包名: {package_name}\n"
            f"版本: {package_version}\n"
            f"描述: {package_description}\n"
        )
    
    # 新增：源管理相关方法
    def check_current_source(self):
        """检查所选Python版本当前使用的源"""
        # 获取所选版本
        version_str = self.source_version_combobox.get()
        if not version_str:
            messagebox.showwarning("未选择版本", "请先选择一个Python版本")
            return
        
        # 从下拉框的显示文本中提取路径
        path = version_str.split("(")[1].rstrip(")")
        
        self.status_label.config(text=f"正在检查 {path} 的当前源...")
        self.root.update()
        
        # 创建线程检查当前源，避免UI卡顿
        threading.Thread(target=self._check_current_source_thread, args=(path,), daemon=True).start()
    
    def _check_current_source_thread(self, python_path):
        """在后台线程中检查当前源"""
        # 获取当前源
        current_index = get_current_pip_index(python_path)
        
        # 更新UI（在主线程中）
        self.root.after(0, lambda: self._update_ui_with_current_source(current_index))
    
    def _update_ui_with_current_source(self, current_index):
        """在主线程中更新UI的当前源信息"""
        self.current_source_value.config(text=current_index)
        self.status_label.config(text="当前源检查完成")
    
    def refresh_source_list(self):
        """刷新源列表"""
        # 获取源列表
        sources = list_pip_indices()
        
        # 清空源树
        for item in self.source_tree.get_children():
            self.source_tree.delete(item)
        
        # 填充源树
        for source in sources:
            self.source_tree.insert("", tk.END, values=(source["name"], source["url"]))
        
        self.status_label.config(text="源列表已刷新")
    
    def switch_source(self):
        """切换到所选源"""
        # 获取所选Python版本
        version_str = self.source_version_combobox.get()
        if not version_str:
            messagebox.showwarning("未选择版本", "请先选择一个Python版本")
            return
        
        # 获取所选源
        selected_items = self.source_tree.selection()
        if not selected_items:
            messagebox.showwarning("未选择源", "请先选择一个要切换的源")
            return
        
        # 从下拉框的显示文本中提取路径
        python_path = version_str.split("(")[1].rstrip(")")
        
        # 获取所选源的URL
        item = selected_items[0]
        source_name, source_url = self.source_tree.item(item, "values")
        
        # 确认切换
        if not messagebox.askyesno("确认切换", f"确定要将 {python_path} 的pip源切换到 {source_name} ({source_url})？"):
            return
        
        self.status_label.config(text=f"正在切换源到 {source_name}...")
        self.root.update()
        
        # 创建线程切换源，避免UI卡顿
        threading.Thread(target=self._switch_source_thread, args=(python_path, source_url), daemon=True).start()
    
    def _switch_source_thread(self, python_path, source_url):
        """在后台线程中切换源"""
        # 切换源
        success, message = set_pip_index(python_path, source_url)
        
        # 更新UI（在主线程中）
        self.root.after(0, lambda: self._update_ui_after_source_switch(success, message))
    
    def _update_ui_after_source_switch(self, success, message):
        """在主线程中更新切换源后的UI"""
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)
        
        # 重新检查当前源
        self.check_current_source()
    
    def add_custom_source(self):
        """添加自定义源"""
        # 弹出对话框输入源名称和URL
        custom_source_window = tk.Toplevel(self.root)
        custom_source_window.title("添加自定义源")
        custom_source_window.geometry("400x150")
        custom_source_window.resizable(False, False)
        custom_source_window.transient(self.root)  # 设置为主窗口的临时窗口
        
        # 居中窗口
        custom_source_window.update_idletasks()
        width = custom_source_window.winfo_width()
        height = custom_source_window.winfo_height()
        x = (custom_source_window.winfo_screenwidth() // 2) - (width // 2)
        y = (custom_source_window.winfo_screenheight() // 2) - (height // 2)
        custom_source_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # 名称输入
        name_frame = ttk.Frame(custom_source_window, padding=5)
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        
        name_label = ttk.Label(name_frame, text="源名称:")
        name_label.pack(side=tk.LEFT, padx=5)
        
        name_entry = ttk.Entry(name_frame, width=30)
        name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # URL输入
        url_frame = ttk.Frame(custom_source_window, padding=5)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        url_label = ttk.Label(url_frame, text="源URL:")
        url_label.pack(side=tk.LEFT, padx=5)
        
        url_entry = ttk.Entry(url_frame, width=30)
        url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 按钮
        button_frame = ttk.Frame(custom_source_window, padding=5)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_cancel():
            custom_source_window.destroy()
        
        def on_ok():
            name = name_entry.get().strip()
            url = url_entry.get().strip()
            
            if not name or not url:
                messagebox.showwarning("输入错误", "源名称和URL不能为空", parent=custom_source_window)
                return
            
            success, message = add_custom_pip_index(name, url)
            
            if success:
                messagebox.showinfo("成功", message, parent=custom_source_window)
                custom_source_window.destroy()
                # 刷新源列表
                self.refresh_source_list()
            else:
                messagebox.showerror("错误", message, parent=custom_source_window)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        ok_button = ttk.Button(button_frame, text="确定", command=on_ok)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        # 设置焦点到名称输入框
        name_entry.focus_set() 