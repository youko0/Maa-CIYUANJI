#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主页标签页模块
包含设备管理和日志显示功能
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QTextEdit, QPushButton, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QTextCursor, QCloseEvent

from core.config_manager import get_config_manager
from core.maa_manager import get_maa_manager
from modules.device_task_thread_manager import get_device_task_thread_manager
from modules.game_logger import GameLoggerFactory
from ui.device_dialog import DeviceConnectionDialog
from utils.logger import get_logger
from utils.time_utils import TimeUtils


class HomeTab(QWidget):
    """主页标签页"""

    log_message_event = Signal(str)  # 日志消息

    def __init__(self):
        super().__init__()
        self.maa_manager = get_maa_manager()
        self.maa_manager.device_info_changed_event.connect(self.refresh_device_list)
        self.config_manager = get_config_manager()

        # 初始化UI
        self.init_ui()

        # 获取带Qt信号注入的日志记录器
        self.logger = get_logger(self.log_message_event)

        # 任务线程管理器
        self.task_thread_manager = get_device_task_thread_manager()

        # 连接所有设备日志到UI
        self._connect_device_logs_to_ui()

        # 添加一些测试日志
        self.logger.info("主页标签页初始化完成")

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
        self.one_click_connect_device_btn = QPushButton("一键连接设备")
        self.one_click_connect_device_btn.clicked.connect(self.one_click_connect_device)
        device_btn_layout.addWidget(self.one_click_connect_device_btn)
        self.one_click_check_in_btn = QPushButton("一键签到")
        self.one_click_check_in_btn.clicked.connect(self.one_click_check_in)
        device_btn_layout.addWidget(self.one_click_check_in_btn)
        self.one_click_refresh_balance_btn = QPushButton("一键刷新余额")
        self.one_click_refresh_balance_btn.clicked.connect(self.one_click_refresh_balance)
        device_btn_layout.addWidget(self.one_click_refresh_balance_btn)
        self.one_click_initialized_btn = QPushButton("一键初始化")
        self.one_click_initialized_btn.clicked.connect(self.one_click_initialized)
        device_btn_layout.addWidget(self.one_click_initialized_btn)

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
        self.log_message_event.connect(self._add_log_message)
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

    def _connect_device_logs_to_ui(self):
        """连接所有设备日志到UI显示"""
        # 连接已存在的设备日志记录器到UI
        GameLoggerFactory.connect_all_loggers_to_ui(self._add_log_message)

    def _add_log_message(self, message: str):
        """添加日志消息到UI"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.moveCursor(QTextCursor.End)

    def _show_connect_device_dialog(self):
        """显示连接设备对话框"""
        # 创建连接设备对话框
        dialog = DeviceConnectionDialog(self.maa_manager)
        dialog.device_selected.connect(self._connect_device)
        dialog.device_connect_completed.connect(self.refresh_device_list)
        if dialog.exec() == DeviceConnectionDialog.DialogCode.Accepted:
            # 设备连接对话框关闭
            pass

    def one_click_connect_device(self):
        """一键连接设备 - 异步调用"""
        self.logger.info("开始一键连接设备...")

        # 禁用按钮防止重复点击
        self.one_click_connect_device_btn.setEnabled(False)
        self.one_click_connect_device_btn.setText("连接中...")

        # 在新线程中执行连接操作
        self.connection_thread = DeviceConnectionThread(self.maa_manager, self.logger)
        self.connection_thread.connection_finished.connect(self._on_connection_finished)
        self.connection_thread.start()

    def _on_connection_finished(self, success: bool):
        """连接完成回调"""
        # 恢复按钮状态
        self.one_click_connect_device_btn.setEnabled(True)
        self.one_click_connect_device_btn.setText("一键连接设备")

        if success:
            self.logger.info("一键连接设备完成")
        else:
            self.logger.warning("一键连接设备完成，但没有成功连接任何设备")

        # 刷新设备列表显示
        self.refresh_device_list()

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
        self.logger.info("刷新设备列表")
        try:
            device_serial_list = self.maa_manager.get_connected_device_serial_list()
            self.device_table.setRowCount(len(device_serial_list))

            for row, device_serial in enumerate(device_serial_list):
                # 获取设备信息
                device_info = self.maa_manager.get_device_info(device_serial)
                self.device_table.setItem(row, 0, QTableWidgetItem(""))
                self.device_table.setItem(row, 1, QTableWidgetItem(device_info.device_serial))
                self.device_table.setItem(row, 2, QTableWidgetItem(str(device_info.balance)))

                last_sign_in = "从未" if device_info.last_sign_in_time is None else TimeUtils.format(device_info.last_sign_in_time)
                self.device_table.setItem(row, 3, QTableWidgetItem(last_sign_in))

                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)

                connect_btn = QPushButton("连接" if "已连接" != "已连接" else "断开")
                connect_btn.clicked.connect(
                    lambda checked, addr=device_info.device_serial: self.toggle_device_connection(addr)
                )

                btn_layout.addWidget(connect_btn)
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

    def start_device_task(self, device_serial, task_name):
        """
        启动线程
        :param device_serial:
        :param task_name:
        :return:
        """
        task_thread = self.task_thread_manager.start_device_task(
            device_serial=device_serial,
            task_name=task_name
        )
        if task_thread:
            # 连接任务线程的信号
            # task_thread.user_data_updated.connect(self._on_user_data_updated)
            # task_thread.execution_stopped.connect(self._stop_device_tasks)
            #
            # self.is_task_running = True
            # self._update_task_button_state()
            # self.task_status_changed.emit(self.device_serial, True)
            self.logger.info("任务启动成功")
        else:
            self.logger.info("任务启动失败")

    def one_click_check_in(self):
        """一键签到"""
        device_serial_list = self.maa_manager.get_connected_device_serial_list()
        for device_serial in device_serial_list:
            # 获取设备信息
            device_info = self.maa_manager.get_device_info(device_serial)
            # 判断今天是否已经进行签到
            if device_info.last_sign_in_time is None or TimeUtils.is_today(device_info.last_sign_in_time) is False:
                tasker = self.maa_manager.get_device_tasker(device_info.device_serial)
                # 执行签到逻辑
                self.start_device_task(device_info.device_serial, "signIn")

    def one_click_refresh_balance(self):
        """一键刷新余额"""
        device_serial_list = self.maa_manager.get_connected_device_serial_list()
        for device_serial in device_serial_list:
            self.start_device_task(device_serial, "refreshBalance")

    def one_click_initialized(self):
        """一键初始化"""
        device_serial_list = self.maa_manager.get_connected_device_serial_list()
        for device_serial in device_serial_list:
            # 判断设备是否已经初始化过
            device_info = self.maa_manager.get_device_info(device_serial)
            if device_info.is_initialized:
                self.logger.info(f"设备 {device_serial} 已经初始化过")
                continue
            self.start_device_task(device_serial, "initialized")

    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()

    def refresh_logs(self):
        """刷新日志"""
        # 清空日志显示
        self.log_text.clear()

    def closeEvent(self, event: QCloseEvent):
        """窗口关闭事件"""
        self.maa_manager.save_device_infos()


class DeviceConnectionThread(QThread):
    """设备连接线程"""
    connection_finished = Signal(bool)  # 连接完成信号

    def __init__(self, maa_manager, logger):
        super().__init__()
        self.maa_manager = maa_manager
        self.logger = logger

    def run(self):
        """执行连接操作"""
        try:
            success = self.maa_manager.one_click_connect_device(self.logger)
            self.connection_finished.emit(success)
        except Exception as e:
            self.logger.error(f"一键连接设备时发生错误: {e}")
            self.connection_finished.emit(False)
