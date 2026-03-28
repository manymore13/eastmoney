@echo off
chcp 65001 >nul
echo 正在启动东方财富研报工具...
echo.

cd /d "%~dp0"

python gui\main.py

if errorlevel 1 (
    echo.
    echo 启动失败！请确保已安装依赖：
    echo   pip install -r requirements.txt
    echo.
    pause
)
