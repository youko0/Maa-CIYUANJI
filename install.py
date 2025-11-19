#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目安装脚本
自动安装项目所需的依赖
"""

import subprocess
import sys
import os


def install_dependencies():
    """安装项目依赖"""
    print("开始安装项目依赖...")
    
    try:
        # 检查是否在conda环境中
        if 'CONDA_DEFAULT_ENV' not in os.environ:
            print("警告: 未检测到conda环境，请确保已在Maa-WJDR环境中!")
        
        # 安装requirements.txt中的依赖
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成!")
        
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False
    except Exception as e:
        print(f"安装过程中发生错误: {e}")
        return False
    
    return True


def main():
    print("次元姬小说助手 - 依赖安装程序")
    print("=" * 40)
    
    if install_dependencies():
        print("\n安装成功! 您现在可以运行项目了。")
        print("运行方式:")
        print("  Windows: 双击 start.bat 或运行 python main.py")
        print("  其他系统: python main.py")
    else:
        print("\n安装失败，请检查错误信息。")
        sys.exit(1)


if __name__ == "__main__":
    main()