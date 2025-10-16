from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)


class BalanceTabWidget(QWidget):
    """余额Tab控件"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 总余额信息
        total_balance_group = QGroupBox("总余额信息")
        total_layout = QVBoxLayout()
        
        self.total_balance_label = QLabel("所有设备代币总余额: 0")
        self.nearest_expire_label = QLabel("最近过期时间: 无")
        total_layout.addWidget(self.total_balance_label)
        total_layout.addWidget(self.nearest_expire_label)
        
        total_balance_group.setLayout(total_layout)
        layout.addWidget(total_balance_group)
        
        # 各设备余额信息
        device_balance_group = QGroupBox("各设备余额信息")
        device_layout = QVBoxLayout()
        
        self.device_balance_table = QTableWidget()
        self.device_balance_table.setColumnCount(3)
        self.device_balance_table.setHorizontalHeaderLabels(["设备ID", "余额", "最近过期时间"])
        self.device_balance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        device_layout.addWidget(self.device_balance_table)
        
        device_balance_group.setLayout(device_layout)
        layout.addWidget(device_balance_group)
        
        # 代币使用记录
        record_group = QGroupBox("代币使用记录")
        record_layout = QVBoxLayout()
        
        self.coin_record_log = QTextEdit()
        self.coin_record_log.setReadOnly(True)
        record_layout.addWidget(self.coin_record_log)
        
        record_group.setLayout(record_layout)
        layout.addWidget(record_group)
    
    def update_balance_info(self):
        """更新余额信息"""
        # 总余额
        total_coins = self.main_window.config_manager.get_total_coins()
        self.total_balance_label.setText(f"所有设备代币总余额: {total_coins}")
        
        # 最近过期时间
        coins = self.main_window.config_manager.get_stats().get("coins", [])
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