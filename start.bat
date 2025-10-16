@echo off
echo 正在启动次元姬小说助手...

REM 确保日志目录存在
if not exist "logs" mkdir logs

call conda activate Maa-WJDR
python main.py
pause