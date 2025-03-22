@echo off
REM 作者：道相抖音@慈悲剪辑，技术问题点关注留言

REM 设置中文编码
chcp 936 >nul
echo 正在启动MyTools工具箱...

:: 设置工作目录为脚本所在目录
cd /d "%~dp0"

:: 检查虚拟环境是否存在
if not exist .venv (
    echo 创建虚拟环境...
    python -m venv .venv
)

:: 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate.bat

:: 安装依赖
echo 安装依赖...
pip install -q -r requirements.txt

:: 启动工具箱
echo 启动工具箱...
python mytools.py

:: 暂停
pause 