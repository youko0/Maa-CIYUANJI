# -*- coding: utf-8 -*-
"""
用户信息相关的游戏逻辑
包含用户信息识别和动作
"""
import re
import time
from datetime import datetime, timedelta
from typing import List

from maa.define import TaskDetail, OCRResult

from core.balance_manager import BalanceInfo
from core.maa_manager import get_maa_manager
from modules.game_logger import GameLoggerFactory
from utils.random_utils import RandomUtils
from utils.time_utils import TimeUtils


class NovelLogic:
    """
    用户信息相关的游戏逻辑
    包含用户信息识别和动作
    """

    def __init__(self, device_serial):
        self.device_serial = device_serial
        self.maa_manager = get_maa_manager()
        self.tasker = self.maa_manager.get_device_tasker(device_serial)
        self.logger = GameLoggerFactory.get_logger(device_serial)

    def initialized(self):
        """初始化"""
        result_succeeded = self.tasker.post_task("existAndClickBookshelf").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别初始化]没有识别到书架页")
            return False
        time.sleep(0.6)
        # 点击第一本小说
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((49, 393, 149, 166))).wait()
        time.sleep(0.8)
        # 点击一个中间安全的位置，调出设置按钮
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((242, 500, 237, 370))).wait()
        time.sleep(0.6)
        # 判断是否存在设置按钮
        result_succeeded = self.tasker.post_task("existAndClickSettingsBtn").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别初始化]没有识别到设置按钮")
            return False
        time.sleep(0.3)
        # 设置字体字为最小
        self.tasker.controller.post_swipe(231, 881, 33, 879, 700).wait()
        time.sleep(0.2)
        # 点击更多设置
        result_succeeded = self.tasker.post_task("existAndClickMoreSettingsBtn").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[小说识别初始化]没有识别到更多设置按钮")
            return False
        time.sleep(0.3)
        # 依次点击最窄、最窄、无、隐藏
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((50, 242, 80, 45))).wait()
        time.sleep(0.3)
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((50, 424, 80, 42))).wait()
        time.sleep(0.3)
        # self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((80,612,33,64))).wait()
        # time.sleep(0.3)
        self.tasker.controller.post_click(*RandomUtils.random_coordinates_in_box((52, 853, 84, 45))).wait()

        # 完成初始化
        self.maa_manager.initialized_complete(self.device_serial)

        # 调用返回按钮
        self.tasker.post_task("androidBack").wait()
        # 调用返回按钮
        self.tasker.post_task("androidBack").wait()
        self.logger.info(f"[小说识别初始化]初始化完成")
