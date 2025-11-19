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

from modules.game_logger import GameLoggerFactory
from utils.time_utils import TimeUtils


class UserLogic:
    """
    用户信息相关的游戏逻辑
    包含用户信息识别和动作
    """

    def __init__(self, device_serial, tasker, page_manager, user_data_updated):
        self.device_serial = device_serial
        self.tasker = tasker
        self.page_manager = page_manager
        self.logger = GameLoggerFactory.get_logger(device_serial)
        self.user_data_updated = user_data_updated

    def sign_in(self, is_user_data_updated=False):
        """签到"""

        result_succeeded = self.tasker.post_task("existsAndClickUser").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[签到]没有识别到用户页")
            return False

        time.sleep(0.5)
        # 进入签到任务页面
        result_succeeded = self.tasker.post_task("existsAndClickSignInEntrance").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[签到]没有识别到签到入口按钮，判断是否存在青少年模式提示")
            # 判断是否出现了青少年模拟提示
            result_succeeded = self.tasker.post_task("existsTeenModeTips").wait().succeeded
            if result_succeeded is False:
                self.logger.error(f"[签到]没有出现青少年模式提示，任务结束")
                return False
            else:
                # 点击我知道了
                self.tasker.post_task("existsAndClickISeeBtn").wait()
                time.sleep(0.3)
                result_succeeded = self.tasker.post_task("existsAndClickSignInEntrance").wait().succeeded
                if result_succeeded is False:
                    self.logger.error(f"[签到]没有识别到签到入口按钮，任务结束")
                    return False

        # 等待页面加载结束（判断是否成功进入签到成功页面）
        result_succeeded = self.tasker.post_task("existsRulesDescription").wait().succeeded
        if result_succeeded is False:
            self.logger.error(f"[签到]没有正常进入签到成功页面")
            return False

        self.logger.info(f"[签到]成功进入签到成功页面")
        # 判断是否存在签到成功提示
        if self.tasker.post_task("existsSignInSuccessTip").wait().succeeded:
            self.logger.info('签到成功，识别代币数量')
            result = self.tasker.post_task("ocrSignInCoinNum").wait().get()
            if result and result.nodes and len(result.nodes) > 0:
                coin_num_str = result.nodes[0].recognition.best_result.text
                # 添加代币（模拟签到获得5个代币）
                expire_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                # self.config_manager.add_coin(self.device_serial, int(coin_num_str), expire_time)
                print(f"{self.device_serial}设备签到成功，添加代币：{coin_num_str}，过期时间：{expire_time}")
                # 更新设备信息及余额数据

            else:
                self.logger.error(f"{self.device_serial}设备没有识别到代币数量")
        else:
            # 签到失败
            self.logger.error(f"[签到]设备已签到")

        # 调用返回按钮
        self.tasker.post_task("androidBack").wait()
