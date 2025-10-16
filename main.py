"""
次元姬小说助手主程序
使用MaaFramework + PySide6实现次元姬小说app签到及小说内容识别保存到本地
"""

import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_ui import main as ui_main


def main():
    """主程序入口"""
    # 启动UI
    ui_main()


if __name__ == "__main__":
    main()