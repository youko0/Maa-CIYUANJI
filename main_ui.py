import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QFormLayout, QTabWidget, QListWidget, QTableWidget, QTableWidgetItem,
    QDialog, QListWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QThread, Signal
from config_manager import ConfigManager
from novel_processor import NovelProcessor
from logger import app_logger
from device_manager import device_manager, DeviceInfo
import os
import json


class NovelProcessorThread(QThread):
    """小说处理线程"""
    progress_updated = Signal(str)
    finished_signal = Signal(bool, str)
    
    def __init__(self, config_manager, novel_processor):
        super().__init__()
        self.config_manager = config_manager
        self.novel_processor = novel_processor
        self.running = False
    
    def run(self):
        """执行小说处理任务"""
        try:
            self.running = True
            self.progress_updated.emit("开始处理小说...")
            
            config = self.config_manager.get_config()
            target_novel = config.get("target_novel", "")
            start_chapter = config.get("start_chapter", "")
            end_chapter = config.get("end_chapter", "")
            
            if not target_novel:
                self.finished_signal.emit(False, "请先设置目标小说")
                return
            
            self.progress_updated.emit(f"正在处理小说: {target_novel}")
            self.progress_updated.emit(f"处理章节范围: {start_chapter} - {end_chapter}")
            
            # 这里应该是实际的小说处理逻辑
            # 包括使用MaaFramework进行自动化操作
            # 暂时用模拟代码替代
            
            import time
            for i in range(10):
                if not self.running:
                    break
                self.progress_updated.emit(f"处理进度: {i+1}/10")
                # 模拟章节处理
                chapter_name = f"第{i+1}章"
                if not self.novel_processor.is_chapter_processed(target_novel, chapter_name):
                    # 模拟章节内容
                    content = {
                        "text": f"这是{chapter_name}的内容...",
                        "page": i+1
                    }
                    # 保存章节内容
                    self.novel_processor.save_chapter_content(
                        target_novel, 
                        chapter_name, 
                        content, 
                        "device_001"  # 设备ID，实际应用中应该动态获取
                    )
                    self.progress_updated.emit(f"已保存章节: {chapter_name}")
                else:
                    self.progress_updated.emit(f"章节已存在，跳过: {chapter_name}")
                time.sleep(0.5)
            
            self.finished_signal.emit(True, "小说处理完成")
        except Exception as e:
            self.finished_signal.emit(False, f"处理出错: {str(e)}")
    
    def stop(self):
        """停止处理"""
        self.running = False


