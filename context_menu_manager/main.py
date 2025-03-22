#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
右键菜单管理器
用于查看、添加、修改和删除Windows右键菜单项
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import ctypes
import threading
import webbrowser
from typing import Dict, List, Any, Optional, Tuple, Union

# 导入工具类
from .utils import ContextMenuManager, is_admin, refresh_explorer

class ContextMenuApp:
    """右键菜单管理器应用类"""
    
    def __init__(self, root):
        """
        初始化应用
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("右键菜单管理器 by道相 抖音@慈悲剪辑")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # 尝试设置图标
        try:
            self.root.iconbitmap("context_menu.ico")
        except:
            pass  # 图标不存在则忽略
        
        # 右键菜单管理器实例
        self.menu_manager = ContextMenuManager()
        
        # 当前上下文
        self.current_context = tk.StringVar(value="文件")
        
        # 当前选中的菜单项
        self.selected_item = None
        
        # 创建UI
        self.create_menu_bar()
        self.create_main_frame()
        self.create_status_bar()
        
        # 检查管理员权限并显示警告
        self.check_admin_privileges()
        
        # 加载菜单项
        self.load_menu_items()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        self.menu_bar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="刷新", command=self.load_menu_items)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 操作菜单
        action_menu = tk.Menu(self.menu_bar, tearoff=0)
        action_menu.add_command(label="添加菜单项", command=self.add_menu_item)
        action_menu.add_command(label="修改菜单项", command=self.modify_menu_item)
        action_menu.add_command(label="删除菜单项", command=self.delete_menu_item)
        action_menu.add_separator()
        action_menu.add_command(label="刷新资源管理器", command=self.refresh_explorer)
        self.menu_bar.add_cascade(label="操作", menu=action_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="查看帮助", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        self.menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=self.menu_bar)
    
    def create_main_frame(self):
        """创建主框架"""
        # 主分割面板
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板
        self.left_frame = ttk.Frame(self.main_pane, width=250)
        self.main_pane.add(self.left_frame, weight=1)
        
        # 右侧面板
        self.right_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.right_frame, weight=2)
        
        # 设置左侧面板
        self.setup_left_panel()
        
        # 设置右侧面板
        self.setup_right_panel()
    
    def setup_left_panel(self):
        """设置左侧面板"""
        # 上下文选择框架
        context_frame = ttk.LabelFrame(self.left_frame, text="右键菜单上下文")
        context_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 上下文选择下拉框
        contexts = list(self.menu_manager.CONTEXTS.keys())
        context_combo = ttk.Combobox(context_frame, textvariable=self.current_context,
                                     values=contexts, state="readonly")
        context_combo.pack(fill=tk.X, padx=5, pady=5)
        context_combo.bind("<<ComboboxSelected>>", lambda e: self.load_menu_items())
        
        # 菜单项列表框架
        list_frame = ttk.LabelFrame(self.left_frame, text="菜单项列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建树形视图
        columns = ("display_name", "source")
        self.menu_tree = ttk.Treeview(list_frame, columns=columns, show="headings",
                                     yscrollcommand=scrollbar.set)
        
        # 设置列标题
        self.menu_tree.heading("display_name", text="菜单名称")
        self.menu_tree.heading("source", text="来源")
        
        # 设置列宽
        self.menu_tree.column("display_name", width=150)
        self.menu_tree.column("source", width=70)
        
        # 绑定选择事件
        self.menu_tree.bind("<<TreeviewSelect>>", self.on_item_selected)
        self.menu_tree.bind("<Double-1>", lambda e: self.modify_menu_item())
        
        self.menu_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.menu_tree.yview)
        
        # 按钮框架
        button_frame = ttk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加按钮
        add_button = ttk.Button(button_frame, text="添加", command=self.add_menu_item)
        add_button.pack(side=tk.LEFT, padx=2)
        
        # 修改按钮
        modify_button = ttk.Button(button_frame, text="修改", command=self.modify_menu_item)
        modify_button.pack(side=tk.LEFT, padx=2)
        
        # 删除按钮
        delete_button = ttk.Button(button_frame, text="删除", command=self.delete_menu_item)
        delete_button.pack(side=tk.LEFT, padx=2)
        
        # 刷新按钮
        refresh_button = ttk.Button(button_frame, text="刷新", command=self.load_menu_items)
        refresh_button.pack(side=tk.RIGHT, padx=2)
    
    def setup_right_panel(self):
        """设置右侧面板"""
        # 菜单项详情框架
        details_frame = ttk.LabelFrame(self.right_frame, text="菜单项详情")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建详情视图
        info_frame = ttk.Frame(details_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 放置详情字段
        fields = [
            ("名称", "name"),
            ("显示名称", "display_name"),
            ("来源", "source"),
            ("命令", "command"),
            ("图标", "icon"),
            ("位置", "position"),
            ("扩展菜单", "extended")
        ]
        
        self.detail_labels = {}
        
        for i, (label_text, field) in enumerate(fields):
            # 字段标签
            ttk.Label(info_frame, text=f"{label_text}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=3)
            
            # 字段值
            if field == "command":
                # 命令使用文本框显示
                frame = ttk.Frame(info_frame)
                frame.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=3)
                
                command_text = scrolledtext.ScrolledText(frame, height=4, wrap=tk.WORD)
                command_text.pack(fill=tk.BOTH, expand=True)
                self.detail_labels[field] = command_text
            else:
                # 其他字段使用标签显示
                var = tk.StringVar()
                ttk.Label(info_frame, textvariable=var).grid(row=i, column=1, sticky=tk.W, padx=5, pady=3)
                self.detail_labels[field] = var
        
        # 使列可扩展
        info_frame.columnconfigure(1, weight=1)
        
        # 预览框架
        preview_frame = ttk.LabelFrame(self.right_frame, text="右键菜单预览")
        preview_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 预览标签
        self.preview_label = ttk.Label(preview_frame, text="选择一个菜单项以查看预览")
        self.preview_label.pack(fill=tk.X, padx=5, pady=10)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 状态标签
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 管理员状态标签
        self.admin_label = ttk.Label(self.status_bar, text="")
        self.admin_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def check_admin_privileges(self):
        """检查管理员权限并更新状态"""
        if is_admin():
            self.admin_label.config(text="管理员模式", foreground="green")
        else:
            self.admin_label.config(text="普通用户模式", foreground="red")
            messagebox.showwarning("权限不足", 
                                  "当前以普通用户模式运行，将无法添加、修改或删除右键菜单项。\n"
                                  "请以管理员身份运行此应用以获得完整功能。")
    
    def load_menu_items(self):
        """加载当前上下文的菜单项"""
        # 清空现有项
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)
        
        # 清空详情视图
        self.clear_details()
        
        # 获取当前上下文
        context = self.current_context.get()
        if not context:
            return
        
        # 更新状态
        self.status_label.config(text=f"正在加载{context}的右键菜单项...")
        self.root.update_idletasks()
        
        try:
            # 获取菜单项
            items = self.menu_manager.get_context_menu_items(context)
            
            # 填充树形视图
            for item in items:
                self.menu_tree.insert("", tk.END, text=item["name"], 
                                     values=(item["display_name"], item["source"]),
                                     tags=(item["source"],))
                
            # 设置标签颜色
            self.menu_tree.tag_configure("HKCU", foreground="blue")
            self.menu_tree.tag_configure("HKCR", foreground="green")
            
            # 更新状态
            self.status_label.config(text=f"已加载 {len(items)} 个{context}的右键菜单项")
        except Exception as e:
            messagebox.showerror("加载失败", f"加载菜单项时出错：\n{str(e)}")
            self.status_label.config(text="加载菜单项失败")
    
    def on_item_selected(self, event):
        """当选择菜单项时触发"""
        selections = self.menu_tree.selection()
        if not selections:
            self.selected_item = None
            self.clear_details()
            return
        
        # 获取选中项
        item_id = selections[0]
        item_name = self.menu_tree.item(item_id, "text")
        item_values = self.menu_tree.item(item_id, "values")
        display_name = item_values[0]
        source = item_values[1]
        
        # 获取当前上下文
        context = self.current_context.get()
        
        # 获取菜单项详细信息
        items = self.menu_manager.get_context_menu_items(context)
        selected_item = next((item for item in items if item["name"] == item_name), None)
        
        if not selected_item:
            self.clear_details()
            return
        
        # 保存当前选中项
        self.selected_item = selected_item
        
        # 更新详情视图
        self.update_details(selected_item)
    
    def clear_details(self):
        """清空详情视图"""
        for field, widget in self.detail_labels.items():
            if field == "command":
                widget.delete(1.0, tk.END)
                widget.config(state=tk.DISABLED)
            else:
                widget.set("")
        
        self.preview_label.config(text="选择一个菜单项以查看预览")
    
    def update_details(self, item):
        """
        更新详情视图
        
        Args:
            item: 菜单项信息字典
        """
        # 更新字段
        for field, widget in self.detail_labels.items():
            if field == "command":
                widget.config(state=tk.NORMAL)
                widget.delete(1.0, tk.END)
                widget.insert(tk.END, item.get(field, ""))
                widget.config(state=tk.DISABLED)
            else:
                value = item.get(field, "")
                if field == "extended":
                    value = "是" if value else "否"
                widget.set(str(value))
        
        # 更新预览
        self.preview_label.config(text=f"右键菜单显示为：{item.get('display_name', '')}")
    
    def add_menu_item(self):
        """添加新的右键菜单项"""
        if not is_admin():
            messagebox.showwarning("权限不足", "添加菜单项需要管理员权限，请以管理员身份运行此应用。")
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加右键菜单项")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置对话框内容
        self.create_menu_item_form(dialog, is_add=True)
    
    def modify_menu_item(self):
        """修改选中的右键菜单项"""
        if not self.selected_item:
            messagebox.showinfo("提示", "请先选择一个要修改的菜单项")
            return
        
        if not is_admin():
            messagebox.showwarning("权限不足", "修改菜单项需要管理员权限，请以管理员身份运行此应用。")
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("修改右键菜单项")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置对话框内容
        self.create_menu_item_form(dialog, is_add=False)
    
    def create_menu_item_form(self, dialog, is_add=True):
        """
        创建菜单项表单
        
        Args:
            dialog: 对话框窗口
            is_add: 是否为添加操作
        """
        # 表单框架
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 获取当前上下文
        current_context = self.current_context.get()
        
        # 上下文选择
        ttk.Label(form_frame, text="上下文:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        context_var = tk.StringVar(value=current_context)
        context_combo = ttk.Combobox(form_frame, textvariable=context_var,
                                    values=list(self.menu_manager.CONTEXTS.keys()),
                                    state="readonly")
        context_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 名称
        ttk.Label(form_frame, text="名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var)
        name_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 显示名称
        ttk.Label(form_frame, text="显示名称:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        display_name_var = tk.StringVar()
        display_name_entry = ttk.Entry(form_frame, textvariable=display_name_var)
        display_name_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 命令
        ttk.Label(form_frame, text="命令:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        command_text = scrolledtext.ScrolledText(form_frame, height=5, wrap=tk.WORD)
        command_text.grid(row=3, column=1, sticky=tk.NSEW, padx=5, pady=5)
        
        # 图标
        ttk.Label(form_frame, text="图标:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        icon_frame = ttk.Frame(form_frame)
        icon_frame.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        icon_var = tk.StringVar()
        icon_entry = ttk.Entry(icon_frame, textvariable=icon_var)
        icon_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(icon_frame, text="浏览...", 
                  command=lambda: icon_var.set(filedialog.askopenfilename(
                      filetypes=[("图标文件", "*.ico;*.exe;*.dll"), ("所有文件", "*.*")]
                  ))).pack(side=tk.RIGHT)
        
        # 位置
        ttk.Label(form_frame, text="位置:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        position_var = tk.StringVar()
        position_combo = ttk.Combobox(form_frame, textvariable=position_var,
                                     values=["Top", "Bottom", ""])
        position_combo.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 扩展菜单
        extended_var = tk.BooleanVar(value=False)
        extended_check = ttk.Checkbutton(form_frame, text="扩展菜单 (需要按Shift键才显示)",
                                        variable=extended_var)
        extended_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # 来源
        if not is_add:
            ttk.Label(form_frame, text="来源:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
            source_var = tk.StringVar(value=self.selected_item.get("source", "HKCU"))
            source_label = ttk.Label(form_frame, textvariable=source_var)
            source_label.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 确定按钮
        if is_add:
            ttk.Button(button_frame, text="添加", 
                      command=lambda: self.do_add_menu_item(
                          dialog, context_var.get(), name_var.get(), 
                          command_text.get(1.0, tk.END).strip(),
                          display_name_var.get(), icon_var.get(),
                          position_var.get(), extended_var.get()
                      )).pack(side=tk.RIGHT, padx=5)
        else:
            ttk.Button(button_frame, text="修改", 
                      command=lambda: self.do_modify_menu_item(
                          dialog, context_var.get(), name_var.get(), 
                          source_var.get(), command_text.get(1.0, tk.END).strip(),
                          display_name_var.get(), icon_var.get(),
                          position_var.get(), extended_var.get()
                      )).pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        ttk.Button(button_frame, text="取消", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 如果是修改操作，填充现有数据
        if not is_add and self.selected_item:
            name_var.set(self.selected_item.get("name", ""))
            display_name_var.set(self.selected_item.get("display_name", ""))
            command_text.insert(tk.END, self.selected_item.get("command", ""))
            icon_var.set(self.selected_item.get("icon", ""))
            position_var.set(self.selected_item.get("position", ""))
            extended_var.set(self.selected_item.get("extended", False))
        
        # 使列可扩展
        form_frame.columnconfigure(1, weight=1)
        
        # 使命令行可扩展
        form_frame.rowconfigure(3, weight=1)
    
    def do_add_menu_item(self, dialog, context, name, command, 
                         display_name, icon, position, extended):
        """
        执行添加菜单项操作
        
        Args:
            dialog: 对话框窗口
            context: 上下文
            name: 菜单项名称
            command: 命令
            display_name: 显示名称
            icon: 图标路径
            position: 位置
            extended: 是否为扩展菜单
        """
        # 验证输入
        if not name:
            messagebox.showwarning("输入错误", "名称不能为空")
            return
        
        if not command:
            messagebox.showwarning("输入错误", "命令不能为空")
            return
        
        # 更新状态
        self.status_label.config(text="正在添加菜单项...")
        dialog.update_idletasks()
        
        try:
            # 执行添加
            success = self.menu_manager.add_menu_item(
                context, name, command, display_name, icon, position, extended
            )
            
            if success:
                messagebox.showinfo("添加成功", f"已成功添加右键菜单项：{name}")
                dialog.destroy()
                
                # 刷新列表
                self.load_menu_items()
            else:
                messagebox.showerror("添加失败", "无法添加右键菜单项，请检查您的输入和权限")
        except Exception as e:
            messagebox.showerror("添加失败", f"添加菜单项时出错：\n{str(e)}")
        finally:
            self.status_label.config(text="就绪")
    
    def do_modify_menu_item(self, dialog, context, name, source, command, 
                           display_name, icon, position, extended):
        """
        执行修改菜单项操作
        
        Args:
            dialog: 对话框窗口
            context: 上下文
            name: 菜单项名称
            source: 来源
            command: 命令
            display_name: 显示名称
            icon: 图标路径
            position: 位置
            extended: 是否为扩展菜单
        """
        # 验证输入
        if not name:
            messagebox.showwarning("输入错误", "名称不能为空")
            return
        
        if not command:
            messagebox.showwarning("输入错误", "命令不能为空")
            return
        
        # 更新状态
        self.status_label.config(text="正在修改菜单项...")
        dialog.update_idletasks()
        
        try:
            # 执行修改
            success = self.menu_manager.modify_menu_item(
                context, name, source, command, display_name, icon, position, extended
            )
            
            if success:
                messagebox.showinfo("修改成功", f"已成功修改右键菜单项：{name}")
                dialog.destroy()
                
                # 刷新列表
                self.load_menu_items()
            else:
                messagebox.showerror("修改失败", "无法修改右键菜单项，请检查您的输入和权限")
        except Exception as e:
            messagebox.showerror("修改失败", f"修改菜单项时出错：\n{str(e)}")
        finally:
            self.status_label.config(text="就绪")
    
    def delete_menu_item(self):
        """删除选中的右键菜单项"""
        if not self.selected_item:
            messagebox.showinfo("提示", "请先选择一个要删除的菜单项")
            return
        
        if not is_admin():
            messagebox.showwarning("权限不足", "删除菜单项需要管理员权限，请以管理员身份运行此应用。")
            return
        
        # 获取菜单项信息
        name = self.selected_item.get("name", "")
        display_name = self.selected_item.get("display_name", "")
        source = self.selected_item.get("source", "HKCU")
        context = self.current_context.get()
        
        # 确认删除
        if not messagebox.askyesno("确认删除", 
                                  f"确定要删除菜单项\"{display_name}\"吗？\n"
                                  f"此操作无法撤销。"):
            return
        
        # 更新状态
        self.status_label.config(text="正在删除菜单项...")
        self.root.update_idletasks()
        
        try:
            # 执行删除
            success = self.menu_manager.delete_menu_item(context, name, source)
            
            if success:
                messagebox.showinfo("删除成功", f"已成功删除右键菜单项：{display_name}")
                
                # 刷新列表
                self.load_menu_items()
            else:
                messagebox.showerror("删除失败", "无法删除右键菜单项，请检查您的权限")
        except Exception as e:
            messagebox.showerror("删除失败", f"删除菜单项时出错：\n{str(e)}")
        finally:
            self.status_label.config(text="就绪")
    
    def refresh_explorer(self):
        """刷新资源管理器"""
        self.status_label.config(text="正在刷新资源管理器...")
        self.root.update_idletasks()
        
        try:
            # 创建线程执行刷新操作
            threading.Thread(target=self._refresh_explorer_thread).start()
        except Exception as e:
            messagebox.showerror("刷新失败", f"刷新资源管理器时出错：\n{str(e)}")
            self.status_label.config(text="刷新资源管理器失败")
    
    def _refresh_explorer_thread(self):
        """在后台线程中刷新资源管理器"""
        try:
            refresh_explorer()
            self.root.after(0, lambda: self.status_label.config(text="资源管理器已刷新"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("刷新失败", f"刷新资源管理器时出错：\n{str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="刷新资源管理器失败"))
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """右键菜单管理器帮助

此工具用于管理Windows系统中的右键菜单项。

主要功能：
- 查看不同上下文（文件、文件夹、桌面背景等）的右键菜单项
- 添加新的右键菜单项
- 修改现有右键菜单项
- 删除不需要的右键菜单项

注意事项：
- 添加、修改和删除菜单项需要管理员权限
- 某些系统保护的菜单项可能无法修改或删除
- 修改注册表有风险，请谨慎操作
- 建议在修改前备份注册表

在"来源"列中：
- HKCU：表示菜单项存储在当前用户的注册表中
- HKCR：表示菜单项存储在系统的注册表中

如有任何问题，请联系软件开发者。
"""
        dialog = tk.Toplevel(self.root)
        dialog.title("帮助")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        
        text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """右键菜单管理器 v1.0

此工具是MyTools工具箱的一部分，用于管理Windows系统右键菜单。

功能：
- 查看、添加、修改和删除右键菜单项
- 支持不同上下文的右键菜单管理
- 提供直观的用户界面

© 2023 MyTools团队
"""
        messagebox.showinfo("关于", about_text)

def main():
    """主函数"""
    root = tk.Tk()
    app = ContextMenuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 