@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cls

:: ====================== 配置区（你只需要改这里） ======================
set "PROJECT_DIR=F:\Workspaces\JetBrains\PyCharm\python_uv_cloud_music"
set "SCRIPT_NAME=interactive_process.py"
set "OPEN_FOLDER=downloads"
:: =====================================================================

:: 日志输出函数
echo ==============================================
echo  启动脚本执行中... [%date% %time%]
echo ==============================================
echo.

:: 1. 切换到项目目录
echo [INFO] 切换到项目目录：%PROJECT_DIR%
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo [ERROR] 项目目录不存在！请检查路径配置
    pause
    exit /b 1
)

:: 2. 判断是否传入 --git 参数
if /i "%~1"=="--git" (
    echo.
    echo [INFO] 检测到 --git 参数，执行 git pull...
    git pull
    if errorlevel 1 (
        echo [WARN] git pull 执行失败，请手动检查仓库
    ) else (
        echo [SUCCESS] git pull 执行完成
    )
)

echo.
echo [INFO] 打开下载目录：%OPEN_FOLDER%
start explorer ".\%OPEN_FOLDER%"

echo.
echo [INFO] 启动 Python 脚本：%SCRIPT_NAME%
start uv run "%SCRIPT_NAME%"

echo.
echo ==============================================
echo  脚本执行完成！[%date% %time%]
echo ==============================================
echo.

endlocal