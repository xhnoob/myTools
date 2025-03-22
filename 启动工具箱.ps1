# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

# 设置控制台输出编码为GBK(936)
[Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding(936)
Write-Host "正在启动MyTools工具箱..." -ForegroundColor Green

# 获取脚本所在路径并设置工作目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $scriptPath

# 检查虚拟环境是否存在
if (-not (Test-Path -Path ".venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
if ($PSVersionTable.PSVersion.Major -ge 6) {
    # PowerShell Core
    & .\.venv\Scripts\Activate.ps1
} else {
    # Windows PowerShell
    & .\.venv\Scripts\Activate.ps1
}

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -q -r requirements.txt

# 启动工具箱
Write-Host "启动工具箱..." -ForegroundColor Green
python mytools.py

# 提示退出
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 