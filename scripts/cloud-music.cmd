@echo off

:: ====================== Configuration ======================
set "PROJECT_DIR=F:\Workspaces\JetBrains\PyCharm\python_uv_cloud_music"
set "SCRIPT_NAME=interactive_process.py"
set "OPEN_FOLDER=downloads"
:: ===========================================================

:: Check parameters FIRST, before changing directory
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="--folder-only" goto :folder_only
if /i "%~1"=="--git-pull" goto :git_pull

echo ==============================================
echo  Starting Script...
echo ==============================================
echo.

:: Step 1: Change to project directory
cd /d "%PROJECT_DIR%" 2>nul
if errorlevel 1 (
    echo [ERROR] Project directory does not exist!
    pause
    exit /b 1
)

goto :normal_mode

:show_help
echo.
echo ==============================================
echo  Help Information
echo ==============================================
echo.
echo Usage: cloud-music.cmd [options]
echo.
echo Options:
echo   --folder-only    Switch to project directory only
echo   --git-pull       Pull from remote repository (default: origin)
echo   --git-pull REMOTE Pull from specified remote
echo   --help           Show this help message
echo   No options       Normal mode: open downloads and start script
echo.
echo Examples:
echo   cloud-music.cmd                  :: Normal mode
echo   cloud-music.cmd --folder-only    :: Directory only
echo   cloud-music.cmd --git-pull       :: Pull from origin
echo   cloud-music.cmd --git-pull upstream :: Pull from upstream
echo.
echo ==============================================
exit /b 0

:folder_only
cd /d "%PROJECT_DIR%" 2>nul
if errorlevel 1 (
    echo [ERROR] Project directory does not exist!
    pause
    exit /b 1
)
echo.
echo [INFO] --folder-only detected, switching to project directory only
echo [SUCCESS] Current directory: %CD%
exit /b 0

:git_pull
set "GIT_REMOTE=origin"
if not "%~2"=="" set "GIT_REMOTE=%~2"
cd /d "%PROJECT_DIR%" 2>nul
if errorlevel 1 (
    echo [ERROR] Project directory does not exist!
    pause
    exit /b 1
)
echo.
echo [INFO] Pulling from %GIT_REMOTE%...
git pull %GIT_REMOTE%
if errorlevel 1 (
    echo [WARN] Git pull failed
) else (
    echo [SUCCESS] Git pull completed
)
exit /b 0

:normal_mode
echo.
echo [INFO] Opening download directory: %OPEN_FOLDER%
start explorer ".\%OPEN_FOLDER%"

echo.
echo [INFO] Starting Python script: %SCRIPT_NAME%
start uv run "%SCRIPT_NAME%"

echo.
echo ==============================================
echo  Script Completed!
echo ==============================================
echo.
