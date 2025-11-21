#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
随机工具类
提供各种随机数生成和随机选择功能
"""

import random
from typing import Tuple, List, Optional


class RandomUtils:
    """
    随机工具类，提供各种随机相关的功能
    """


    @staticmethod
    def random_coordinates_in_box(area: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """
        在指定矩形内生成随机坐标点

        Args:
            area (tuple): 区域坐标 (x1, y1, width, height)，其中(x1, y1)是左上角坐标，(width, height)是右下角坐标

        Returns:
            tuple: 随机坐标点 (x, y)

        Example:
            >>> RandomUtils.random_coordinates_in_area((100, 100, 50, 50))
            (133, 125)
        """
        x1, y1, width, height = area
        x2 = x1 + width
        y2 = y1 + height

        # 生成随机坐标点
        x = random.randint(x1, x2)
        y = random.randint(y1, y2)

        return x, y
