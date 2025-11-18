from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from logger import app_logger


class HomeTabWidget(QWidget):
    """主页Tab控件"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
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
        self.add_novel_btn.clicked.connect(self.main_window.add_novel)
        self.delete_novel_btn = QPushButton("删除小说")
        self.delete_novel_btn.clicked.connect(self.main_window.delete_novel)
        self.refresh_novel_btn = QPushButton("刷新列表")
        self.refresh_novel_btn.clicked.connect(self.main_window.refresh_novel_list)
        
        novel_btn_layout.addWidget(self.add_novel_btn)
        novel_btn_layout.addWidget(self.delete_novel_btn)
        novel_btn_layout.addWidget(self.refresh_novel_btn)
        novel_layout.addLayout(novel_btn_layout)
        
        novel_group.setLayout(novel_layout)
        layout.addWidget(novel_group)
        
        # 下部分：设备列表
        device_group = QGroupBox("设备列表")
        device_layout = QVBoxLayout()
        
        # 设备列表控件（使用表格显示详细信息）
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(6)  # 增加到6列
        self.device_table.setHorizontalHeaderLabels(["设备名称", "连接地址", "ADB路径", "状态", "上次签到时间", "操作"])
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
        self.connect_device_btn.clicked.connect(self.main_window.connect_device)
        self.disconnect_device_btn = QPushButton("断开设备")
        self.disconnect_device_btn.clicked.connect(self.main_window.disconnect_device)
        self.sign_in_device_btn = QPushButton("全部签到")
        self.sign_in_device_btn.clicked.connect(self.main_window.sign_in_all_devices)
        self.sign_in_device_btn.setToolTip("为所有已连接的设备执行签到操作")
        
        device_btn_layout.addWidget(self.connect_device_btn)
        device_btn_layout.addWidget(self.disconnect_device_btn)
        device_btn_layout.addWidget(self.sign_in_device_btn)
        device_layout.addLayout(device_btn_layout)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
    
    def refresh_novel_list(self):
        """刷新小说列表"""
        self.novel_table.setRowCount(0)  # 清空表格
        config = self.main_window.config_manager.get_config()
        target_novel = config.get("target_novel", "")
        if target_novel:
            self.novel_table.setRowCount(1)
            self.novel_table.setItem(0, 0, QTableWidgetItem(target_novel))
            self.novel_table.setItem(0, 1, QTableWidgetItem("0/0"))  # 进度
            self.novel_table.setItem(0, 2, QTableWidgetItem("无"))  # 上次识别时间
            self.novel_table.setItem(0, 3, QTableWidgetItem("未开始"))  # 状态
            
            # 添加操作按钮
            start_btn = QPushButton("开始识别")
            start_btn.clicked.connect(lambda: self.main_window.start_novel_recognition_by_row(0))
            self.novel_table.setCellWidget(0, 4, start_btn)
    
    def refresh_device_list(self):
        """刷新设备列表 - 只显示已连接的设备"""
        self.device_table.setRowCount(0)  # 清空表格
        # 只显示已连接的设备
        connected_devices = self.main_window.maa_manager.get_connected_devices()
        
        # 通过MAA框架获取设备详细信息
        all_devices = self.main_window.maa_manager.find_devices()
        device_details = {device.address: device for device in all_devices}
        
        self.device_table.setRowCount(len(connected_devices))
        for row, device_serial in enumerate(connected_devices):
            # 获取设备详细信息
            if device_serial in device_details:
                device = device_details[device_serial]
                self.device_table.setItem(row, 0, QTableWidgetItem(device.name))
                self.device_table.setItem(row, 1, QTableWidgetItem(device.address))
                self.device_table.setItem(row, 2, QTableWidgetItem(str(device.adb_path)))
            else:
                # 如果找不到详细信息，使用默认值
                self.device_table.setItem(row, 0, QTableWidgetItem(f"设备 {device_serial}"))
                self.device_table.setItem(row, 1, QTableWidgetItem(device_serial))
                self.device_table.setItem(row, 2, QTableWidgetItem("N/A"))
                
            status_item = QTableWidgetItem("已连接")
            self.device_table.setItem(row, 3, status_item)
            
            # 设置状态列字体为绿色
            status_item.setForeground(Qt.GlobalColor.darkGreen)
            
            # 添加上次签到时间
            last_sign_in = self.main_window.device_sign_in_status.get(device_serial, "未签到")
            self.device_table.setItem(row, 4, QTableWidgetItem(last_sign_in))
            
            # 添加操作按钮
            operation_widget = QWidget()
            operation_layout = QHBoxLayout(operation_widget)
            operation_layout.setContentsMargins(0, 0, 0, 0)
            
            sign_in_btn = QPushButton("签到")
            sign_in_btn.clicked.connect(lambda checked, ds=device_serial: self.main_window.sign_in_device_by_serial(ds))
            refresh_btn = QPushButton("刷新余额")
            refresh_btn.clicked.connect(lambda checked, ds=device_serial: self.main_window.refresh_device_balance(ds))
            
            operation_layout.addWidget(sign_in_btn)
            operation_layout.addWidget(refresh_btn)
            operation_widget.setLayout(operation_layout)
            
            self.device_table.setCellWidget(row, 5, operation_widget)
