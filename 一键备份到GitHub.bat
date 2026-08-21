@echo off
chcp 65001 >nul
title AI虚拟文员 - 一键备份到 GitHub
cd /d "%~dp0"

echo ============================================
echo   AI虚拟文员 - 一键备份到 GitHub
echo   备份文件夹：%~dp0
echo ============================================
echo.

REM 检查 Git 是否安装
where git >nul 2>nul
if errorlevel 1 (
    echo [错误] 电脑里没找到 Git。
    echo 请先到 https://git-scm.com/ 下载安装，一路点"下一步"即可。
    pause
    exit /b 1
)

REM 保证提交时有作者信息（GitHub 账号登录时也会提示）
git config user.name >nul 2>nul
if errorlevel 1 git config user.name "ai-clerk"
git config user.email >nul 2>nul
if errorlevel 1 git config user.email "ai-clerk@local"

REM 第一次使用：设置 GitHub 仓库地址（之后会记住，不再问）
git remote get-url origin >nul 2>nul
if errorlevel 1 (
    echo [第一次使用] 还没设置 GitHub 仓库地址。
    echo.
    echo 步骤：先去 GitHub 网站注册账号，点 New repository 建一个"空仓库"
    echo （名字随意，不要勾选添加 README），然后把仓库地址粘贴到下面。
    echo 地址长这样：https://github.com/你的用户名/仓库名.git
    echo.
    set /p GITHUB_URL=请粘贴仓库地址: 
    if "%GITHUB_URL%"=="" (
        echo.
        echo 没填地址，本次取消。下次再运行本脚本设置即可。
        pause
        exit /b 1
    )
    git remote add origin %GITHUB_URL%
    if errorlevel 1 (
        echo.
        echo [错误] 设置仓库地址失败，请把上方英文提示截图发我。
        pause
        exit /b 1
    )
    echo %GITHUB_URL%> "github地址.txt"
    git branch -M main
    echo.
    echo 仓库地址已记住，以后备份不用再填。
    echo.
)

echo [1/3] 收集改动...
git add .
if errorlevel 1 goto error

echo [2/3] 生成备份记录...
git commit -m "自动备份 %date% %time%"
if errorlevel 1 (
    echo.
    echo 没有新改动，无需备份。
    goto done
)

echo [3/3] 上传中（第一次会弹出 GitHub 登录框）...
git push -u origin main
if errorlevel 1 goto error

echo.
echo 备份成功！代码已上传到 GitHub。
goto done

:error
echo.
echo 出错了！请把窗口里的英文提示截图发我。
:done
echo.
pause
