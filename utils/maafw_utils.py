# -*- coding: utf-8 -*-

"""
maafw工具模块
该模块包含游戏中maafw的工具函数，与游戏逻辑无关的方法
"""
import random
import time
import logging
from typing import List, Tuple, Union, Optional
import numpy as np


def random_point_in_scale_box(tasker, box: Tuple[int, int, int, int]) -> Tuple[int, int]:
    """
    在给定的边界框中生成一个随机坐标点

    Args:
        tasker
        box (tuple): 边界框 (x, y, w, h)

    Returns:
        tuple: 随机坐标点 (x, y)
    """
    x, y, w, h = box

    # 在边界框内生成随机坐标
    random_x = random.randint(x, x + w)
    random_y = random.randint(y, y + h)

    return (random_x, random_y)


def find_element_by_swipe(tasker,
                          swipe_start_point: List[int],
                          swipe_end_point: List[int],
                          target_pipeline: str,
                          pipeline_override=None,
                          swipe_num: int = 1,
                          swipe_pause: float = 0.1,
                          swipe_duration=200,
                          touch_pause: float = 0.1,
                          is_start_swipe_to_boundary=True):
    """
    通过滑动查找目标元素，采用优化策略：
    1. 首先检查目标是否已经存在，避免不必要的滑动
    2. 如果没有找到目标对象，先向一个方向滑动到底，然后再反向滑动查找
    
    Args:
        tasker: MaaFramework
        swipe_start_point (list): 滑动起始点坐标，格式为[x, y]
        swipe_end_point (list): 滑动终点点坐标，格式为[x, y]
        target_pipeline (str): 目标元素的识别pipeline名称
        pipeline_override:
        swipe_num (int): 滑动次数，默认为1次。既从可滑动区域一端滑动到另一端最大滑动次数
        swipe_pause (float): 每次滑动后的暂停时间（秒），默认为0.1秒
        swipe_duration:      滑动持续时间，单位毫秒。可选，默认 200
        touch_pause (float): 点击目标元素后的暂停时间（秒），默认为1秒
        is_start_swipe_to_boundary: 是否需要先按参数反方向滑动到边界

    Returns:
        若找到目标则返回True
    """
    if pipeline_override is None:
        pipeline_override = {}
    # 首先检查目标是否已经存在（不需要滑动）
    result = tasker.post_task(target_pipeline, pipeline_override).wait()
    if result.succeeded:
        return True

    # 先按参数反方向滑动到边界
    if is_start_swipe_to_boundary:
        tasker.controller.post_swipe(
            swipe_end_point[0],
            swipe_end_point[1],
            swipe_start_point[0],
            swipe_start_point[1],
            200
        ).wait()
        time.sleep(swipe_pause)

    # 反方向滑动查找
    for i in range(swipe_num):
        # 查找目标元素
        result = tasker.post_task(target_pipeline, pipeline_override).wait()
        if result.succeeded:
            return True

        # 滑动屏幕
        if i < swipe_num - 1:  # 最后一次不需要滑动
            # 滑动至下一页
            swipe_pipeline_override = {"swipe": {"begin": [*swipe_start_point, 1, 1],
                                                 "end": [[*swipe_end_point, 1, 1],
                                                         [*calculate_perpendicular_point(swipe_start_point, swipe_end_point), 1, 1]],
                                                 "duration": 1500}}
            tasker.post_task("swipe", swipe_pipeline_override).wait()
            time.sleep(swipe_pause)

    # 如果达到最大尝试次数仍未找到目标元素，则提示并返回False
    return False


import math


def calculate_perpendicular_point(swipe_start_point, swipe_end_point, distance=50):
    """
    计算从 swipe_end_point 出发，垂直于 swipe_start_point->swipe_end_point 向量的一个点

    Args:
        swipe_start_point: 起始点 (x, y)
        swipe_end_point: 结束点 (x, y)
        distance: 垂直距离，默认为100

    Returns:
        垂直方向上的一个点 (x, y)
    """
    # 计算向量
    dx = swipe_end_point[0] - swipe_start_point[0]
    dy = swipe_end_point[1] - swipe_start_point[1]

    # 计算垂直向量（旋转90度）
    # 有两种可能的垂直方向：(-dy, dx) 和 (dy, -dx)
    # 这里我们选择 (-dy, dx) 作为垂直向量
    perpendicular_dx = -dy
    perpendicular_dy = dx

    # 归一化垂直向量
    length = math.sqrt(perpendicular_dx ** 2 + perpendicular_dy ** 2)
    if length > 0:
        unit_perpendicular_dx = perpendicular_dx / length
        unit_perpendicular_dy = perpendicular_dy / length

        # 计算垂直方向上的点
        perpendicular_point = (
            swipe_end_point[0] + unit_perpendicular_dx * distance,
            swipe_end_point[1] + unit_perpendicular_dy * distance
        )

        return perpendicular_point

    return swipe_end_point


def swipe_and_ocr(tasker,
                  swipe_start_point: List[int],
                  swipe_end_point: List[int],
                  target_pipeline: str,
                  pipeline_override=None,
                  swipe_num: int = 1,
                  swipe_pause: float = 0.1,
                  swipe_duration=200,
                  touch_pause: float = 0.1, ):
    """
    滑动并识别屏幕内容，采用优化策略：
    1. 首先检查目标是否已经存在，避免不必要的滑动
    2. 如果没有找到目标对象，先向一个方向滑动到底，然后再反向滑动查找

    Args:
        tasker: MaaFramework
        swipe_start_point (list): 滑动起始点坐标，格式为[x, y]
        swipe_end_point (list): 滑动终点点坐标，格式为[x, y]
        target_pipeline (str): 目标元素的识别pipeline名称
        pipeline_override:
        swipe_num (int): 滑动次数，默认为1次。既从可滑动区域一端滑动到另一端最大滑动次数
        swipe_pause (float): 每次滑动后的暂停时间（秒），默认为0.1秒
        swipe_duration:      滑动持续时间，单位毫秒。可选，默认 200
        touch_pause (float): 点击目标元素后的暂停时间（秒），默认为1秒
        is_start_swipe_to_boundary: 是否需要先按参数反方向滑动到边界

    Returns:
        若找到目标则返回True
    """
    pass
