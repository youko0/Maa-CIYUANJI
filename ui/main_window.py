#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口界面
包含设备管理、小说管理和代币管理的主界面
"""
from typing import Dict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QFormLayout, QTextEdit, QComboBox,
    QProgressBar, QGroupBox, QApplication
)
from PySide6.QtCore import Qt, QTimer, QRect, QStandardPaths
from PySide6.QtGui import QAction, QScreen
from maa.tasker import Tasker

from core.balance_manager import BalanceManager
from core.maa_manager import MaaFrameworkManager
from core.novel_manager import NovelManager
from ui.home_tab import HomeTab
from ui.novel_tab import NovelTab
from ui.balance_tab import BalanceTab
from utils.logger import get_logger


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager

        self.novel_manager = NovelManager(config_manager)
        self.balance_manager = BalanceManager(config_manager)
        # 初始化MaaFramework组件
        self.maa_manager = MaaFrameworkManager(config_manager=config_manager)
        self.logger = get_logger(__name__)

        # 定时器用于定期刷新界面
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_ui)
        self.refresh_timer.start(5000)  # 每5秒刷新一次

        self.home_tab = None
        self.novel_tab = None
        self.balance_tab = None

        self.init_ui()
        self.refresh_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("次元姬小说助手")

        # 设置窗口尺寸为更合适的大小（参考常见桌面应用尺寸）
        self.resize(800, 600)

        # 将窗口移动到屏幕中心
        self.center_window()

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # 创建各个标签页
        self.home_tab = HomeTab(self.maa_manager, self.config_manager)
        self.novel_tab = NovelTab(self.novel_manager, self.config_manager)
        self.balance_tab = BalanceTab(self.balance_manager, self.config_manager)

        tab_widget.addTab(self.home_tab, "主页")
        tab_widget.addTab(self.novel_tab, "小说")
        tab_widget.addTab(self.balance_tab, "余额")

        # 创建菜单栏
        self.create_menu_bar()

    def center_window(self):
        """将窗口居中显示在屏幕中央"""
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_center = screen_geometry.center()

        # 获取窗口尺寸
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)

        # 移动窗口到屏幕中心
        self.move(window_geometry.topLeft())

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件')

        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助')

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", "次元姬小说助手 v1.0.0\n基于MaaFramework + PySide6开发")

    def refresh_ui(self):
        """刷新整个UI"""
        self.home_tab.refresh_device_list()
        self.novel_tab.refresh_novel_list()
        self.balance_tab.refresh_balance_info()


class AddNovelDialog(QDialog):
    """添加小说对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加小说")
        self.setModal(True)
        self.resize(300, 200)

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.start_chapter_edit = QLineEdit("1")
        self.end_chapter_edit = QLineEdit("9999")

        layout.addRow("小说名称:", self.name_edit)
        layout.addRow("起始章节:", self.start_chapter_edit)
        layout.addRow("结束章节:", self.end_chapter_edit)

        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)
