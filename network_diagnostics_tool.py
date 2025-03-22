#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
网络诊断工具主入口
可以直接运行此脚本启动网络诊断工具
"""

import os
import sys
import tkinter as tk

# 确保可以导入network_diagnostics模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from network_diagnostics import NetworkDiagnostics

def main():
    """主函数"""
    # 创建根窗口
    root = tk.Tk()
    root.title("网络诊断工具 by道相 抖音@慈悲剪辑")
    root.geometry("900x600")
    root.minsize(900, 600)
    
    # 创建网络诊断工具实例
    app = NetworkDiagnostics(root)
    
    # 进入主循环
    root.mainloop()

if __name__ == "__main__":
    main() 