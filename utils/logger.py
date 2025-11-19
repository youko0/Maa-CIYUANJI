# -*- coding: utf-8 -*-

"""
日志模块
提供统一的日志配置和管理功能
"""

import os
import sys
import logging
import logging.handlers
import traceback
from pathlib import Path

from core.constants.constants import LOG_LEVEL

# 全局日志记录器实例
_logger_instance = None


def _setup_logger():
    """
    配置并返回应用程序的主日志记录器
    
    Returns:
        logging.Logger: 配置好的日志记录器实例
    """
    # 确保日志目录存在
    log_dir = Path('log')
    log_dir.mkdir(exist_ok=True)

    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    # 使用TimedRotatingFileHandler实现按日期轮转
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / 'app.log',
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # 创建日志记录器
    logger = logging.getLogger(__name__)
    
    # 设置日志级别
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.DEBUG)
    logger.setLevel(log_level)
    
    logger.addHandler(file_handler)

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    global _logger_instance
    _logger_instance = logger
    return logger


def get_logger():
    """
    获取全局日志记录器实例

    Returns:
        Logger: 全局日志记录器实例
    """
    # 如果_logger_instance为None，自动调用setup_logger()
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = _setup_logger()
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