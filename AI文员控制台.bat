@echo off
chcp 65001 >nul
title AI虚拟文员 - 总控制台
cd /d "%~dp0"

:menu
cls
echo ================================================
echo      AI虚拟文员 · 总控制台
echo ================================================
echo.
echo    1. 启动演示系统（记账 + 报税工具）
echo    2. 备份代码到 GitHub
echo    3. 打开项目文件夹
echo    4. 打开AI密钥配置（填了图片识别和AI聊天才能用）
echo    5. 退出
echo.
echo ================================================
echo.
choice /c 12345 /n /m "   请按数字键选择: "
if errorlevel 5 goto end
if errorlevel 4 (
    if not exist "backend\.env" (
        copy "backend\.env.example" "backend\.env" >nul
    )
    start notepad "backend\.env"
    goto menu
)
if errorlevel 3 (
    start explorer "%~dp0"
    goto menu
)
if errorlevel 2 (
    call "一键备份到GitHub.bat"
    goto menu
)
if errorlevel 1 (
    call "启动演示.bat"
    goto menu
)
goto menu

:end
exit /b
