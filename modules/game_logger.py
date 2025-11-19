# -*- coding: utf-8 -*-
"""
游戏逻辑日志管理模块
提供专门用于游戏逻辑的日志记录功能，支持将日志保存到指定设备序列号的文件夹中
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal

from utils.logger import get_logger
import traceback

# 获取日志记录器实例
app_logger = get_logger()


class GameLogger(QObject):
    """
    游戏逻辑日志管理器
    提供统一的日志记录接口，支持UI信号和文件日志输出
    """

    # 日志信号，用于向UI发送日志消息
    log_message = Signal(str)

    def __init__(self, serial_number=None):
        """
        初始化游戏逻辑日志管理器
        
        Args:
            serial_number (str): 设备序列号，用于创建日志文件夹
        """
        super().__init__()

        self.serial_number = serial_number or "unknown_device"

        # 处理设备序列号中的特殊字符，避免在Windows上创建文件夹时出错
        safe_device_serial = self.serial_number.replace(":", "_")

        # 创建以序列号命名的日志目录
        log_dir = Path('log') / safe_device_serial
        log_dir.mkdir(parents=True, exist_ok=True)

        # 配置日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 创建游戏逻辑日志文件处理器，使用TimedRotatingFileHandler实现按日期轮转
        game_logic_log_filename = log_dir / 'game_logic.log'
        self.file_handler = logging.handlers.TimedRotatingFileHandler(
            game_logic_log_filename,
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        self.file_handler.setFormatter(formatter)

        # 创建日志记录器
        self.logger = logging.getLogger(f"GameLogic_{self.serial_number}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.file_handler)

        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _format_message(self, level, message):
        """
        格式化日志消息
        
        Args:
            level (str): 日志级别
            message (str): 日志消息
            
        Returns:
            str: 格式化后的日志消息
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"{timestamp} [{level}] {message}"

    def debug(self, message):
        """
        记录DEBUG级别日志
        
        Args:
            message (str): 日志消息
        """
        formatted_message = self._format_message("DEBUG", message)
        self.log_message.emit(formatted_message)
        self.logger.debug(message)

    def info(self, message):
        """
        记录INFO级别日志
        
        Args:
            message (str): 日志消息
        """
        formatted_message = self._format_message("INFO", message)
        self.log_message.emit(formatted_message)
        self.logger.info(message)

    def warning(self, message):
        """
        记录WARNING级别日志
        
        Args:
            message (str): 日志消息
        """
        formatted_message = self._format_message("WARNING", message)
        self.log_message.emit(formatted_message)
        self.logger.warning(message)

    def error(self, message, show_traceback=False):
        """
        记录ERROR级别日志
        
        Args:
            message (str): 日志消息
            show_traceback: 是否显示错误详情
        """
        formatted_message = self._format_message("ERROR", message)
        self.log_message.emit(formatted_message)
        self.logger.error(message)
        if show_traceback:
            app_logger.error(f'详细错误信息： {traceback.format_exc()}')

    def critical(self, message):
        """
        记录CRITICAL级别日志
        
        Args:
            message (str): 日志消息
        """
        formatted_message = self._format_message("CRITICAL", message)
        self.log_message.emit(formatted_message)
        self.logger.critical(message)


class GameLoggerFactory:
    """
    游戏日志记录器工厂类
    管理GameLogger实例，确保每个设备序列号只有一个实例，避免信号重复连接
    """

    _loggers = {}

    @classmethod
    def get_logger(cls, serial_number, log_message=None):
        """
        获取GameLogger实例
        
        Args:
            serial_number (str): 设备序列号，必填项
            log_message (Signal): 连接日志信号到传入的日志处理函数
            
        Returns:
            GameLogger: GameLogger实例
        """
        if serial_number is None:
            raise ValueError("参数设备序列号异常为空")
        if serial_number not in cls._loggers:
            logger = GameLogger(serial_number)
            if log_message:
                logger.log_message.connect(log_message)
            cls._loggers[serial_number] = logger
        return cls._loggers[serial_number]

    @classmethod
    def remove_logger(cls, serial_number):
        """
        移除指定的logger实例
        
        Args:
            serial_number (str): 设备序列号
        """
        if serial_number in cls._loggers:
            # 关闭文件处理器
            logger_instance = cls._loggers[serial_number]
            logger_instance.file_handler.close()
            logger_instance.logger.removeHandler(logger_instance.file_handler)
            del cls._loggers[serial_number]