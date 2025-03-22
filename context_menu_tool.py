#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
右键菜单管理器启动文件
用于启动右键菜单管理界面
"""

import os
import sys
import tkinter as tk

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入右键菜单管理器
from context_menu_manager.main import ContextMenuApp

def main():
    """主函数"""
    root = tk.Tk()
    app = ContextMenuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 