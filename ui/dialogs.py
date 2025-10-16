from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QPushButton, 
    QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, 
    QMessageBox, QListWidgetItem, QLineEdit
)
from PySide6.QtCore import Qt


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
    
    def __init__(self, parent=None, device_manager=None):
        super().__init__(parent)
        self.device_manager = device_manager
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
        if not self.device_manager:
            return
            
        self.device_table.setRowCount(0)  # 清空表格
        
        # 检测设备
        detected_devices = self.device_manager.detect_devices()
        self.device_manager.update_device_list(detected_devices)
        
        # 显示所有设备
        self.device_table.setRowCount(len(self.device_manager.devices))
        for row, device in enumerate(self.device_manager.devices):
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