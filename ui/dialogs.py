from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QPushButton, 
    QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, 
    QMessageBox, QListWidgetItem, QLineEdit
)
from PySide6.QtCore import Qt
from logger import app_logger


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
    
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.selected_devices = []  # 存储选中的设备地址列表
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
        self.connect_all_btn = QPushButton("连接所有设备")
        self.connect_all_btn.clicked.connect(self.connect_all_devices)
        self.refresh_btn = QPushButton("刷新设备列表")
        self.refresh_btn.clicked.connect(self.refresh_devices)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.connect_all_btn)
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
        if not self.main_window:
            return
            
        self.device_table.setRowCount(0)  # 清空表格
        
        # 检测设备
        detected_devices = self.main_window.maa_manager.find_devices()
        
        # 显示所有设备
        self.device_table.setRowCount(len(detected_devices))
        for row, device in enumerate(detected_devices):
            self.device_table.setItem(row, 0, QTableWidgetItem(device.name))
            self.device_table.setItem(row, 1, QTableWidgetItem(device.address))
            self.device_table.setItem(row, 2, QTableWidgetItem(str(device.adb_path)))
            
            # 检查设备是否已连接
            is_connected = self.main_window.maa_manager.is_device_connected(device.address)
            status = "已连接" if is_connected else "未连接"
            status_item = QTableWidgetItem(status)
            self.device_table.setItem(row, 3, status_item)
            
            # 设置状态列字体颜色
            if is_connected:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            
            # 已连接的设备设置为不可选
            if is_connected:
                for col in range(4):
                    item = self.device_table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
    
    def on_device_selected(self):
        """设备选择变化时更新连接按钮状态"""
        selected_rows = self.device_table.selectionModel().selectedRows()
        if selected_rows:
            # 检查是否有未连接的设备
            has_unconnected = False
            self.selected_devices = []  # 存储所有选中的设备地址
            
            for index in selected_rows:
                row = index.row()
                # 检查是否已连接
                status_item = self.device_table.item(row, 3)
                if status_item and status_item.text() == "未连接":
                    has_unconnected = True
                    # 获取选中的设备地址
                    address_item = self.device_table.item(row, 1)
                    if address_item:
                        self.selected_devices.append(address_item.text())
            
            if has_unconnected:
                self.connect_btn.setEnabled(True)
            else:
                self.connect_btn.setEnabled(False)
                self.selected_devices = []
        else:
            self.connect_btn.setEnabled(False)
            self.selected_devices = []
    
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
            if self.selected_devices:
                self.accept()
            # 如果没有选中设备（可能是因为设备已连接），则不关闭对话框

    def connect_all_devices(self):
        """连接所有未连接的设备"""
        # 检查主窗口是否存在
        if not self.main_window:
            QMessageBox.warning(self, "错误", "主窗口未初始化")
            return
            
        # 获取所有未连接的设备
        unconnected_devices = []
        for row in range(self.device_table.rowCount()):
            status_item = self.device_table.item(row, 3)
            if status_item and status_item.text() == "未连接":
                address_item = self.device_table.item(row, 1)
                if address_item:
                    unconnected_devices.append(address_item.text())
        
        if not unconnected_devices:
            QMessageBox.information(self, "信息", "没有未连接的设备")
            return
        
        # 连接所有未连接的设备
        connected_count = 0
        for device_addr in unconnected_devices:
            # 查找设备详细信息
            device = None
            try:
                devices = self.main_window.maa_manager.find_devices()
                for d in devices:
                    if d.address == device_addr:
                        device = d
                        break
            except Exception as e:
                app_logger.error(f"查找设备失败 {device_addr}: {e}")
                continue
            
            if device:
                try:
                    # 使用MaaFramework连接设备
                    tasker = self.main_window.maa_manager.connect_device(device)
                    connected_count += 1
                except Exception as e:
                    app_logger.error(f"连接设备失败 {device_addr}: {e}")
        
        if connected_count > 0:
            # 刷新设备列表
            self.refresh_devices()
            # 更新主窗口设备列表
            try:
                self.main_window.refresh_device_list()
            except Exception as e:
                app_logger.error(f"刷新主窗口设备列表失败: {e}")
            app_logger.log_device_action("连接设备", f"成功连接{connected_count}个设备")
            QMessageBox.information(self, "成功", f"成功连接{connected_count}个设备")
        else:
            QMessageBox.information(self, "信息", "没有设备被成功连接")

    def get_selected_device(self):
        """获取选中的设备地址列表"""
        return self.selected_devices if hasattr(self, 'selected_devices') else []
