#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志工具模块
提供统一的日志记录功能，支持日志轮转
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path


# 全局日志记录器
_logger = None


def setup_logger():
    """设置全局日志记录器"""
    global _logger
    
    if _logger is not None:
        return _logger
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger("maa_ciyuanji")
    logger.setLevel(logging.DEBUG)
    
    # 创建文件处理器（按天轮转）
    log_file = log_dir / "app.log"
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    _logger = logger
    return logger


def get_logger(name: str):
    """获取指定名称的日志记录器"""
    if _logger is None:
        setup_logger()
    
    return logging.getLogger(f"maa_ciyuanji.{name}")


def get_device_logger(device_address: str):
    """获取设备专用日志记录器"""
    # 创建设备日志目录
    device_log_dir = Path("logs") / device_address
    device_log_dir.mkdir(exist_ok=True)
    
    # 创建设备日志记录器
    logger = logging.getLogger(f"maa_ciyuanji.device.{device_address}")
    logger.setLevel(logging.DEBUG)
    
    # 检查是否已经有处理器
    if logger.handlers:
        return logger
    
    # 创建文件处理器（按天轮转）
    log_file = device_log_dir / "device.log"
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    
    return logger