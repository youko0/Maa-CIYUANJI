#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主页标签页模块
包含设备管理和日志显示功能
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QTextEdit, QPushButton, QHeaderView
)
from PySide6.QtCore import Qt

from ui.device_dialog import DeviceConnectionDialog
from core.maa_manager import MaaFrameworkManager
from utils.logger import get_logger


class HomeTab(QWidget):
    """主页标签页"""

    def __init__(self, maa_manager, config_manager):
        super().__init__()
        self.maa_manager = maa_manager
        self.config_manager = config_manager
        self.logger = get_logger(__name__)

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 设备列表区域
        device_group = QGroupBox("设备列表")
        device_layout = QVBoxLayout(device_group)

        # 设备操作按钮
        device_btn_layout = QHBoxLayout()
        self.connect_device_btn = QPushButton("连接设备")
        self.connect_device_btn.clicked.connect(self._show_connect_device_dialog)
        device_btn_layout.addWidget(self.connect_device_btn)
        self.one_click_check_in_btn = QPushButton("一键签到")
        self.one_click_check_in_btn.clicked.connect(self.one_click_check_in)
        device_btn_layout.addWidget(self.one_click_check_in_btn)

        device_btn_layout.addStretch()

        # 设备表格
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(5)
        self.device_table.setHorizontalHeaderLabels([
            "设备名称", "连接地址", "硬币数量", "上次签到时间", "操作"
        ])
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.device_table.setSelectionBehavior(QTableWidget.SelectRows)

        device_layout.addLayout(device_btn_layout)
        device_layout.addWidget(self.device_table)

        # 日志区域
        log_group = QGroupBox("日志信息")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        # 日志操作按钮
        log_btn_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.clicked.connect(self.clear_logs)
        self.refresh_log_btn = QPushButton("刷新日志")
        self.refresh_log_btn.clicked.connect(self.refresh_logs)
        log_btn_layout.addWidget(self.clear_log_btn)
        log_btn_layout.addWidget(self.refresh_log_btn)
        log_btn_layout.addStretch()
        log_layout.addLayout(log_btn_layout)

        layout.addWidget(device_group)
        layout.addWidget(log_group)

    def _show_connect_device_dialog(self):
        """显示连接设备对话框"""
        # 创建连接设备对话框
        dialog = DeviceConnectionDialog(self.maa_manager)
        dialog.device_selected.connect(self._connect_device)
        if dialog.exec() == DeviceConnectionDialog.DialogCode.Accepted:
            # 设备连接对话框关闭
            pass

    def _connect_device(self, device_info):
        """连接设备"""
        try:
            device_serial = device_info.address  # 使用设备地址作为唯一标识符
            device_display_name = f"{device_info.name} ({device_info.address})"  # 显示用名称

            if self.maa_manager.is_device_connected(device_serial):
                # 这里应该有一个消息提示函数
                return

            # 连接设备
            tasker = self.maa_manager.connect_device(device_info)

            # 刷新设备列表显示
            self.refresh_device_list()
        except Exception as e:
            self.logger.error(f"连接设备时出错: {e}")

    def refresh_device_list(self):
        """刷新设备列表"""
        try:
            device_serial_list = self.maa_manager.get_connected_device_serial_list()
            self.device_table.setRowCount(len(device_serial_list))

            for row, device_serial in enumerate(device_serial_list):
                self.device_table.setItem(row, 0, QTableWidgetItem(""))
                self.device_table.setItem(row, 1, QTableWidgetItem(device_serial))
                self.device_table.setItem(row, 2, QTableWidgetItem("0"))

                last_sign_in = "从未"
                self.device_table.setItem(row, 3, QTableWidgetItem(last_sign_in))

                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)

                connect_btn = QPushButton("连接" if "已连接" != "已连接" else "断开")
                connect_btn.clicked.connect(
                    lambda checked, addr=device_serial: self.toggle_device_connection(addr)
                )
                sign_in_btn = QPushButton("签到")
                sign_in_btn.clicked.connect(
                    lambda checked, addr=device_serial: self.sign_in_device(addr)
                )

                btn_layout.addWidget(connect_btn)
                btn_layout.addWidget(sign_in_btn)
                btn_layout.addStretch()

                self.device_table.setCellWidget(row, 4, btn_widget)
        except Exception as e:
            self.logger.error(f"刷新设备列表失败: {e}")

    def toggle_device_connection(self, address: str):
        """切换设备连接状态"""
        try:
            pass
            self.refresh_device_list()
        except Exception as e:
            self.logger.error(f"切换设备连接状态失败: {e}")

    def one_click_check_in(self):
        """一键签到"""

    def sign_in_device(self, address: str):
        """为设备签到"""
        try:
            pass
            self.refresh_device_list()
        except Exception as e:
            self.logger.error(f"设备签到失败: {e}")

    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()

    def refresh_logs(self):
        """刷新日志"""
        # TODO: 实现日志刷新逻辑
        pass
