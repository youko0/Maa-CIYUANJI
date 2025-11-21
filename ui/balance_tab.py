#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
余额标签页模块
包含代币管理和使用记录显示功能
"""
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHeaderView
)
from PySide6.QtCore import Qt

from core.balance_manager import get_balance_manager
from core.config_manager import get_config_manager
from core.maa_manager import get_maa_manager
from utils.logger import get_logger
from utils.time_utils import TimeUtils


class BalanceTab(QWidget):
    """余额标签页"""

    def __init__(self):
        super().__init__()
        self.maa_manager = get_maa_manager()
        self.balance_manager = get_balance_manager()
        self.config_manager = get_config_manager()
        self.logger = get_logger()

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 余额概览区域
        overview_layout = QHBoxLayout()

        # 总余额显示
        total_coin_group = QGroupBox("总余额")
        total_coin_layout = QVBoxLayout(total_coin_group)
        self.total_coin_label = QLabel("0")
        self.total_coin_label.setAlignment(Qt.AlignCenter)
        self.total_coin_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        total_coin_layout.addWidget(self.total_coin_label)

        # 设备余额列表
        device_coin_group = QGroupBox("各设备余额")
        device_coin_layout = QVBoxLayout(device_coin_group)
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(3)
        self.device_table.setHorizontalHeaderLabels([
            "设备地址", "余额", "最早过期时间"
        ])

        header = self.device_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        # 启用表格排序功能
        self.device_table.setSortingEnabled(True)
        # 设置默认按照"下次执行时间"列升序排序（列索引为1）
        self.device_table.sortByColumn(2, Qt.SortOrder.AscendingOrder)
        device_coin_layout.addWidget(self.device_table)

        overview_layout.addWidget(total_coin_group, 1)
        overview_layout.addWidget(device_coin_group, 2)

        # 代币使用记录区域
        record_group = QGroupBox("代币使用记录")
        record_layout = QVBoxLayout(record_group)

        self.record_table = QTableWidget()
        self.record_table.setColumnCount(5)
        self.record_table.setHorizontalHeaderLabels([
            "设备地址", "小说名称", "章节名称", "使用数量", "时间"
        ])
        self.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        record_layout.addWidget(self.record_table)

        # 记录操作按钮
        record_btn_layout = QHBoxLayout()
        self.refresh_record_btn = QPushButton("刷新记录")
        self.refresh_record_btn.clicked.connect(self.refresh_records)
        record_btn_layout.addWidget(self.refresh_record_btn)
        record_btn_layout.addStretch()
        record_layout.addLayout(record_btn_layout)

        layout.addLayout(overview_layout)
        layout.addWidget(record_group)

    def refresh_balance_info(self):
        """刷新代币信息"""
        try:
            # 刷新总余额
            device_info_list = self.maa_manager.get_all_device_info_list()
            self.device_table.setRowCount(len(device_info_list))
            total_balance = 0
            for row, device_info in enumerate(device_info_list):
                total_balance += device_info.balance
                self.device_table.setItem(row, 0, QTableWidgetItem(device_info.device_serial))
                self.device_table.setItem(row, 1, QTableWidgetItem(str(device_info.balance)))
                # 获取代币最早过期时间
                device_balance_list = self.balance_manager.get_device_balance_list(device_info.device_serial)
                # 获取device_balance_list中，expire_time最小值对象
                balance_info = min(device_balance_list, key=lambda x: x.expire_time)
                self.device_table.setItem(row, 2, QTableWidgetItem(TimeUtils.format(balance_info.expire_time, "%Y-%m-%d") + " 凌晨将过期 " + str(balance_info.balance) + "个代币"))

            self.total_coin_label.setText(str(total_balance))

            # 刷新使用记录
            self.refresh_records()
        except Exception as e:
            self.logger.error(f"刷新代币信息失败: {e}")

    def refresh_records(self):
        """刷新代币使用记录"""
        try:
            records = self.balance_manager.get_all_records()
            self.record_table.setRowCount(len(records))

            for row, record in enumerate(records):
                self.record_table.setItem(row, 0, QTableWidgetItem(record.device_address))
                self.record_table.setItem(row, 1, QTableWidgetItem(record.novel_name))
                self.record_table.setItem(row, 2, QTableWidgetItem(record.chapter_name))
                self.record_table.setItem(row, 3, QTableWidgetItem(str(record.coins_used)))
                self.record_table.setItem(row, 4, QTableWidgetItem(record.timestamp))
        except Exception as e:
            self.logger.error(f"刷新代币使用记录失败: {e}")

    def closeEvent(self, event: QCloseEvent):
        """窗口关闭事件"""
        self.balance_manager.save_balances()
