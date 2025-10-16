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
from device_manager import device_manager, DeviceInfo
from logger import app_logger
from ui.home_tab import HomeTabWidget
from ui.novel_tab import NovelTabWidget
from ui.balance_tab import BalanceTabWidget
from ui.dialogs import AddNovelDialog, ConnectDeviceDialog
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


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.novel_processor = NovelProcessor(self.config_manager)
        self.device_manager = device_manager
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
        self.home_tab = HomeTabWidget(self)
        self.novel_tab = NovelTabWidget(self)
        self.balance_tab = BalanceTabWidget(self)
        
        self.tab_widget.addTab(self.home_tab, "主页")
        self.tab_widget.addTab(self.novel_tab, "小说")
        self.tab_widget.addTab(self.balance_tab, "余额")
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.tab_widget)
        
        # 隐藏小说Tab，只有在开始识别时才显示
        self.tab_widget.setTabEnabled(1, False)
    
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
        self.home_tab.refresh_novel_list()
    
    def refresh_device_list(self):
        """刷新设备列表"""
        self.home_tab.refresh_device_list()
    
    def update_balance_info(self):
        """更新余额信息"""
        self.balance_tab.update_balance_info()
    
    def detect_devices(self):
        """检测设备"""
        try:
            # 检测设备
            detected_devices = self.device_manager.detect_devices()
            self.device_manager.update_device_list(detected_devices)
            
            # 刷新显示
            self.refresh_device_list()
            
            app_logger.info(f"检测到 {len(detected_devices)} 个设备")
        except Exception as e:
            app_logger.error(f"检测设备失败: {e}")
            QMessageBox.critical(self, "错误", f"检测设备失败: {str(e)}")
    
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
        selected_rows = self.home_tab.novel_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的小说")
            return
        
        row = selected_rows[0].row()
        novel_item = self.home_tab.novel_table.item(row, 0)
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
        selected_rows = self.home_tab.novel_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要停用的小说")
            return
        
        row = selected_rows[0].row()
        status_item = self.home_tab.novel_table.item(row, 3)
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
        if self.home_tab.novel_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "请先添加小说")
            return
        
        # 检查是否选中了小说
        selected_rows = self.home_tab.novel_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要识别的小说")
            return
        
        # 切换到小说Tab
        self.tab_widget.setTabEnabled(1, True)
        self.tab_widget.setCurrentIndex(1)
        
        # 开始识别过程
        self.process_novel()
    
    def connect_device(self):
        """连接设备"""
        # 更新对话框中的设备管理器引用
        dialog = ConnectDeviceDialog(self, self.device_manager)
        
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            selected_device_addr = dialog.get_selected_device()
            if selected_device_addr:
                if self.device_manager.connect_device(selected_device_addr):
                    self.refresh_device_list()
                    # 查找设备名称用于日志
                    device = self.device_manager.get_device_by_address(selected_device_addr)
                    if device:
                        app_logger.log_device_action("连接设备", device.name)
    
    def _refresh_dialog_devices(self, dialog):
        """刷新对话框中的设备列表"""
        dialog.device_table.setRowCount(0)  # 清空表格
        
        # 检测设备
        detected_devices = self.device_manager.detect_devices()
        self.device_manager.update_device_list(detected_devices)
        
        # 显示所有设备
        dialog.device_table.setRowCount(len(self.device_manager.devices))
        for row, device in enumerate(self.device_manager.devices):
            dialog.device_table.setItem(row, 0, QTableWidgetItem(device.name))
            dialog.device_table.setItem(row, 1, QTableWidgetItem(device.address))
            dialog.device_table.setItem(row, 2, QTableWidgetItem(device.adb_path))
            status = "已连接" if device.connected else "未连接"
            status_item = QTableWidgetItem(status)
            dialog.device_table.setItem(row, 3, status_item)
            
            # 设置状态列字体颜色
            if device.connected:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            
            # 已连接的设备设置为不可选
            if device.connected:
                for col in range(4):
                    item = dialog.device_table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
    
    def disconnect_device(self):
        """断开设备"""
        # 获取选中的行
        selected_rows = self.home_tab.device_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要断开的设备")
            return
        
        disconnected_count = 0
        for index in selected_rows:
            row = index.row()
            # 安全地获取地址
            address_item = self.home_tab.device_table.item(row, 1)
            if not address_item:
                continue
            address = address_item.text()
            device = self.device_manager.get_device_by_address(address)
            if device and device.connected:
                if self.device_manager.disconnect_device(address):
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
                self.novel_tab.novel_log.append(f"[成功] 小说已导出到: {file_path}")
                QMessageBox.information(self, "成功", f"小说已导出到: {file_path}")
                app_logger.log_novel_action("导出成功", target_novel, f"导出路径: {file_path}")
            else:
                self.novel_tab.novel_log.append("[错误] 导出小说失败")
                QMessageBox.critical(self, "错误", "导出小说失败")
                app_logger.error("小说导出失败")
        except Exception as e:
            self.novel_tab.novel_log.append(f"[错误] 导出小说失败: {str(e)}")
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
        self.novel_tab.novel_log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 签到成功，获得5个代币")
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
        self.novel_tab.current_novel_label.setText(f"当前小说: {target_novel}")
        self.novel_tab.progress_label.setText("进度: 0/10")
        
        self.processor_thread = NovelProcessorThread(self.config_manager, self.novel_processor)
        self.processor_thread.progress_updated.connect(self.update_novel_progress)
        self.processor_thread.finished_signal.connect(self.novel_process_finished)
        
        self.novel_tab.stop_novel_btn.setEnabled(True)
        self.novel_tab.novel_log.append(f"[{self.get_current_time()}] 开始识别小说: {target_novel}")
        
        self.processor_thread.start()
    
    def stop_process(self):
        """停止处理"""
        if self.processor_thread and self.processor_thread.isRunning():
            self.processor_thread.stop()
            self.novel_tab.stop_novel_btn.setEnabled(False)
    
    def novel_process_finished(self, success, message):
        """小说处理完成"""
        self.novel_tab.stop_novel_btn.setEnabled(False)
        
        if success:
            self.novel_tab.novel_log.append(f"[{self.get_current_time()}] {message}")
            self.update_status(f"处理完成: {message}")
            app_logger.log_novel_action("处理完成", "当前小说", message)
        else:
            self.novel_tab.novel_log.append(f"[{self.get_current_time()}] 错误: {message}")
            self.update_status(f"处理失败: {message}")
            app_logger.error(f"小说处理失败: {message}")
    
    def update_novel_progress(self, message):
        """更新小说进度"""
        self.novel_tab.novel_log.append(f"[{self.get_current_time()}] {message}")
        self.novel_tab.progress_info.append(message)
        
        # 更新进度标签（模拟）
        if "处理进度:" in message:
            self.novel_tab.progress_label.setText(message)
        
        # 记录到日志文件
        app_logger.info(f"小说处理进度: {message}")
    
    def get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def update_status(self, message):
        """更新状态信息"""
        # 在新的UI中，状态信息显示在小说Tab的日志中
        self.novel_tab.novel_log.append(f"[状态] {message}")
    
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