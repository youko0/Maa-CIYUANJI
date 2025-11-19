#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小说标签页模块
包含小说管理和识别进度显示功能
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QTextEdit, QPushButton, QHeaderView, QDialog, QLineEdit, QFormLayout
)

from core.config_manager import get_config_manager
from core.novel_manager import get_novel_manager
from utils.logger import get_logger


class NovelTab(QWidget):
    """小说标签页"""

    def __init__(self):
        super().__init__()
        self.novel_manager = get_novel_manager()
        self.config_manager = get_config_manager()
        self.logger = get_logger()

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 小说管理区域
        novel_group = QGroupBox("小说管理")
        novel_layout = QVBoxLayout(novel_group)

        # 小说操作按钮
        novel_btn_layout = QHBoxLayout()
        self.add_novel_btn = QPushButton("添加小说")
        self.add_novel_btn.clicked.connect(self.add_novel)
        self.refresh_novel_btn = QPushButton("刷新列表")
        self.refresh_novel_btn.clicked.connect(self.refresh_novel_list)
        novel_btn_layout.addWidget(self.add_novel_btn)
        novel_btn_layout.addWidget(self.refresh_novel_btn)
        novel_btn_layout.addStretch()

        # 小说表格
        self.novel_table = QTableWidget()
        self.novel_table.setColumnCount(5)
        self.novel_table.setHorizontalHeaderLabels([
            "名称", "当前识别进度", "上次识别时间", "状态", "操作"
        ])
        self.novel_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.novel_table.setSelectionBehavior(QTableWidget.SelectRows)

        novel_layout.addLayout(novel_btn_layout)
        novel_layout.addWidget(self.novel_table)

        # 识别进度区域
        progress_group = QGroupBox("识别进度")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        progress_layout.addWidget(self.progress_text)

        layout.addWidget(novel_group)
        layout.addWidget(progress_group)

    def add_novel(self):
        """添加小说"""
        dialog = AddNovelDialog(self)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.name_edit.text()
            start_chapter = int(dialog.start_chapter_edit.text() or "1")
            end_chapter = int(dialog.end_chapter_edit.text() or "9999")

            success = self.novel_manager.add_novel(name, start_chapter, end_chapter)
            if success:
                self.refresh_novel_list()

    def refresh_novel_list(self):
        """刷新小说列表"""
        try:
            novels = self.novel_manager.get_all_novels()
            self.novel_table.setRowCount(len(novels))

            for row, novel in enumerate(novels):
                self.novel_table.setItem(row, 0, QTableWidgetItem(novel.name))

                # 进度显示
                progress_text = f"{novel.progress:.1f}%"
                self.novel_table.setItem(row, 1, QTableWidgetItem(progress_text))

                last_recognize = novel.last_recognize_time or "从未"
                self.novel_table.setItem(row, 2, QTableWidgetItem(last_recognize))

                status_text = "启用" if novel.is_active else "停用"
                self.novel_table.setItem(row, 3, QTableWidgetItem(status_text))

                # 操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)

                start_btn = QPushButton("开始识别")
                start_btn.clicked.connect(
                    lambda checked, name=novel.name: self.start_novel_recognize(name)
                )

                toggle_btn = QPushButton("停用" if novel.is_active else "启用")
                toggle_btn.clicked.connect(
                    lambda checked, name=novel.name: self.toggle_novel_status(name)
                )

                delete_btn = QPushButton("删除")
                delete_btn.clicked.connect(
                    lambda checked, name=novel.name: self.delete_novel(name)
                )

                btn_layout.addWidget(start_btn)
                btn_layout.addWidget(toggle_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.addStretch()

                self.novel_table.setCellWidget(row, 4, btn_widget)
        except Exception as e:
            self.logger.error(f"刷新小说列表失败: {e}")

    def start_novel_recognize(self, name: str):
        """开始识别小说"""
        try:
            success = self.novel_manager.start_recognize(name)
            # TODO: 启动实际的识别任务
        except Exception as e:
            self.logger.error(f"开始识别小说失败: {e}")

    def toggle_novel_status(self, name: str):
        """切换小说状态"""
        try:
            novel = None
            for n in self.novel_manager.get_all_novels():
                if n.name == name:
                    novel = n
                    break

            if not novel:
                return

            if novel.is_active:
                success = self.novel_manager.disable_novel(name)
            else:
                success = self.novel_manager.enable_novel(name)

            if success:
                self.refresh_novel_list()
        except Exception as e:
            self.logger.error(f"切换小说状态失败: {e}")

    def delete_novel(self, name: str):
        """删除小说"""
        try:
            success = self.novel_manager.remove_novel(name)
            if success:
                self.refresh_novel_list()
        except Exception as e:
            self.logger.error(f"删除小说失败: {e}")


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