class AddNovelDialog(QDialog):
    """添加小说对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加小说")
        self.setModal(True)
        self.resize(300, 200)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 小说名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("小说名称:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 起始章节
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("起始章节:"))
        self.start_edit = QLineEdit()
        start_layout.addWidget(self.start_edit)
        layout.addLayout(start_layout)
        
        # 结束章节
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("结束章节:"))
        self.end_edit = QLineEdit()
        end_layout.addWidget(self.end_edit)
        layout.addLayout(end_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "start": self.start_edit.text(),
            "end": self.end_edit.text()
        }


class ConnectDeviceDialog(QDialog):
    """连接设备对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("连接设备")
        self.setModal(True)
        self.resize(600, 400)
        # 设置弹窗在父窗口正中间显示
        if parent:
            parent_geo = parent.geometry()
            self.move(
                parent_geo.center().x() - self.width() // 2,
                parent_geo.center().y() - self.height() // 2
            )
        self.selected_device = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 设备列表（使用表格形式，与主页保持一致）
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(4)
        self.device_table.setHorizontalHeaderLabels(["设备名称", "连接地址", "ADB路径", "状态"])
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.device_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # 优化选中行的显示样式
        self.device_table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTableWidget {
                selection-background-color: #0078d4;
                selection-color: white;
            }
        """)
        self.device_table.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(QLabel("双击设备进行连接:"))
        layout.addWidget(self.device_table)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("连接选中设备")
        self.connect_btn.clicked.connect(self.accept)
        self.connect_btn.setEnabled(False)  # 默认禁用，选择设备后启用
        self.refresh_btn = QPushButton("刷新设备列表")
        self.refresh_btn.clicked.connect(self.refresh_devices)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接选择变化信号
        self.device_table.itemSelectionChanged.connect(self.on_device_selected)
        
        # 初始化设备列表
        self.refresh_devices()
    
    def refresh_devices(self):
        """刷新设备列表 - 显示所有识别到的设备"""
        self.device_table.setRowCount(0)  # 清空表格
        
        # 检测设备
        detected_devices = device_manager.detect_devices()
        device_manager.update_device_list(detected_devices)
        
        # 显示所有设备
        self.device_table.setRowCount(len(device_manager.devices))
        for row, device in enumerate(device_manager.devices):
            self.device_table.setItem(row, 0, QTableWidgetItem(device.name))
            self.device_table.setItem(row, 1, QTableWidgetItem(device.address))
            self.device_table.setItem(row, 2, QTableWidgetItem(device.adb_path))
            status = "已连接" if device.connected else "未连接"
            status_item = QTableWidgetItem(status)
            self.device_table.setItem(row, 3, status_item)
            
            # 设置状态列字体颜色
            if device.connected:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            
            # 已连接的设备设置为不可选
            if device.connected:
                for col in range(4):
                    item = self.device_table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
    
    def on_device_selected(self):
        """设备选择变化时更新连接按钮状态"""
        selected_rows = self.device_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            # 检查是否已连接
            status_item = self.device_table.item(row, 3)
            if status_item and status_item.text() == "未连接":
                self.connect_btn.setEnabled(True)
                # 获取选中的设备地址
                address_item = self.device_table.item(row, 1)
                if address_item:
                    self.selected_device = address_item.text()
                else:
                    self.selected_device = None
            else:
                self.connect_btn.setEnabled(False)
                self.selected_device = None
        else:
            self.connect_btn.setEnabled(False)
            self.selected_device = None
    
    def on_item_double_clicked(self, item):
        """双击设备项进行连接"""
        if item:
            row = item.row()
            # 检查是否已连接
            status_item = self.device_table.item(row, 3)
            if status_item and status_item.text() == "已连接":
                QMessageBox.information(self, "信息", "设备已连接")
                return
            
            # 设置选中设备并接受对话框
            self.device_table.selectRow(row)
            self.on_device_selected()
            if self.selected_device:
                self.accept()
    
    def get_selected_device(self):
        return self.selected_device


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.novel_processor = NovelProcessor(self.config_manager)
        self.processor_thread = None
        self.novels = []  # 小说列表
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("次元姬小说助手")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建Tab控件
        self.tab_widget = QTabWidget()
        # 设置当前tab标题加粗显示
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #ccc;
                padding: 8px 12px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #0078d4;
                color: white;
                font-weight: bold;
            }
        """)
        
        # 创建各个Tab页
        self.home_tab = self.create_home_tab()
        self.novel_tab = self.create_novel_tab()
        self.balance_tab = self.create_balance_tab()
        
        self.tab_widget.addTab(self.home_tab, "主页")
        self.tab_widget.addTab(self.novel_tab, "小说")
        self.tab_widget.addTab(self.balance_tab, "余额")
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.tab_widget)
        
        # 隐藏小说Tab，只有在开始识别时才显示
        self.tab_widget.setTabEnabled(1, False)
    
    def create_home_tab(self):
        """创建主页Tab"""
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        
        # 上部分：小说列表（使用表格显示）
        novel_group = QGroupBox("小说列表")
        novel_layout = QVBoxLayout()
        
        # 小说列表控件（使用表格）
        self.novel_table = QTableWidget()
        self.novel_table.setColumnCount(5)
        self.novel_table.setHorizontalHeaderLabels(["名称", "当前识别进度", "上次识别时间", "状态", "操作"])
        self.novel_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.novel_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # 设置选中行的样式
        self.novel_table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        novel_layout.addWidget(self.novel_table)
        
        # 小说操作按钮
        novel_btn_layout = QHBoxLayout()
        self.add_novel_btn = QPushButton("添加小说")
        self.add_novel_btn.clicked.connect(self.add_novel)
        self.delete_novel_btn = QPushButton("删除小说")
        self.delete_novel_btn.clicked.connect(self.delete_novel)
        self.refresh_novel_btn = QPushButton("刷新列表")
        self.refresh_novel_btn.clicked.connect(self.refresh_novel_list)
        
        novel_btn_layout.addWidget(self.add_novel_btn)
        novel_btn_layout.addWidget(self.delete_novel_btn)
        novel_btn_layout.addWidget(self.refresh_novel_btn)
        novel_layout.addLayout(novel_btn_layout)
        
        novel_group.setLayout(novel_layout)
        home_layout.addWidget(novel_group)
        
        # 下部分：设备列表
        device_group = QGroupBox("设备列表")
        device_layout = QVBoxLayout()
        
        # 设备列表控件（使用表格显示详细信息）
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(4)
        self.device_table.setHorizontalHeaderLabels(["设备名称", "连接地址", "ADB路径", "状态"])
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.device_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # 设置选中行的样式
        self.device_table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        device_layout.addWidget(self.device_table)
        
        # 设备操作按钮
        device_btn_layout = QHBoxLayout()
        self.connect_device_btn = QPushButton("连接设备")
        self.connect_device_btn.clicked.connect(self.connect_device)
        self.disconnect_device_btn = QPushButton("断开设备")
        self.disconnect_device_btn.clicked.connect(self.disconnect_device)
        
        device_btn_layout.addWidget(self.connect_device_btn)
        device_btn_layout.addWidget(self.disconnect_device_btn)
        device_layout.addLayout(device_btn_layout)
        
        device_group.setLayout(device_layout)
        home_layout.addWidget(device_group)
        
        return home_widget
    
    def create_novel_tab(self):
        """创建小说Tab"""
        novel_widget = QWidget()
        novel_layout = QVBoxLayout(novel_widget)
        
        # 上部分：小说信息和进度
        info_group = QGroupBox("小说识别信息")
        info_layout = QVBoxLayout()
        
        # 当前小说信息
        self.current_novel_label = QLabel("当前小说: 无")
        self.progress_label = QLabel("进度: 0/0")
        info_layout.addWidget(self.current_novel_label)
        info_layout.addWidget(self.progress_label)
        
        # 进度条（简化为标签）
        self.progress_info = QTextEdit()
        self.progress_info.setReadOnly(True)
        self.progress_info.setMaximumHeight(100)
        info_layout.addWidget(QLabel("识别进度:"))
        info_layout.addWidget(self.progress_info)
        
        info_group.setLayout(info_layout)
        novel_layout.addWidget(info_group)
        
        # 下部分：识别日志
        log_group = QGroupBox("识别日志")
        log_layout = QVBoxLayout()
        
        self.novel_log = QTextEdit()
        self.novel_log.setReadOnly(True)
        log_layout.addWidget(self.novel_log)
        
        log_group.setLayout(log_layout)
        novel_layout.addWidget(log_group)
        
        # 操作按钮
        novel_tab_btn_layout = QHBoxLayout()
        self.stop_novel_btn = QPushButton("停止识别")
        self.stop_novel_btn.clicked.connect(self.stop_novel_recognition)
        self.export_novel_btn = QPushButton("导出小说")
        self.export_novel_btn.clicked.connect(self.export_current_novel)
        
        novel_tab_btn_layout.addWidget(self.stop_novel_btn)
        novel_tab_btn_layout.addWidget(self.export_novel_btn)
        novel_layout.addLayout(novel_tab_btn_layout)
        
        return novel_widget
    
    def create_balance_tab(self):
        """创建余额Tab"""
        balance_widget = QWidget()
        balance_layout = QVBoxLayout(balance_widget)
        
        # 总余额信息
        total_balance_group = QGroupBox("总余额信息")
        total_layout = QVBoxLayout()
        
        self.total_balance_label = QLabel("所有设备代币总余额: 0")
        self.nearest_expire_label = QLabel("最近过期时间: 无")
        total_layout.addWidget(self.total_balance_label)
        total_layout.addWidget(self.nearest_expire_label)
        
        total_balance_group.setLayout(total_layout)
        balance_layout.addWidget(total_balance_group)
        
        # 各设备余额信息
        device_balance_group = QGroupBox("各设备余额信息")
        device_layout = QVBoxLayout()
        
        self.device_balance_table = QTableWidget()
        self.device_balance_table.setColumnCount(3)
        self.device_balance_table.setHorizontalHeaderLabels(["设备ID", "余额", "最近过期时间"])
        self.device_balance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        device_layout.addWidget(self.device_balance_table)
        
        device_balance_group.setLayout(device_layout)
        balance_layout.addWidget(device_balance_group)
        
        # 代币使用记录
        record_group = QGroupBox("代币使用记录")
        record_layout = QVBoxLayout()
        
        self.coin_record_log = QTextEdit()
        self.coin_record_log.setReadOnly(True)
        record_layout.addWidget(self.coin_record_log)
        
        record_group.setLayout(record_layout)
        balance_layout.addWidget(record_group)
        
        return balance_widget
    
    def load_data(self):
        """加载数据"""
        # 加载小说列表（从配置中读取或初始化）
        self.refresh_novel_list()
        
        # 检测并加载设备列表
        self.detect_devices()
        
        # 更新余额信息
        self.update_balance_info()
    
    def refresh_novel_list(self):
        """刷新小说列表"""
        self.novel_table.setRowCount(0)  # 清空表格
        config = self.config_manager.get_config()
        target_novel = config.get("target_novel", "")
        if target_novel:
            self.novel_table.setRowCount(1)
            self.novel_table.setItem(0, 0, QTableWidgetItem(target_novel))
            self.novel_table.setItem(0, 1, QTableWidgetItem("0/0"))  # 进度
            self.novel_table.setItem(0, 2, QTableWidgetItem("无"))  # 上次识别时间
            self.novel_table.setItem(0, 3, QTableWidgetItem("未开始"))  # 状态
            
            # 添加操作按钮
            start_btn = QPushButton("开始识别")
            start_btn.clicked.connect(lambda: self.start_novel_recognition_by_row(0))
            self.novel_table.setCellWidget(0, 4, start_btn)
    
    def refresh_device_list(self):
        """刷新设备列表 - 只显示已连接的设备"""
        self.device_table.setRowCount(0)  # 清空表格
        # 只显示已连接的设备
        connected_devices = [device for device in device_manager.devices if device.connected]
        self.device_table.setRowCount(len(connected_devices))
        for row, device in enumerate(connected_devices):
            self.device_table.setItem(row, 0, QTableWidgetItem(device.name))
            self.device_table.setItem(row, 1, QTableWidgetItem(device.address))
            self.device_table.setItem(row, 2, QTableWidgetItem(device.adb_path))
            status_item = QTableWidgetItem("已连接")
            self.device_table.setItem(row, 3, status_item)
            
            # 设置状态列字体为绿色
            status_item.setForeground(Qt.GlobalColor.darkGreen)
    
    def update_balance_info(self):
        """更新余额信息"""
        # 总余额
        total_coins = self.config_manager.get_total_coins()
        self.total_balance_label.setText(f"所有设备代币总余额: {total_coins}")
        
        # 最近过期时间
        coins = self.config_manager.get_stats().get("coins", [])
        if coins:
            # 简化处理，实际应该找出最近的过期时间
            nearest_expire = coins[0].get("expire_time", "无")
            self.nearest_expire_label.setText(f"最近过期时间: {nearest_expire}")
        else:
            self.nearest_expire_label.setText("最近过期时间: 无")
        
        # 更新设备余额表格（简化处理）
        self.device_balance_table.setRowCount(1)
        self.device_balance_table.setItem(0, 0, QTableWidgetItem("device_001"))
        self.device_balance_table.setItem(0, 1, QTableWidgetItem(str(total_coins)))
        self.device_balance_table.setItem(0, 2, QTableWidgetItem("2025-10-23 00:00:00"))
        
        # 更新代币使用记录（模拟）
        self.coin_record_log.append("[2025-10-16 10:30:00] 签到获得5个代币")
    
    def add_novel(self):
        """添加小说"""
        dialog = AddNovelDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data["name"]:
                # 保存到配置
                config = self.config_manager.get_config()
                config["target_novel"] = data["name"]
                config["start_chapter"] = data["start"]
                config["end_chapter"] = data["end"]
                self.config_manager.update_config(config)
                
                # 更新表格显示
                self.refresh_novel_list()
                
                app_logger.log_novel_action("添加小说", data["name"], f"章节范围: {data['start']} - {data['end']}")
    
    def delete_novel(self):
        """删除小说"""
        # 获取选中的行
        selected_rows = self.novel_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的小说")
            return
        
        row = selected_rows[0].row()
        novel_item = self.novel_table.item(row, 0)
        if novel_item:
            novel_name = novel_item.text()
            # 从配置中移除
            config = self.config_manager.get_config()
            if config.get("target_novel") == novel_name:
                config["target_novel"] = ""
                self.config_manager.update_config(config)
            
            # 更新表格显示
            self.refresh_novel_list()
            
            app_logger.log_novel_action("删除小说", novel_name)
    
    def disable_novel(self):
        """停用小说"""
        # 获取选中的行
        selected_rows = self.novel_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要停用的小说")
            return
        
        row = selected_rows[0].row()
        status_item = self.novel_table.item(row, 3)
        if status_item:
            if status_item.text() == "已停用":
                status_item.setText("未开始")
            else:
                status_item.setText("已停用")
    
    def start_novel_recognition_by_row(self, row):
        """根据行号开始小说识别"""
        # 切换到小说Tab
        self.tab_widget.setTabEnabled(1, True)
        self.tab_widget.setCurrentIndex(1)
        
        # 开始识别过程
        self.process_novel()
    
    def start_novel_recognition(self):
        """开始小说识别"""
        # 检查是否有小说
        if self.novel_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "请先添加小说")
            return
        
        # 检查是否选中了小说
        selected_rows = self.novel_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要识别的小说")
            return
        
        # 切换到小说Tab
        self.tab_widget.setTabEnabled(1, True)
        self.tab_widget.setCurrentIndex(1)
        
        # 开始识别过程
        self.process_novel()
    
    def detect_devices(self):
        """检测设备"""
        try:
            # 检测设备
            detected_devices = device_manager.detect_devices()
            device_manager.update_device_list(detected_devices)
            
            # 刷新显示
            self.refresh_device_list()
            
            app_logger.info(f"检测到 {len(detected_devices)} 个设备")
        except Exception as e:
            app_logger.error(f"检测设备失败: {e}")
            QMessageBox.critical(self, "错误", f"检测设备失败: {str(e)}")
    
    def connect_device(self):
        """连接设备"""
        dialog = ConnectDeviceDialog(self)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            selected_device_addr = dialog.get_selected_device()
            if selected_device_addr:
                if device_manager.connect_device(selected_device_addr):
                    self.refresh_device_list()
                    # 查找设备名称用于日志
                    device = device_manager.get_device_by_address(selected_device_addr)
                    if device:
                        app_logger.log_device_action("连接设备", device.name)
    
    def disconnect_device(self):
        """断开设备"""
        # 获取选中的行
        selected_rows = self.device_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要断开的设备")
            return
        
        disconnected_count = 0
        for index in selected_rows:
            row = index.row()
            # 安全地获取地址
            address_item = self.device_table.item(row, 1)
            if not address_item:
                continue
            address = address_item.text()
            device = device_manager.get_device_by_address(address)
            if device and device.connected:
                if device_manager.disconnect_device(address):
                    disconnected_count += 1
        
        # 刷新显示
        self.refresh_device_list()
        
        if disconnected_count > 0:
            app_logger.log_device_action("断开设备", f"成功断开{disconnected_count}个设备")
            QMessageBox.information(self, "成功", f"成功断开{disconnected_count}个设备")
        else:
            QMessageBox.information(self, "信息", "没有设备需要断开")
    
    def stop_novel_recognition(self):
        """停止小说识别"""
        self.stop_process()
    
    def export_current_novel(self):
        """导出当前小说"""
        config = self.config_manager.get_config()
        target_novel = config.get("target_novel", "")
        
        if not target_novel:
            QMessageBox.warning(self, "警告", "没有可导出的小说")
            app_logger.warning("尝试导出小说时未找到目标小说")
            return
        
        # 选择导出路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出小说", f"{target_novel}.txt", "Text Files (*.txt)"
        )
        
        if not file_path:
            app_logger.info("用户取消了小说导出操作")
            return
        
        # 导出小说
        try:
            success = self.novel_processor.export_novel_to_txt(target_novel, file_path)
            if success:
                self.novel_log.append(f"[成功] 小说已导出到: {file_path}")
                QMessageBox.information(self, "成功", f"小说已导出到: {file_path}")
                app_logger.log_novel_action("导出成功", target_novel, f"导出路径: {file_path}")
            else:
                self.novel_log.append("[错误] 导出小说失败")
                QMessageBox.critical(self, "错误", "导出小说失败")
                app_logger.error("小说导出失败")
        except Exception as e:
            self.novel_log.append(f"[错误] 导出小说失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"导出小说失败: {str(e)}")
            app_logger.error(f"小说导出异常: {e}")
    
    # 保留原来的方法，但进行适配
    def load_config(self):
        """加载配置"""
        config = self.config_manager.get_config()
        # 更新代币信息
        total_coins = self.config_manager.get_total_coins()
        self.update_balance_info()
    
    def save_config(self):
        """保存配置"""
        # 这个方法在新的UI中不再直接使用，但保留以避免错误
        self.update_status("配置已保存")
    
    def sign_in(self):
        """签到"""
        # 模拟签到过程
        from datetime import datetime, timedelta
        
        # 添加代币（模拟签到获得5个代币）
        expire_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        self.config_manager.add_coin(5, expire_time)
        
        # 更新UI
        self.update_balance_info()
        self.update_status("签到成功，获得5个代币")
        self.novel_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 签到成功，获得5个代币")
        app_logger.info("用户执行签到操作，获得5个代币")
    
    def process_novel(self):
        """处理小说"""
        if self.processor_thread and self.processor_thread.isRunning():
            return
        
        config = self.config_manager.get_config()
        target_novel = config.get("target_novel", "")
        if not target_novel:
            QMessageBox.warning(self, "警告", "请先添加并选择小说")
            return
        
        # 更新小说Tab信息
        self.current_novel_label.setText(f"当前小说: {target_novel}")
        self.progress_label.setText("进度: 0/10")
        
        self.processor_thread = NovelProcessorThread(self.config_manager, self.novel_processor)
        self.processor_thread.progress_updated.connect(self.update_novel_progress)
        self.processor_thread.finished_signal.connect(self.novel_process_finished)
        
        self.stop_novel_btn.setEnabled(True)
        self.novel_log.append(f"[{self.get_current_time()}] 开始识别小说: {target_novel}")
        
        self.processor_thread.start()
    
    def stop_process(self):
        """停止处理"""
        if self.processor_thread and self.processor_thread.isRunning():
            self.processor_thread.stop()
            self.stop_novel_btn.setEnabled(False)
    
    def novel_process_finished(self, success, message):
        """小说处理完成"""
        self.stop_novel_btn.setEnabled(False)
        
        if success:
            self.novel_log.append(f"[{self.get_current_time()}] {message}")
            self.update_status(f"处理完成: {message}")
            app_logger.log_novel_action("处理完成", "当前小说", message)
        else:
            self.novel_log.append(f"[{self.get_current_time()}] 错误: {message}")
            self.update_status(f"处理失败: {message}")
            app_logger.error(f"小说处理失败: {message}")
    
    def update_novel_progress(self, message):
        """更新小说进度"""
        self.novel_log.append(f"[{self.get_current_time()}] {message}")
        self.progress_info.append(message)
        
        # 更新进度标签（模拟）
        if "处理进度:" in message:
            self.progress_label.setText(message)
        
        # 记录到日志文件
        app_logger.info(f"小说处理进度: {message}")
    
    def get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def update_status(self, message):
        """更新状态信息"""
        # 在新的UI中，状态信息显示在小说Tab的日志中
        self.novel_log.append(f"[状态] {message}")
    
    def update_progress(self, message):
        """更新进度信息（保持兼容性）"""
        self.update_novel_progress(message)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()