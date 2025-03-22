#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
MyTools 工具箱
一个集成了多种实用工具的GUI应用程序
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

class ToolsApp:
    """工具箱主应用类"""
    
    def __init__(self, root):
        """初始化应用"""
        self.root = root
        self.root.title("MyTools 工具箱 by道相 抖音@慈悲剪辑")
        self.root.geometry("800x500")
        self.root.minsize(800, 500)
        
        # 设置应用图标
        try:
            self.root.iconbitmap("toolbox.ico")
        except:
            pass  # 如果图标文件不存在，则忽略
        
        # 设置样式
        self.style = ttk.Style()
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")  # 使用clam主题
        
        # 创建框架
        self.setup_frames()
        
        # 创建控件
        self.setup_widgets()
        
        # 显示欢迎信息
        self.show_welcome()
    
    def setup_frames(self):
        """设置应用的框架"""
        # 主分割框架 - 左侧为工具列表，右侧为内容
        self.main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧工具列表框架
        self.tools_frame = ttk.Frame(self.main_frame, width=200)
        self.main_frame.add(self.tools_frame, weight=1)
        
        # 右侧内容框架
        self.content_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(self.content_frame, weight=3)
        
        # 状态栏框架
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
    
    def setup_widgets(self):
        """设置应用的控件"""
        # 右侧欢迎标签 - 放在最前面确保早点创建
        self.content_label = ttk.Label(self.content_frame, text="欢迎使用工具箱", font=("Arial", 14))
        self.content_label.pack(padx=20, pady=20)
        
        # 工具描述文本框
        self.description_frame = ttk.LabelFrame(self.content_frame, text="工具描述")
        self.description_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.description_text = tk.Text(self.description_frame, wrap=tk.WORD, width=50, height=10)
        self.description_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.description_text.config(state=tk.DISABLED)
        
        # 启动按钮
        self.launch_button = ttk.Button(self.content_frame, text="启动所选工具", command=self.launch_selected_tool)
        self.launch_button.pack(padx=20, pady=20)
        
        # 左侧工具列表标题
        tools_title = ttk.Label(self.tools_frame, text="可用工具", font=("Arial", 12, "bold"))
        tools_title.pack(anchor=tk.W, padx=10, pady=10)
        
        # 工具列表
        self.tools_list = ttk.Treeview(self.tools_frame, columns=("name",), show="tree", height=15)
        self.tools_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 状态栏
        self.status_label = ttk.Label(self.status_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)
        
        # 版本信息
        version_label = ttk.Label(self.status_frame, text="版本 1.0")
        version_label.pack(side=tk.RIGHT)
        
        # 添加工具到列表
        self.add_tools_to_list()
        
        # 绑定双击事件
        self.tools_list.bind("<Double-1>", self.on_tool_selected)
        self.tools_list.bind("<<TreeviewSelect>>", self.on_tool_selected)
    
    def add_tools_to_list(self):
        """添加工具到列表中"""
        # 开发工具
        dev_tools = self.tools_list.insert("", tk.END, text="开发工具", open=True)
        python_vm = self.tools_list.insert(dev_tools, tk.END, text="Python版本管理器", values=("python_version_manager",))
        
        # 系统工具
        system_tools = self.tools_list.insert("", tk.END, text="系统工具", open=True)
        env_var_mgr = self.tools_list.insert(system_tools, tk.END, text="环境变量管理器", values=("env_var_manager",))
        context_menu_mgr = self.tools_list.insert(system_tools, tk.END, text="右键菜单管理器", values=("context_menu_manager",))
        # 这里可以添加更多工具...
        
        # 网络工具
        network_tools = self.tools_list.insert("", tk.END, text="网络工具", open=True)
        network_diag = self.tools_list.insert(network_tools, tk.END, text="网络诊断工具", values=("network_diagnostics",))
        # 这里可以添加更多工具...
        
        # 实用工具
        utility_tools = self.tools_list.insert("", tk.END, text="实用工具", open=True)
        # 这里可以添加更多工具...
        format_converter = self.tools_list.insert(utility_tools, tk.END, text="格式转换工具", values=("format_converter",))
        
        # 选中第一个工具
        self.tools_list.selection_set(python_vm)
        self.update_tool_info(python_vm)
    
    def on_tool_selected(self, event):
        """当选择一个工具时触发"""
        selections = self.tools_list.selection()
        if selections:
            self.update_tool_info(selections[0])
    
    def update_tool_info(self, item_id):
        """更新工具信息显示"""
        item = self.tools_list.item(item_id)
        tool_name = item["text"]
        
        # 添加安全检查，确保content_label已被创建
        if not hasattr(self, 'content_label'):
            self.content_label = ttk.Label(self.content_frame, text="", font=("Arial", 14))
            self.content_label.pack(padx=20, pady=20)
            
        # 如果是分类标题，则不显示启动按钮
        if not item["values"]:
            self.content_label.config(text=tool_name)
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(tk.END, "请选择一个具体的工具来查看详细信息。")
            self.description_text.config(state=tk.DISABLED)
            self.launch_button.config(state=tk.DISABLED)
            return
        
        # 获取工具标识符
        tool_id = item["values"][0]
        
        # 根据工具ID设置相应的描述
        descriptions = {
            "python_version_manager": """Python版本管理器

用于管理Windows系统中的Python版本和包的图形界面工具。

功能：
- 扫描并列出系统中所有安装的Python版本
- 切换系统当前使用的Python版本
- 管理Python包：查看、安装、卸载和更新
- 管理PyPI镜像源：切换和自定义Python包的安装源

适用于需要处理多个Python版本的开发者和用户。
""",
            "env_var_manager": """环境变量管理器

用于查看和管理Windows系统中的环境变量的图形界面工具。

功能：
- 查看和编辑用户环境变量
- 查看和编辑系统环境变量
- 管理PATH环境变量：添加、编辑、删除和排序路径
- 实时应用环境变量更改

适用于开发者和系统管理员，是配置开发环境的必备工具。
""",
            "network_diagnostics": """网络诊断工具

用于网络测试、IP查询、端口扫描和网络状态分析的图形界面工具。

功能：
- 查看系统网络配置和连接状态
- 执行网络测试：Ping、路由跟踪、DNS查询和HTTP测试
- IP地址查询：地理位置和运营商信息
- 端口扫描：检测目标主机开放的网络端口

适用于网络故障排查、安全检测和网络配置分析。
""",
            "context_menu_manager": """右键菜单管理器

用于查看、添加、修改和删除Windows系统右键菜单的图形界面工具。

功能：
- 查看不同上下文（文件、文件夹、桌面背景等）的右键菜单项
- 添加新的右键菜单项
- 修改现有右键菜单项的命令和属性
- 删除不需要的右键菜单项
- 支持扩展菜单（按Shift键显示）管理

适用于系统管理员和高级用户，让Windows使用更加高效便捷。
""",
            "format_converter": """格式转换工具

用于将文件从一种格式转换为另一种格式的图形界面工具。

功能：
- 支持多种文件格式之间的转换
- 提供简单的操作界面
- 快速完成文件格式转换任务

适用于需要频繁进行文件格式转换的用户。
"""
        }
        
        # 更新界面显示
        self.content_label.config(text=tool_name)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete(1.0, tk.END)
        
        if tool_id in descriptions:
            self.description_text.insert(tk.END, descriptions[tool_id])
            self.launch_button.config(state=tk.NORMAL)
        else:
            self.description_text.insert(tk.END, "该工具尚未实现或没有描述信息。")
            self.launch_button.config(state=tk.DISABLED)
        
        self.description_text.config(state=tk.DISABLED)
    
    def launch_selected_tool(self):
        """启动选中的工具"""
        selections = self.tools_list.selection()
        if not selections:
            return
        
        item = self.tools_list.item(selections[0])
        if not item["values"]:
            return
        
        tool_id = item["values"][0]
        
        # 根据工具ID启动相应的工具
        if tool_id == "python_version_manager":
            self.launch_python_version_manager()
        elif tool_id == "env_var_manager":
            self.launch_env_var_manager()
        elif tool_id == "network_diagnostics":
            self.launch_network_diagnostics()
        elif tool_id == "context_menu_manager":
            self.launch_context_menu_manager()
        elif tool_id == "format_converter":
            self.launch_format_converter()
        else:
            messagebox.showinfo("暂未实现", f"工具 '{item['text']}' 暂未实现，敬请期待。")
    
    def launch_python_version_manager(self):
        """启动Python版本管理器"""
        self.status_label.config(text="正在启动 Python版本管理器...")
        
        # 创建线程启动工具，避免UI卡顿
        threading.Thread(target=self._launch_python_version_manager_thread, daemon=True).start()
    
    def _launch_python_version_manager_thread(self):
        """在后台线程中启动Python版本管理器"""
        try:
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 构建Python版本管理器路径
            pvm_dir = os.path.join(current_dir, "python_version_manager")
            main_script = os.path.join(pvm_dir, "main.py")
            
            # 检查虚拟环境
            venv_dir = None
            if os.path.exists(os.path.join(current_dir, ".venv")):
                venv_dir = os.path.join(current_dir, ".venv")
            elif os.path.exists(os.path.join(current_dir, "venv")):
                venv_dir = os.path.join(current_dir, "venv")
            
            # 启动命令
            if os.name == 'nt':  # Windows
                if venv_dir:
                    # 使用批处理文件启动
                    bat_content = f"""@echo off
cd /d {current_dir}
call {os.path.join(venv_dir, 'Scripts', 'activate.bat')}
python "{main_script}"
"""
                    # 创建临时批处理文件
                    temp_bat = os.path.join(current_dir, "temp_pvm.bat")
                    with open(temp_bat, 'w', encoding='utf-8') as f:
                        f.write(bat_content)
                    
                    # 启动批处理文件
                    subprocess.Popen([temp_bat], shell=True)
                    
                    # 2秒后删除临时文件
                    def remove_temp():
                        import time
                        time.sleep(2)
                        try:
                            os.remove(temp_bat)
                        except:
                            pass
                    threading.Thread(target=remove_temp, daemon=True).start()
                else:
                    # 直接使用系统Python
                    subprocess.Popen(["python", main_script], shell=True)
            else:  # Linux/Mac
                if venv_dir:
                    activate_path = os.path.join(venv_dir, "bin", "activate")
                    cmd = f"source {activate_path} && python {main_script}"
                    subprocess.Popen(["bash", "-c", cmd])
                else:
                    subprocess.Popen(["python", main_script])
            
            # 更新UI（在主线程中）
            self.root.after(0, lambda: self.status_label.config(text="已启动 Python版本管理器"))
        except Exception as e:
            # 更新UI（在主线程中）
            self.root.after(0, lambda: self.status_label.config(text=f"启动失败: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("启动错误", f"启动Python版本管理器时出错:\n{str(e)}"))
    
    def launch_env_var_manager(self):
        """启动环境变量管理器"""
        self.status_label.config(text="正在启动 环境变量管理器...")
        
        # 创建线程启动工具，避免UI卡顿
        threading.Thread(target=self._launch_env_var_manager_thread, daemon=True).start()
    
    def _launch_env_var_manager_thread(self):
        """在后台线程中启动环境变量管理器"""
        try:
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 构建环境变量管理器路径
            evm_dir = os.path.join(current_dir, "env_var_manager")
            main_script = os.path.join(evm_dir, "main.py")
            
            # 检查虚拟环境
            venv_dir = None
            if os.path.exists(os.path.join(current_dir, ".venv")):
                venv_dir = os.path.join(current_dir, ".venv")
            elif os.path.exists(os.path.join(current_dir, "venv")):
                venv_dir = os.path.join(current_dir, "venv")
            
            # 启动命令
            if os.name == 'nt':  # Windows
                if venv_dir:
                    # 使用批处理文件启动
                    bat_content = f"""@echo off
cd /d {current_dir}
call {os.path.join(venv_dir, 'Scripts', 'activate.bat')}
python "{main_script}"
"""
                    # 创建临时批处理文件
                    temp_bat = os.path.join(current_dir, "temp_evm.bat")
                    with open(temp_bat, 'w', encoding='utf-8') as f:
                        f.write(bat_content)
                    
                    # 启动批处理文件
                    subprocess.Popen([temp_bat], shell=True)
                    
                    # 2秒后删除临时文件
                    def remove_temp():
                        import time
                        time.sleep(2)
                        try:
                            os.remove(temp_bat)
                        except:
                            pass
                    threading.Thread(target=remove_temp, daemon=True).start()
                else:
                    # 直接使用系统Python
                    subprocess.Popen(["python", main_script], shell=True)
            else:  # Linux/Mac
                if venv_dir:
                    activate_path = os.path.join(venv_dir, "bin", "activate")
                    cmd = f"source {activate_path} && python {main_script}"
                    subprocess.Popen(["bash", "-c", cmd])
                else:
                    subprocess.Popen(["python", main_script])
            
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="就绪"))
            
        except Exception as e:
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="启动环境变量管理器失败"))
            # 显示错误信息
            self.root.after(0, lambda: messagebox.showerror("启动失败", f"启动环境变量管理器失败:\n{str(e)}"))
    
    def launch_network_diagnostics(self):
        """启动网络诊断工具"""
        self.status_label.config(text="正在启动 网络诊断工具...")
        
        # 创建线程启动工具，避免UI卡顿
        threading.Thread(target=self._launch_network_diagnostics_thread, daemon=True).start()
    
    def _launch_network_diagnostics_thread(self):
        """在后台线程中启动网络诊断工具"""
        try:
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 构建网络诊断工具路径
            nd_script = os.path.join(current_dir, "network_diagnostics_tool.py")
            
            # 检查虚拟环境
            venv_dir = None
            if os.path.exists(os.path.join(current_dir, ".venv")):
                venv_dir = os.path.join(current_dir, ".venv")
            elif os.path.exists(os.path.join(current_dir, "venv")):
                venv_dir = os.path.join(current_dir, "venv")
            
            # 启动命令
            if os.name == 'nt':  # Windows
                if venv_dir:
                    # 使用批处理文件启动
                    bat_content = f"""@echo off
cd /d {current_dir}
call {os.path.join(venv_dir, 'Scripts', 'activate.bat')}
python "{nd_script}"
"""
                    # 创建临时批处理文件
                    temp_bat = os.path.join(current_dir, "temp_nd.bat")
                    with open(temp_bat, 'w', encoding='utf-8') as f:
                        f.write(bat_content)
                    
                    # 启动批处理文件
                    subprocess.Popen([temp_bat], shell=True)
                    
                    # 2秒后删除临时文件
                    def remove_temp():
                        import time
                        time.sleep(2)
                        try:
                            os.remove(temp_bat)
                        except:
                            pass
                    threading.Thread(target=remove_temp, daemon=True).start()
                else:
                    # 直接使用系统Python
                    subprocess.Popen(["python", nd_script], shell=True)
            else:  # Linux/Mac
                if venv_dir:
                    activate_path = os.path.join(venv_dir, "bin", "activate")
                    cmd = f"source {activate_path} && python {nd_script}"
                    subprocess.Popen(["bash", "-c", cmd])
                else:
                    subprocess.Popen(["python", nd_script])
            
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="就绪"))
            
        except Exception as e:
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="启动网络诊断工具失败"))
            # 显示错误信息
            self.root.after(0, lambda: messagebox.showerror("启动失败", f"启动网络诊断工具失败:\n{str(e)}"))
    
    def launch_context_menu_manager(self):
        """启动右键菜单管理器"""
        self.status_label.config(text="正在启动 右键菜单管理器...")
        
        # 创建线程启动工具，避免UI卡顿
        threading.Thread(target=self._launch_context_menu_manager_thread, daemon=True).start()
    
    def _launch_context_menu_manager_thread(self):
        """在后台线程中启动右键菜单管理器"""
        try:
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 构建右键菜单管理器路径
            cmm_dir = os.path.join(current_dir, "context_menu_manager")
            main_script = os.path.join(cmm_dir, "main.py")
            
            # 检查虚拟环境
            venv_dir = None
            if os.path.exists(os.path.join(current_dir, ".venv")):
                venv_dir = os.path.join(current_dir, ".venv")
            elif os.path.exists(os.path.join(current_dir, "venv")):
                venv_dir = os.path.join(current_dir, "venv")
            
            # 启动命令
            if os.name == 'nt':  # Windows
                if venv_dir:
                    # 使用批处理文件启动
                    bat_content = f"""@echo off
cd /d {current_dir}
call {os.path.join(venv_dir, 'Scripts', 'activate.bat')}
python "{main_script}"
"""
                    # 创建临时批处理文件
                    temp_bat = os.path.join(current_dir, "temp_cmm.bat")
                    with open(temp_bat, 'w', encoding='utf-8') as f:
                        f.write(bat_content)
                    
                    # 启动批处理文件
                    subprocess.Popen([temp_bat], shell=True)
                    
                    # 2秒后删除临时文件
                    def remove_temp():
                        import time
                        time.sleep(2)
                        try:
                            os.remove(temp_bat)
                        except:
                            pass
                    threading.Thread(target=remove_temp, daemon=True).start()
                else:
                    # 直接使用系统Python
                    subprocess.Popen(["python", main_script], shell=True)
            else:  # Linux/Mac
                if venv_dir:
                    activate_path = os.path.join(venv_dir, "bin", "activate")
                    cmd = f"source {activate_path} && python {main_script}"
                    subprocess.Popen(["bash", "-c", cmd])
                else:
                    subprocess.Popen(["python", main_script])
            
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="就绪"))
            
        except Exception as e:
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="启动右键菜单管理器失败"))
            # 显示错误信息
            self.root.after(0, lambda: messagebox.showerror("启动失败", f"启动右键菜单管理器失败:\n{str(e)}"))
    
    def launch_format_converter(self):
        """启动格式转换工具"""
        self.status_label.config(text="正在启动 格式转换工具...")
        
        # 创建线程启动工具，避免UI卡顿
        threading.Thread(target=self._launch_format_converter_thread, daemon=True).start()
    
    def _launch_format_converter_thread(self):
        """在后台线程中启动格式转换工具"""
        try:
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 构建格式转换工具路径
            fc_dir = os.path.join(current_dir, "format_converter")
            main_script = os.path.join(fc_dir, "main.py")
            
            # 检查虚拟环境
            venv_dir = None
            if os.path.exists(os.path.join(current_dir, ".venv")):
                venv_dir = os.path.join(current_dir, ".venv")
            elif os.path.exists(os.path.join(current_dir, "venv")):
                venv_dir = os.path.join(current_dir, "venv")
            
            # 启动命令
            if os.name == 'nt':  # Windows
                if venv_dir:
                    # 使用批处理文件启动
                    bat_content = f"""@echo off
cd /d {current_dir}
call {os.path.join(venv_dir, 'Scripts', 'activate.bat')}
python "{main_script}"
"""
                    # 创建临时批处理文件
                    temp_bat = os.path.join(current_dir, "temp_fc.bat")
                    with open(temp_bat, 'w', encoding='utf-8') as f:
                        f.write(bat_content)
                    
                    # 启动批处理文件
                    subprocess.Popen([temp_bat], shell=True)
                    
                    # 2秒后删除临时文件
                    def remove_temp():
                        import time
                        time.sleep(2)
                        try:
                            os.remove(temp_bat)
                        except:
                            pass
                    threading.Thread(target=remove_temp, daemon=True).start()
                else:
                    # 直接使用系统Python
                    subprocess.Popen(["python", main_script], shell=True)
            else:  # Linux/Mac
                if venv_dir:
                    activate_path = os.path.join(venv_dir, "bin", "activate")
                    cmd = f"source {activate_path} && python {main_script}"
                    subprocess.Popen(["bash", "-c", cmd])
                else:
                    subprocess.Popen(["python", main_script])
            
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="就绪"))
            
        except Exception as e:
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="启动格式转换工具失败"))
            # 显示错误信息
            self.root.after(0, lambda: messagebox.showerror("启动失败", f"启动格式转换工具失败:\n{str(e)}"))
    
    def show_welcome(self):
        """显示欢迎信息"""
        welcome_text = """欢迎使用 MyTools 工具箱!
        
这个工具箱集成了多种实用工具，帮助您提高工作效率。
请从左侧列表中选择一个工具开始使用。

当前版本包含的工具:
- Python版本管理器
- 环境变量管理器
- 网络诊断工具
- 右键菜单管理器
- 格式转换工具
- 更多工具即将添加...

感谢您的使用！我是作者道相，欢迎关注我的抖音@慈悲剪辑
"""
        messagebox.showinfo("欢迎", welcome_text)

def main():
    """程序入口函数"""
    root = tk.Tk()
    app = ToolsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 