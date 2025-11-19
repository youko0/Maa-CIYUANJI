# -*- coding: utf-8 -*-
"""
行军队列信息处理模块

该模块用于解析和处理游戏中行军队列的OCR识别结果，
包括资源采集、行军和战斗等不同类型的信息。
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class DeviceInfo:
    """
    设备信息类
    
    Attributes:
        device_serial (str): 设备序列号，设备唯一标识
    """

    # 设备序列号，设备唯一标识
    device_serial: str
    name: str
    # 余额
    balance: int = 0
    # 上次签到时间
    last_sign_in_time: datetime = None
    # 是否已做识别初始化处理
    is_initialized: bool = False

    def __init__(self, device_serial):
        self.device_serial = device_serial
        self.name = "设备" + device_serial

    @staticmethod
    def _classify_mine(text: str) -> tuple[Optional[str], Optional[str]]:
        pass


# 使用示例
if __name__ == "__main__":
    # 设置编码以正确显示中文
    pass
