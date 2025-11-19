#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
次元姬小说助手主程序入口
基于MaaFramework + PySide6实现次元姬小说app签到及小说内容识别保存到本地
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.balance_manager import get_balance_manager
from core.maa_manager import get_maa_manager
from core.novel_manager import get_novel_manager
from ui.main_window import MainWindow
from utils.logger import get_logger
from core.config_manager import get_config_manager


def init_directories():
    """初始化项目目录结构"""
    # 创建必要的目录
    dirs = ['logs', 'configs', 'data', 'novels']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)


def load_managers():
    """加载manager"""
    get_config_manager()
    get_maa_manager()
    get_novel_manager()
    get_balance_manager()

def main():
    # 初始化目录
    init_directories()

    # 初始化日志记录器
    get_logger()

    # 加载manager
    load_managers()

    # 创建Qt应用
    app = QApplication(sys.argv)
    app.setApplicationName("次元姬小说助手")
    app.setApplicationVersion("1.0.0")

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
