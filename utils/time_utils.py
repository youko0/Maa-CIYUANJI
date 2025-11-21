# -*- coding: utf-8 -*-
"""
时间工具模块
提供时间格式解析和计算功能
"""

import re
from datetime import datetime, timedelta
from random import randint


class TimeUtils:
    """
    时间工具类
    提供时间格式解析和计算功能，支持如"00:02:31"、"1天 22:16:44"等格式
    """

    @staticmethod
    def current_time():
        return datetime.now()

    @staticmethod
    def format(dt: datetime | None, format_str: str = "%Y-%m-%d %H:%M:%S", empty_msg="") -> str:
        """
        格式化datetime对象为字符串
        
        Args:
            dt (datetime): datetime对象
            format_str
            empty_msg
            
        Returns:
            str: 格式化后的时间字符串，格式为"YYYY-MM-DD HH:MM:SS"
        """
        if not dt:
            return empty_msg
        # 如果dt为list，则取最小
        dt = min(dt) if isinstance(dt, list) else dt
        return dt.strftime(format_str)

    @staticmethod
    def strptime(time_str: str, format_str: str = "%Y-%m-%d %H:%M:%S"):
        """
        将字符串转换为datetime对象

        Args:
            time_str (str): 时间字符串，格式为"YYYY-MM-DD HH:MM:SS"
            format_str

        Returns:
            datetime: 转换后的datetime对象
        """
        if not time_str:
            return None
        return datetime.strptime(time_str, format_str)

    # 判断参数时间是否为今天
    @staticmethod
    def is_today(dt: datetime):
        """
        判断参数时间是否为今天

        Args:
            dt (datetime): 时间参数

        Returns:
            bool: True表示为今天，False表示不是今天
        """
        return dt.date() == datetime.now().date()


# 使用示例
if __name__ == "__main__":
    pass
