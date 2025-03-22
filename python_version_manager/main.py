#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
Python版本管理器
用于扫描、切换Python版本以及管理Python包
现已支持管理PyPI镜像源功能，提高包下载速度
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