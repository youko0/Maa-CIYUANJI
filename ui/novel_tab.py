#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小说标签页模块
包含小说管理和识别进度显示功能
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Any

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QTextEdit, QPushButton, QHeaderView, QDialog, QLineEdit, QFormLayout, QMessageBox, QCheckBox
)

from core.config_manager import get_config_manager
from core.maa_manager import get_maa_manager
from core.novel_manager import get_novel_manager
from modules.device_task_thread_manager import get_device_task_thread_manager
from utils.logger import get_logger

# 添加设备选择对话框的导入
from ui.device_selection_dialog import DeviceSelectionDialog


class NovelTab(QWidget):
    """小说标签页"""

    def __init__(self):
        super().__init__()
        self.novel_manager = get_novel_manager()
        self.config_manager = get_config_manager()
        self.maa_manager = get_maa_manager()
        self.logger = get_logger()

        # 任务线程管理器
        self.task_thread_manager = get_device_task_thread_manager()

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
        header = self.novel_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
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
            chapter_default_price = int(dialog.chapter_default_price_edit.text() or "15")  # 获取默认价格
            is_buy = dialog.is_buy_edit.isChecked()  # 获取是否购买

            # 修改调用add_novel方法，传入chapter_default_price和is_buy参数
            success = self.novel_manager.add_novel_with_price_and_buy(name, start_chapter, end_chapter, chapter_default_price, is_buy)
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
                start_btn.clicked.connect(lambda checked, name=novel.name: self.start_novel_recognize(name))
                export_btn = QPushButton("导出TXT")
                export_btn.clicked.connect(lambda checked, name=novel.name: self.export_novel(name))

                toggle_btn = QPushButton("停用" if novel.is_active else "启用")
                toggle_btn.clicked.connect(
                    lambda checked, name=novel.name: self.toggle_novel_status(name)
                )

                edit_btn = QPushButton("编辑")
                edit_btn.clicked.connect(
                    lambda checked, name=novel.name: self.edit_novel(name)
                )

                delete_btn = QPushButton("删除")
                delete_btn.clicked.connect(
                    lambda checked, name=novel.name: self.delete_novel(name)
                )

                btn_layout.addWidget(start_btn)
                btn_layout.addWidget(export_btn)
                btn_layout.addWidget(toggle_btn)
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.addStretch()

                self.novel_table.setCellWidget(row, 4, btn_widget)
        except Exception as e:
            self.logger.error(f"刷新小说列表失败: {e}")

    def start_novel_recognize(self, name: str):
        """开始识别小说"""
        try:
            novel_info = self.novel_manager.get_novel(name)
            # 判断小说状态是否启用
            if not novel_info.is_active:
                self.logger.error(f"小说 {name} 状态未启用")
                QMessageBox.warning(self, "提示", "小说状态未启用")
                return

            # 判断是否存在已连接的设备，如果没有则提示
            if not self.maa_manager.get_connected_device_serial_list():
                self.logger.error("请先连接设备")
                # 弹窗提示
                QMessageBox.warning(self, "提示", "请先连接设备")
                return

            # 弹出设备选择框
            dialog = DeviceSelectionDialog(self)
            if dialog.exec() == QDialog.Accepted:
                selected_devices = dialog.get_selected_devices()
                if not selected_devices:
                    QMessageBox.warning(self, "提示", "未选择任何设备")
                    return

                # 在选中的设备中进行识别
                self.logger.info(f"开始在 {len(selected_devices)} 个设备上识别小说: {name}")
                self.progress_text.append(f"开始在 {len(selected_devices)} 个设备上识别小说: {name}")

                ocr_novel_params: Dict[str, any] = {}
                current_chapter = novel_info.current_chapter
                # 需要根据选中的设备分配章节并启动识别任务
                for device_info in selected_devices:
                    # 根据设备余额，分配不同设备识别的章节数
                    chapter_quantity = 5
                    if novel_info.chapter_default_price > 0:
                        chapter_quantity = device_info.balance // novel_info.chapter_default_price
                    if chapter_quantity > 0:
                        chapter_list = []
                        i = 0
                        while i < chapter_quantity:
                            current_chapter = current_chapter + 1
                            # 判断当前章节是否已完成
                            if current_chapter in novel_info.complete_chapter:
                                if len(chapter_list) == 0:
                                    i -= 1
                                else:
                                    current_chapter -= 1
                                    break
                            else:
                                chapter_list.append(current_chapter)
                            i += 1

                        if len(chapter_list) == 0:
                            self.logger.info(f"- 设备 {device_info.name} ({device_info.device_serial}) 无剩余章节可识别")
                            continue
                        ocr_novel_params[device_info.device_serial] = {
                            "novel_name": name,
                            "chapter_list": chapter_list,
                        }
                        self.logger.info(f"- 准备在设备 {device_info.name} ({device_info.device_serial}) 上进行识别 {name} 小说，分别识别 {chapter_list} 章节")
                        self.progress_text.append(f"- 准备在设备 {device_info.name} ({device_info.device_serial}) 上进行识别 {name} 小说，分别识别 {chapter_list} 章节")
                        # 获取当前小说进度，根据当前连接设备自动分配章节
                        task_thread = self.task_thread_manager.start_device_task(
                            device_serial=device_info.device_serial,
                            task_name="ocrNovel",
                            task_params=ocr_novel_params[device_info.device_serial],
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
                            time.sleep(0.4)
                        else:
                            self.logger.info("任务启动失败")
                    else:
                        self.logger.warning(f"设备 {device_info.name} ({device_info.device_serial}) 余额不足 {novel_info.chapter_default_price}，跳过该设备")


        except Exception as e:
            self.logger.error(f"开始识别小说失败: {e}")

    def export_novel(self, name: str):
        """导出小说"""
        try:
            # 判断文件夹是否存在
            novels_path = Path(f"configs/novels/{name}")
            if not novels_path.exists():
                self.logger.error(f"本地不存在{name}小说识别记录")
                return
            # 识别目录下是否存在有效文件
            if not novels_path.glob("*.json"):
                self.logger.error(f"本地不存在{name}小说章节识别记录")
                return
            # 异步执行导出任务
            self._execute_export_novel(name, novels_path)

            # ocr_novel_params = {
            #     "novel_name": name,
            # }
            # task_thread = self.task_thread_manager.start_device_task(
            #     device_serial="export_novel_" + name,
            #     task_name="exportNovel",
            #     task_params=ocr_novel_params,
            # )
            # if task_thread:
            #     # 连接任务线程的信号
            #     # task_thread.user_data_updated.connect(self._on_user_data_updated)
            #     # task_thread.execution_stopped.connect(self._stop_device_tasks)
            #     #
            #     # self.is_task_running = True
            #     # self._update_task_button_state()
            #     # self.task_status_changed.emit(self.device_serial, True)
            #     self.logger.info("任务启动成功")
            # else:
            #     self.logger.info("任务启动失败")
            self.logger.info(f"导出《{name}》小说完成")

        except Exception as e:
            self.logger.error(f"导出《{name}》小说失败: {e}")

    def _execute_export_novel(self, name: str, novels_path):
        """执行导出小说"""
        # 创建导出文件
        export_file_path = Path(f"configs/novels/{name}.txt")
        # export_file_path.parent.mkdir(parents=True, exist_ok=True)

        # 清空或创建新文件
        export_file_path.write_text("", encoding='utf-8')

        # 获取novels_path目录下所有json文件，按照文件名数字升序排序
        json_files = list(novels_path.glob("*.json"))
        # 使用自定义排序键，按文件名中的数字排序
        json_file_list = sorted(json_files, key=lambda x: float(x.stem))
        for json_file in json_file_list:
            # 读取小说内容
            novel_chapter_obj = self._load_json_file(json_file)
            # 追加到导出文件
            with open(export_file_path, 'a', encoding='utf-8') as f:
                f.write(f'第{novel_chapter_obj["num"]}章 {novel_chapter_obj["name"]}\n')
                f.write(novel_chapter_obj["content"] + "\n\n\n")

    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """加载JSON文件"""
        if not file_path.exists():
            # 创建空的配置文件
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件 {file_path} 失败: {e}")
            return {}

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

    def edit_novel(self, name: str):
        """编辑小说"""
        try:
            # 获取要编辑的小说信息
            novel = None
            for n in self.novel_manager.get_all_novels():
                if n.name == name:
                    novel = n
                    break

            if not novel:
                return

            # 显示编辑对话框
            dialog = EditNovelDialog(self, novel)
            if dialog.exec() == QDialog.Accepted:
                new_name = dialog.name_edit.text()
                start_chapter = int(dialog.start_chapter_edit.text() or "1")
                end_chapter = int(dialog.end_chapter_edit.text() or "9999")
                current_chapter = int(dialog.current_chapter_edit.text() or "1")
                chapter_default_price = int(dialog.chapter_default_price_edit.text() or "15")  # 获取默认价格
                is_buy = dialog.is_buy_edit.isChecked()  # 获取是否购买

                # 解析已完成章节列表
                complete_chapter_str = dialog.complete_chapter_edit.text()
                if complete_chapter_str:
                    try:
                        complete_chapter = [int(x.strip()) for x in complete_chapter_str.split(",") if x.strip()]
                    except ValueError:
                        complete_chapter = []
                else:
                    complete_chapter = []

                # 如果名称改变，需要特殊处理
                if new_name != novel.name:
                    # 先删除旧的小说，再添加新的
                    self.novel_manager.remove_novel(novel.name)
                    # 注意：这里需要传递所有参数给add_novel_with_price_and_buy方法
                    self.novel_manager.add_novel_with_price_and_buy(new_name, start_chapter, end_chapter, chapter_default_price, is_buy)
                    # 更新新添加的小说的额外字段
                    new_novel = None
                    for n in self.novel_manager.get_all_novels():
                        if n.name == new_name:
                            new_novel = n
                            break
                    if new_novel:
                        new_novel.current_chapter = current_chapter
                        new_novel.complete_chapter = complete_chapter
                        self.novel_manager.save_novels()
                else:
                    # 只更新所有字段
                    novel.start_chapter = start_chapter
                    novel.end_chapter = end_chapter
                    novel.current_chapter = current_chapter
                    novel.complete_chapter = complete_chapter
                    novel.chapter_default_price = chapter_default_price  # 更新默认价格
                    novel.is_buy = is_buy  # 更新是否购买
                    self.novel_manager.save_novels()

                self.refresh_novel_list()
        except Exception as e:
            self.logger.error(f"编辑小说失败: {e}")

    def delete_novel(self, name: str):
        """删除小说"""
        try:
            # 显示确认对话框
            reply = QMessageBox.question(self, '确认删除', f'确定要删除小说 "{name}" 吗？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                success = self.novel_manager.remove_novel(name)
                if success:
                    self.refresh_novel_list()
        except Exception as e:
            self.logger.error(f"删除小说失败: {e}")

    def closeEvent(self, event: QCloseEvent):
        """窗口关闭事件"""
        # self.maa_manager.save_device_infos()
        self.novel_manager.save_novels()


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
        self.chapter_default_price_edit = QLineEdit("15")  # 添加默认价格输入框
        self.is_buy_edit = QCheckBox()  # 添加是否购买复选框

        layout.addRow("小说名称:", self.name_edit)
        layout.addRow("起始章节:", self.start_chapter_edit)
        layout.addRow("结束章节:", self.end_chapter_edit)
        layout.addRow("章节默认价格:", self.chapter_default_price_edit)  # 添加默认价格行
        layout.addRow("是否订购章节:", self.is_buy_edit)  # 添加是否购买行

        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)


class EditNovelDialog(QDialog):
    """编辑小说对话框"""

    def __init__(self, parent=None, novel=None):
        super().__init__(parent)
        self.novel = novel
        self.setWindowTitle("编辑小说")
        self.setModal(True)
        self.resize(300, 250)

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self.novel.name if self.novel else "")
        self.start_chapter_edit = QLineEdit(str(self.novel.start_chapter) if self.novel else "1")
        self.end_chapter_edit = QLineEdit(str(self.novel.end_chapter) if self.novel else "9999")
        self.current_chapter_edit = QLineEdit(str(self.novel.current_chapter) if self.novel else "1")
        self.complete_chapter_edit = QLineEdit(",".join(map(str, self.novel.complete_chapter)) if self.novel and self.novel.complete_chapter else "")
        self.chapter_default_price_edit = QLineEdit(str(self.novel.chapter_default_price) if self.novel else "15")  # 添加默认价格输入框
        self.is_buy_edit = QCheckBox()  # 添加是否购买复选框
        self.is_buy_edit.setChecked(self.novel.is_buy if self.novel else False)

        layout.addRow("小说名称:", self.name_edit)
        layout.addRow("起始章节:", self.start_chapter_edit)
        layout.addRow("结束章节:", self.end_chapter_edit)
        layout.addRow("当前章节:", self.current_chapter_edit)
        layout.addRow("已完成章节:", self.complete_chapter_edit)
        layout.addRow("章节默认价格:", self.chapter_default_price_edit)  # 添加默认价格行
        layout.addRow("是否订购章节:", self.is_buy_edit)  # 添加是否购买行

        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)
