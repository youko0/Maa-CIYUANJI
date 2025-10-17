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
            # 过滤掉余额为0的代币，然后找出最近的过期时间
            valid_coins = [coin for coin in coins if coin.get("balance", 0) > 0]
            if valid_coins:
                nearest_expire = min(valid_coins, key=lambda x: x.get("expire_time", "无"))["expire_time"]
                self.nearest_expire_label.setText(f"最近过期时间: {nearest_expire}")
            else:
                self.nearest_expire_label.setText("最近过期时间: 无")
        else:
            self.nearest_expire_label.setText("最近过期时间: 无")

        # 对coins列表按照device_serial进行分组，并计算每个设备的代币总余额和最近的过期时间
        device_balance = {}
        device_expire_time = {}
        
        for coin in coins:
            device_serial = coin.get("device_serial", "无")
            balance = coin.get("balance", 0)
            expire_time = coin.get("expire_time", "无")
            
            # 累加设备余额
            if device_serial in device_balance:
                device_balance[device_serial] += balance
            else:
                device_balance[device_serial] = balance
            
            # 更新设备最近过期时间（选择最早的过期时间）
            if device_serial in device_expire_time:
                if expire_time != "无" and (device_expire_time[device_serial] == "无" or expire_time < device_expire_time[device_serial]):
                    device_expire_time[device_serial] = expire_time
            else:
                device_expire_time[device_serial] = expire_time

        # 对设备余额进行排序，先按照过期时间升序、余额降序
        sorted_devices = sorted(device_balance.items(), key=lambda x: (device_expire_time.get(x[0], "无"), -x[1]))
        
        # 更新设备余额列表
        self.device_balance_table.setRowCount(len(sorted_devices))
        for i, (device_serial, balance) in enumerate(sorted_devices):
            self.device_balance_table.setItem(i, 0, QTableWidgetItem(device_serial))
            self.device_balance_table.setItem(i, 1, QTableWidgetItem(str(balance)))
            expire_time = device_expire_time.get(device_serial, "无")
            self.device_balance_table.setItem(i, 2, QTableWidgetItem(expire_time))

        # 更新代币使用记录
        self.coin_record_log.clear()
        # 显示所有代币记录，按过期时间排序
        sorted_coins = sorted(coins, key=lambda x: x.get("expire_time", "无"))
        for coin in sorted_coins:
            if coin.get("balance", 0) > 0:  # 只显示余额大于0的代币
                record = f"[{coin.get('expire_time', '无')}] 设备 {coin.get('device_serial', '无')} 余额: {coin.get('balance', 0)}/{coin.get('amount', 0)}"
                self.coin_record_log.append(record)
