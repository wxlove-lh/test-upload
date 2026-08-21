@echo off
chcp 65001 >nul
title AI虚拟文员 - 演示服务器
echo ============================================
echo   AI虚拟文员 演示服务器
echo   正在启动，请稍候...
echo   启动后浏览器会自动打开 http://localhost:5000
echo   演示账号: 13812345678 / 123456
echo   关闭本窗口即停止服务
echo ============================================
echo.

cd /d "%~dp0"

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查后端依赖（第一次运行会自动安装）
python -c "import flask, flask_jwt_extended, flask_sqlalchemy, flask_migrate, openpyxl, openai, PIL" >nul 2>nul
if %errorlevel% neq 0 (
    echo [首次运行] 正在安装后端依赖...
    pip install -r backend\requirements.txt
)

REM 检查 Node/npm
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

REM 每次启动都重新构建前端，确保是最新界面
echo.
echo [正在构建前端] 每次启动都会自动构建最新界面...
cd frontend
if not exist "node_modules" (
    echo [首次运行] 正在安装前端依赖，可能需要几分钟...
    call npm install
)
call npm run build
cd ..

echo.
echo 启动成功！浏览器打开 http://localhost:5000
echo 登录账号: 13812345678 / 123456
echo.
start http://localhost:5000
python demo_server.py

pause
