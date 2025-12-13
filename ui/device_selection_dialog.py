# -*- coding: utf-8 -*-
"""
设备选择对话框
用于选择已连接的设备进行小说识别
"""

import logging
from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt

from core.domain.device_info import DeviceInfo
from core.maa_manager import get_maa_manager


class DeviceSelectionDialog(QDialog):
    """
    设备选择对话框
    显示已连接的设备列表供用户选择用于小说识别
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.maa_manager = get_maa_manager()
        self.logger = logging.getLogger(__name__)
        self.selected_devices: List[DeviceInfo] = []

        self.setWindowTitle("选择设备")
        self.setModal(True)
        self.resize(600, 400)

        self._setup_ui()
        self._connect_signals()
        self._update_device_table()

    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)

        # 标题和说明
        self._setup_header(layout)

        # 设备列表
        self._setup_device_table(layout)

        # 控制按钮
        self._setup_control_buttons(layout)

    def _setup_header(self, parent_layout):
        """设置标题区域"""
        header_group = QGroupBox("设备选择")
        header_layout = QVBoxLayout(header_group)

        title_label = QLabel("选择用于小说识别的设备")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel("请选择一个或多个已连接的设备来进行小说识别。")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin: 10px;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(desc_label)

        parent_layout.addWidget(header_group)

    def _setup_device_table(self, parent_layout):
        """设置设备列表表格"""
        table_group = QGroupBox("已连接设备")
        table_layout = QVBoxLayout(table_group)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(3)
        self.device_table.setHorizontalHeaderLabels([
            "选择", "设备名称", "设备序列号"
        ])

        # 设置表格属性
        header = self.device_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.device_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.device_table.setAlternatingRowColors(True)

        table_layout.addWidget(self.device_table)
        parent_layout.addWidget(table_group)

    def _setup_control_buttons(self, parent_layout):
        """设置控制按钮"""
        button_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setMinimumHeight(35)

        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setMinimumHeight(35)
        self.confirm_btn.setDefault(True)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(35)

        button_layout.addWidget(self.select_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)

        parent_layout.addLayout(button_layout)

    def _connect_signals(self):
        """连接信号和槽"""
        self.select_all_btn.clicked.connect(self._toggle_select_all)
        self.confirm_btn.clicked.connect(self._confirm_selection)
        self.cancel_btn.clicked.connect(self.reject)

    def _update_device_table(self):
        """更新设备表格"""
        # 获取已连接的设备信息
        connected_devices = self.maa_manager.get_connected_device_info_list()

        self.device_table.setRowCount(len(connected_devices))

        for i, device_info in enumerate(connected_devices):
            # 选择复选框
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # 默认选中所有设备
            self.device_table.setCellWidget(i, 0, checkbox)

            # 设备名称
            name_item = QTableWidgetItem(device_info.name or "未知设备")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.device_table.setItem(i, 1, name_item)

            # 设备序列号
            serial_item = QTableWidgetItem(device_info.device_serial)
            serial_item.setFlags(serial_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.device_table.setItem(i, 2, serial_item)

    def _toggle_select_all(self):
        """切换全选状态"""
        if not self.device_table.rowCount():
            return

        # 检查当前是否全部选中
        all_selected = True
        for i in range(self.device_table.rowCount()):
            checkbox = self.device_table.cellWidget(i, 0)
            if not checkbox.isChecked():
                all_selected = False
                break

        # 设置相反的状态
        for i in range(self.device_table.rowCount()):
            checkbox = self.device_table.cellWidget(i, 0)
            checkbox.setChecked(not all_selected)

    def _confirm_selection(self):
        """确认选择"""
        self.selected_devices = []

        # 收集选中的设备
        for i in range(self.device_table.rowCount()):
            checkbox = self.device_table.cellWidget(i, 0)
            if checkbox.isChecked():
                # 获取设备信息
                serial_item = self.device_table.item(i, 2)
                self.selected_devices.append(self.maa_manager.get_device_info(serial_item.text()))

        if not self.selected_devices:
            QMessageBox.warning(self, "提示", "请至少选择一个设备")
            return

        self.accept()

    def get_selected_devices(self) -> List[DeviceInfo]:
        """获取选中的设备列表"""
        return self.selected_devices
