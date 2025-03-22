# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

# 以管理员权限运行Python版本管理器
Write-Host "正在以管理员权限启动Python版本管理器..." -ForegroundColor Green

# 获取当前脚本的路径
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 激活虚拟环境并运行应用程序
Set-Location $scriptPath
& "$scriptPath\venv\Scripts\Activate.ps1"
python "$scriptPath\python_version_manager\main.py"

# 完成后暂停
Write-Host "按任意键退出..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 