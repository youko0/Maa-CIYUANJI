import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """日志管理类"""
    
    def __init__(self, name: str = "MaaCIYUANJI", log_file: str = "logs/app.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # 设置处理器格式化器
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器到日志器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录一般信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误信息"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误信息"""
        self.logger.critical(message)
    
    def log_novel_action(self, action: str, novel_name: str, details: Optional[str] = None):
        """记录小说相关操作"""
        message = f"小说操作 - {action}: {novel_name}"
        if details:
            message += f" ({details})"
        self.info(message)
    
    def log_device_action(self, action: str, device_id: str, details: Optional[str] = None):
        """记录设备相关操作"""
        message = f"设备操作 - {action}: {device_id}"
        if details:
            message += f" ({details})"
        self.info(message)
    
    def log_coin_action(self, action: str, amount: int, details: Optional[str] = None):
        """记录代币相关操作"""
        message = f"代币操作 - {action}: {amount}"
        if details:
            message += f" ({details})"
        self.info(message)


# 全局日志实例
app_logger = Logger()