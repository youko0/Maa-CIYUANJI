@echo off
echo 正在启动次元姬小说助手...
echo.

REM 激活conda环境
call conda activate Maa-WJDR

REM 启动主程序
python main.py

echo.
echo 程序已退出。
pause