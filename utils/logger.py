# -*- coding: utf-8 -*-

"""
日志模块
提供统一的日志配置和管理功能
"""

import sys
import logging
import logging.handlers
import traceback
from pathlib import Path
from typing import Optional, Any

from core.constants.constants import LOG_LEVEL


class QtLogHandler(logging.Handler):
    """Qt日志处理器，将日志消息转发到Qt信号"""
    
    def __init__(self, signal: Any):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        """发送日志记录"""
        try:
            msg = self.format(record)
            self.signal.emit(msg)
        except Exception:
            self.handleError(record)


# 全局日志记录器实例
_logger_instance = None


def _setup_logger(qt_signal=None):
    """
    配置并返回应用程序的主日志记录器
    
    Args:
        qt_signal: 可选的Qt信号，用于直接发送日志消息到UI
        
    Returns:
        logging.Logger: 配置好的日志记录器实例
    """
    # 确保日志目录存在
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    # 使用TimedRotatingFileHandler实现按日期轮转
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / 'app.log',
        when='midnight',
        interval=1,
        backupCount=30,  # 保留30天的日志
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # 创建日志记录器
    logger = logging.getLogger("MaaCIYUANJI")
    logger.setLevel(logging.DEBUG)

    # 清除现有的处理器（避免重复添加）
    logger.handlers.clear()

    # 添加文件处理器
    logger.addHandler(file_handler)

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
        
    # 如果提供了Qt信号，创建并添加Qt日志处理器
    if qt_signal is not None:
        qt_handler = QtLogHandler(qt_signal)
        qt_handler.setFormatter(formatter)
        logger.addHandler(qt_handler)

    return logger


def get_logger(qt_signal=None):
    """
    获取全局日志记录器实例

    Args:
        qt_signal: 可选的Qt信号，用于直接发送日志消息到UI

    Returns:
        Logger: 全局日志记录器实例
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = _setup_logger(qt_signal)
    elif qt_signal is not None:
        # 如果已经存在实例但传入了qt_signal，添加Qt处理器
        has_qt_handler = any(isinstance(handler, QtLogHandler) for handler in _logger_instance.handlers)
        if not has_qt_handler:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            qt_handler = QtLogHandler(qt_signal)
            qt_handler.setFormatter(formatter)
            _logger_instance.addHandler(qt_handler)
    return _logger_instance


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    全局异常处理函数
    
    Args:
        exc_type: 异常类型
        exc_value: 异常值
        exc_traceback: 异常追踪信息
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # 获取日志记录器
    logger = get_logger()

    # 记录异常信息到日志文件
    logger.error("未捕获的异常:", exc_info=(exc_type, exc_value, exc_traceback))

    # 同时将异常信息输出到控制台
    print("未捕获的异常:", file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)