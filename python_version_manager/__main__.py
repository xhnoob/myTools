#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
Python版本管理器入口模块
当直接运行整个目录时，Python会查找并执行此文件
"""

import sys
import tkinter as tk
from ui import PyVersionManagerApp

def main():
    """程序主入口"""
    root = tk.Tk()
    app = PyVersionManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 