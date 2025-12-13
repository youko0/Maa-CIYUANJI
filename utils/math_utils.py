# -*- coding: utf-8 -*-
"""
数学工具类
包含常用的数学计算和数值处理方法
"""

import re
from typing import Union


class MathUtils:
    """
    数学工具类
    提供各种数学计算和数值处理的静态方法
    """

    @staticmethod
    def is_int_string(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def format_number_with_separators(number: Union[int, str], separator: str = ",") -> str:
        """
        使用三位分节法格式化数字
        
        Args:
            number: 需要格式化的数字，可以是整数或数字字符串
            separator: 分节符，默认为逗号","
            
        Returns:
            str: 格式化后的数字字符串
            
        Examples:
            >>> MathUtils.format_number_with_separators(1234567)
            '1,234,567'
            >>> MathUtils.format_number_with_separators(1234567, " ")
            '1 234 567'
            >>> MathUtils.format_number_with_separators("12345678", "'")
            "12'345'678"
        """
        # 将输入转换为字符串并移除可能存在的空格
        num_str = str(number).strip()

        # 检查是否为有效的数字
        if not re.match(r'^-?\d+$', num_str):
            raise ValueError("输入必须是有效的整数")

        # 处理负数
        is_negative = num_str.startswith("-")
        if is_negative:
            num_str = num_str[1:]

        # 执行三位分节
        # 从右到左每3位插入分节符
        parts = []
        for i in range(len(num_str), 0, -3):
            start = max(0, i - 3)
            parts.append(num_str[start:i])

        formatted = separator.join(reversed(parts))

        # 如果是负数，添加负号
        if is_negative:
            formatted = "-" + formatted

        return formatted

    @staticmethod
    def format_chinese_number(number: Union[int, str]) -> str:
        """
        将数字转换为中文三位分节法格式（支持万、亿单位）
        支持参数3或4的分节方式
        
        Args:
            number: 需要格式化的数字，可以是整数或数字字符串
            
        Returns:
            str: 中文格式化后的数字字符串
            
        Examples:
            >>> MathUtils.format_chinese_number(1234567)
            '123万4567'
            >>> MathUtils.format_chinese_number(12345678)
            '1234万5678'
            >>> MathUtils.format_chinese_number(123456789)
            '1亿2345万6789'
        """
        # 将输入转换为字符串并移除可能存在的空格
        num_str = str(number).strip()

        # 检查是否为有效的数字
        if not re.match(r'^-?\d+$', num_str):
            raise ValueError("输入必须是有效的整数")

        # 处理负数
        is_negative = num_str.startswith("-")
        if is_negative:
            num_str = num_str[1:]

        length = len(num_str)
        result = ""

        if length <= 4:
            # 4位及以下直接返回
            result = num_str
        elif length <= 8:
            # 5-8位分为万级和个级
            ten_thousand_part = num_str[:-4]
            unit_part = num_str[-4:]
            # 移除万级前面的零
            ten_thousand_part = ten_thousand_part.lstrip('0')
            result = f"{ten_thousand_part}万{unit_part}" if ten_thousand_part else unit_part
        else:
            # 9位及以上分为亿级、万级和个级
            billion_part = num_str[:-8]
            ten_thousand_part = num_str[-8:-4]
            unit_part = num_str[-4:]

            # 处理亿级部分
            if int(billion_part) > 0:
                # 有亿级
                if int(ten_thousand_part) > 0:
                    # 有万级
                    result = f"{billion_part}亿{ten_thousand_part}万{unit_part}"
                else:
                    # 无万级
                    result = f"{billion_part}亿{unit_part}"
            else:
                # 无亿级
                if int(ten_thousand_part) > 0:
                    # 有万级
                    result = f"{ten_thousand_part}万{unit_part}"
                else:
                    # 无万级，直接返回个级
                    result = unit_part

        # 如果是负数，添加负号
        if is_negative:
            result = "-" + result

        return result

    @staticmethod
    def is_valid_thousands_separator_format(formatted_number: str, separator: str = ",") -> bool:
        """
        校验字符串是否符合三位分节法格式
        
        Args:
            formatted_number: 待校验的格式化数字字符串
            separator: 分节符，默认为逗号","
            
        Returns:
            bool: 符合规范返回True，否则返回False
            
        Examples:
            >>> MathUtils.is_valid_thousands_separator_format("1,234,567")
            True
            >>> MathUtils.is_valid_thousands_separator_format("1234,567")
            False
            >>> MathUtils.is_valid_thousands_separator_format("1,24,567")
            False
            >>> MathUtils.is_valid_thousands_separator_format("123")
            True
            >>> MathUtils.is_valid_thousands_separator_format("0")
            True
        """
        if not formatted_number:
            return False

        # 检查是否只包含数字和分节符
        valid_chars = set(separator + "0123456789")
        if not all(c in valid_chars for c in formatted_number):
            return False

        # 处理负数
        if formatted_number.startswith("-"):
            number_part = formatted_number[1:]
        else:
            number_part = formatted_number

        # 按分节符分割
        parts = number_part.split(separator)

        # 如果没有分节符，只要是纯数字就合法
        if len(parts) == 1:
            return parts[0].isdigit()

        # 第一部分（最高位）可以是1-3位数字
        if not parts[0].isdigit() or len(parts[0]) == 0 or len(parts[0]) > 3:
            return False

        # 第一部分不能以0开头，除非整个数字就是0
        if len(parts[0]) > 1 and parts[0][0] == '0':
            return False

        # 其余部分必须是3位数字
        for part in parts[1:]:
            if len(part) != 3 or not part.isdigit():
                return False

        return True

    @staticmethod
    def pad_zero(number: int, length: int) -> str:
        """
        将数字填充为指定长度的字符串，不足的位数用0填充

        Args:
            number: 需要填充的数字
            length: 填充后的长度

        Returns:
            str: 填充后的字符串

        Examples:
            >>> MathUtils.pad_zero(123, 5)
            '00123'
            >>> MathUtils.pad_zero(123, 3)
            '123'
        """
        return str(number).zfill(length)
