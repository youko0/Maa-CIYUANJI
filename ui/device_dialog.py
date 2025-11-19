# -*- coding: utf-8 -*-
"""
设备连接对话框
支持MaaFramework设备发现和连接
"""

import logging
from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QProgressBar, QTextEdit, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont

from maa.toolkit import AdbDevice
from core.maa_manager import MaaFrameworkManager


class DeviceDiscoveryThread(QThread):
    """
    设备发现线程
    在后台扫描可用的ADB设备
    """

    # 信号定义
    devices_found = Signal(list)  # 发现设备列表
    discovery_finished = Signal()  # 发现完成
    error_occurred = Signal(str)  # 发生错误

    def __init__(self, maa_manager: MaaFrameworkManager):
        super().__init__()
        self.maa_manager = maa_manager
        self.logger = logging.getLogger(__name__)

    def run(self):
        """执行设备发现"""
        try:
            self.logger.info("开始扫描ADB设备...")
            devices = self.maa_manager.find_devices()
            self.devices_found.emit(devices)
            self.logger.info(f"设备扫描完成，找到 {len(devices)} 个设备")
        except Exception as e:
            error_msg = f"设备扫描失败: {e}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            self.discovery_finished.emit()


class DeviceConnectionDialog(QDialog):
    """
    设备连接对话框
    显示可用设备列表并支持连接操作
    """

    # 信号定义
    device_selected = Signal(object)  # 设备选择信号
    device_connect_completed = Signal()  # 设备连接完成事件

    def __init__(self, maa_manager: MaaFrameworkManager, parent=None):
        super().__init__(parent)
        self.maa_manager = maa_manager
        self.logger = logging.getLogger(__name__)
        self.devices: List[AdbDevice] = []
        self.discovery_thread: Optional[DeviceDiscoveryThread] = None

        self.setWindowTitle("连接设备")
        self.setModal(True)
        self.resize(750, 550)

        self._setup_ui()
        self._connect_signals()

        # 自动开始设备发现
        self._start_device_discovery()

    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)

        # 标题和说明
        self._setup_header(layout)

        # 设备列表
        self._setup_device_table(layout)

        # 控制按钮
        self._setup_control_buttons(layout)

        # 状态和日志
        self._setup_status_area(layout)

    def _setup_header(self, parent_layout):
        """设置标题区域"""
        header_group = QGroupBox("设备连接")
        header_layout = QVBoxLayout(header_group)

        title_label = QLabel("MaaFramework 设备管理")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel("请选择要连接的ADB设备。确保设备已开启USB调试并授权此计算机。")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin: 10px;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(desc_label)

        parent_layout.addWidget(header_group)

    def _setup_device_table(self, parent_layout):
        """设置设备列表表格"""
        table_group = QGroupBox("可用设备")
        table_layout = QVBoxLayout(table_group)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(4)
        self.device_table.setHorizontalHeaderLabels([
            "设备名称", "连接地址", "ADB路径", "状态"
        ])

        # 设置表格属性
        header = self.device_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.device_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.device_table.setAlternatingRowColors(True)

        table_layout.addWidget(self.device_table)
        parent_layout.addWidget(table_group)

    def _setup_control_buttons(self, parent_layout):
        """设置控制按钮"""
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("刷新设备列表")
        self.refresh_btn.setMinimumHeight(35)

        self.connect_btn = QPushButton("连接选中设备")
        self.connect_btn.setMinimumHeight(35)
        self.connect_btn.setEnabled(False)

        self.connect_all_btn = QPushButton("连接所有设备")
        self.connect_all_btn.setMinimumHeight(35)
        self.connect_all_btn.setEnabled(False)

        self.close_btn = QPushButton("关闭")
        self.close_btn.setMinimumHeight(35)

        # 全选按钮
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setMinimumHeight(35)

        button_layout.addWidget(self.select_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.connect_all_btn)
        button_layout.addWidget(self.close_btn)

        parent_layout.addLayout(button_layout)

    def _setup_status_area(self, parent_layout):
        """设置状态显示区域"""
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout(status_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #333; font-weight: bold; padding: 5px;")
        status_layout.addWidget(self.status_label)

        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #f5f5f5; font-family: monospace;")
        status_layout.addWidget(self.log_text)

        parent_layout.addWidget(status_group)

    def _connect_signals(self):
        """连接信号和槽"""
        self.refresh_btn.clicked.connect(self._start_device_discovery)
        self.connect_btn.clicked.connect(self._connect_selected_device)
        self.connect_all_btn.clicked.connect(self._connect_all_devices)
        self.close_btn.clicked.connect(self.reject)
        self.select_all_btn.clicked.connect(self._select_all_devices)

        self.device_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.device_table.itemDoubleClicked.connect(self._connect_selected_device)

    def _start_device_discovery(self):
        """开始设备发现"""
        if self.discovery_thread and self.discovery_thread.isRunning():
            return

        # 更新UI状态
        self._set_discovery_state(True)
        self._add_log("开始扫描设备...")

        # 启动发现线程
        self.discovery_thread = DeviceDiscoveryThread(self.maa_manager)
        self.discovery_thread.devices_found.connect(self._on_devices_found)
        self.discovery_thread.discovery_finished.connect(self._on_discovery_finished)
        self.discovery_thread.error_occurred.connect(self._on_discovery_error)
        self.discovery_thread.start()

    def _set_discovery_state(self, discovering: bool):
        """设置发现状态"""
        self.progress_bar.setVisible(discovering)
        if discovering:
            self.progress_bar.setRange(0, 0)  # 无限进度条
            self.status_label.setText("正在扫描设备...")
            self.refresh_btn.setEnabled(False)
        else:
            self.progress_bar.setVisible(False)
            self.refresh_btn.setEnabled(True)

    def _on_devices_found(self, devices: List[AdbDevice]):
        """处理发现的设备"""
        self.devices = devices
        self._update_device_table()
        self._add_log(f"找到 {len(devices)} 个设备")

    def _on_discovery_finished(self):
        """设备发现完成"""
        self._set_discovery_state(False)
        self.status_label.setText(f"扫描完成，找到 {len(self.devices)} 个设备")

    def _on_discovery_error(self, error_msg: str):
        """设备发现错误"""
        self._set_discovery_state(False)
        self.status_label.setText("扫描失败")
        self._add_log(f"错误: {error_msg}")
        QMessageBox.warning(self, "扫描错误", error_msg)

    def _update_device_table(self):
        """更新设备表格"""
        self.device_table.setRowCount(len(self.devices))

        # 更新连接所有设备按钮的状态
        has_unconnected_devices = False

        for i, device in enumerate(self.devices):
            # 设备名称
            name_item = QTableWidgetItem(device.name or "未知设备")
            self.device_table.setItem(i, 0, name_item)

            # 连接地址
            address_item = QTableWidgetItem(device.address)
            self.device_table.setItem(i, 1, address_item)

            # ADB路径
            adb_path_item = QTableWidgetItem(str(device.adb_path))
            self.device_table.setItem(i, 2, adb_path_item)

            # 状态 - 使用设备地址作为唯一标识符
            device_key = device.address  # 使用地址作为唯一标识
            status = "已连接" if self.maa_manager.is_device_connected(device_key) else "未连接"
            status_item = QTableWidgetItem(status)
            if status == "已连接":
                status_item.setBackground(Qt.GlobalColor.green)
            else:
                has_unconnected_devices = True
            self.device_table.setItem(i, 3, status_item)

        # 根据是否有未连接的设备来启用/禁用连接所有设备按钮
        self.connect_all_btn.setEnabled(has_unconnected_devices and len(self.devices) > 0)

    def _select_all_devices(self):
        """全选所有设备"""
        if not self.devices:
            return

        # 检查当前是否全部选中
        selected_rows = self.device_table.selectionModel().selectedRows()
        if len(selected_rows) == len(self.devices):
            # 如果全部选中，则取消全部选中
            self.device_table.clearSelection()
            self._add_log("取消全选")
        else:
            # 否则选中所有设备
            self.device_table.selectAll()
            self._add_log(f"全选 {len(self.devices)} 个设备")

    def _on_selection_changed(self):
        """选择变化处理"""
        selected_rows = self.device_table.selectionModel().selectedRows()
        self.connect_btn.setEnabled(len(selected_rows) > 0)

    def _connect_all_devices(self):
        """连接所有设备"""
        for device in self.devices:
            if self.maa_manager.is_device_connected(device.address):
                continue
            self.maa_manager.connect_device(device)

        self.device_connect_completed.emit()
        self.accept()
    def _connect_selected_device(self):
        """连接选中的设备"""
        selected_rows = self.device_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要连接的设备")
            return

        # 获取所有选中的设备
        devices_to_connect = []
        already_connected = []

        for selected_row in selected_rows:
            row = selected_row.row()
            if row >= len(self.devices):
                continue

            device = self.devices[row]
            device_key = device.address

            # 检查设备是否已连接
            if self.maa_manager.is_device_connected(device_key):
                already_connected.append(f"{device.name} ({device.address})")
            else:
                devices_to_connect.append(device)

        # 显示已连接的设备信息
        if already_connected:
            msg = f"以下设备已经连接:\n" + "\n".join(already_connected)
            if devices_to_connect:
                msg += f"\n\n将连接其余 {len(devices_to_connect)} 个设备"
            QMessageBox.information(self, "连接状态", msg)

        # 连接未连接的设备
        if devices_to_connect:
            if len(devices_to_connect) == 1:
                # 单个设备直接连接
                device = devices_to_connect[0]
                self.device_selected.emit(device)
                self._add_log(f"选择连接设备: {device.name} ({device.address})")
                self.accept()
            else:
                # 多个设备需要用户确认
                device_list = "\n".join([f"{d.name} ({d.address})" for d in devices_to_connect])
                reply = QMessageBox.question(
                    self, "确认连接",
                    f"确认连接以下 {len(devices_to_connect)} 个设备？\n\n{device_list}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # 连接第一个设备（暂时方案，未来可以扩展为批量连接）
                    device = devices_to_connect[0]
                    self.device_selected.emit(device)
                    self._add_log(f"选择连接设备: {device.name} ({device.address})")
                    self._add_log(f"注意: 其余 {len(devices_to_connect) - 1} 个设备需要手动连接")
                    self.accept()
        else:
            QMessageBox.information(self, "提示", "所选设备均已连接")

    def _add_log(self, message: str):
        """添加日志消息"""
        self.log_text.append(message)
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止发现线程
        if self.discovery_thread and self.discovery_thread.isRunning():
            self.discovery_thread.quit()
            self.discovery_thread.wait(3000)

        event.accept()


class QuickConnectDialog(QDialog):
    """
    快速连接对话框
    用于手动输入设备地址进行连接
    """

    device_address_entered = Signal(str)  # 设备地址输入信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("快速连接设备")
        self.setModal(True)
        self.resize(400, 200)

        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)

        # 说明
        desc_label = QLabel("请输入设备连接地址（例如: 127.0.0.1:5555）")
        layout.addWidget(desc_label)

        # 输入框
        from PySide6.QtWidgets import QLineEdit
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("127.0.0.1:5555")
        layout.addWidget(self.address_input)

        # 按钮
        button_layout = QHBoxLayout()

        connect_btn = QPushButton("连接")
        cancel_btn = QPushButton("取消")

        connect_btn.clicked.connect(self._connect_device)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(connect_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _connect_device(self):
        """连接设备"""
        address = self.address_input.text().strip()
        if not address:
            QMessageBox.warning(self, "错误", "请输入设备地址")
            return

        self.device_address_entered.emit(address)
        self.accept()
