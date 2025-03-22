@echo off
REM 作者：道相抖音@慈悲剪辑，技术问题点关注留言
echo 正在启动Python版本管理器...
cd /d %~dp0
call venv\Scripts\activate.bat
python python_version_manager\main.py
pause 