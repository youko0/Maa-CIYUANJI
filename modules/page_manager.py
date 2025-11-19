# -*- coding: utf-8 -*-
"""
页面管理模块
简化的页面状态检查器，仅负责确认当前页面状态
参考MaaXuexi-master的简洁设计
"""

import logging
import time
from datetime import timedelta
from enum import Enum

from modules.game_logger import GameLoggerFactory


class PageType(Enum):
    """页面类型枚举"""
    HOME = "home"  # 主页（城镇或野外）
    TOWN = "town"  # 城镇内
    WILD = "wild"  # 野外
    ISLAND = "island"  # 海岛
    UNKNOWN = "unknown"  # 未知页面


class PageManager:
    """
    简化的页面管理器
    仅负责页面状态检查，不参与任务执行
    """

    def __init__(self, device_serial, tasker, error_callback=None):
        """
        :param device_serial:
        :param tasker:
        :param error_callback: 发生错误的回调，这里用来通知被调用方退出方法循环
        """
        self.device_serial = device_serial
        self.tasker = tasker
        self.error_callback = error_callback
        self.logger = GameLoggerFactory.get_logger(device_serial)

    def callback_caller(self, caller, is_reconnect=False):
        """
        回调调用方法
        :param caller:  被调用的方法
        :param is_reconnect:  是否尝试重连
        :return:
        """
        if caller is None:
            return
        if caller == "home":
            self.check_is_home_page(is_reconnect=is_reconnect)

    def reconnect(self, wait_time=300, max_attempts=3, caller=None):
        """
        重新连接应用（处理账号被顶号和网络断开的情况）

        当用户账号在其他设备上登录时，当前设备会被强制下线，此方法用于处理这种情况。
        如果检测到"重连按钮"，说明账号被顶号，等待指定时间后重新连接；
        如果未检测到重连按钮，则尝试重启应用应用。

        Args:
            wait_time (int): 账号被顶号后的等待时间（秒），默认为300秒（5分钟）
                            等待一段时间后再次尝试连接，避免频繁重连
            max_attempts (int): 最大尝试重新连接次数，默认为3次
            caller :调用方
        """

        self.logger.info('尝试重启应用')
        self.tasker.controller.post_stop_app("com.xunyou.rb").wait()
        self.logger.info('关闭应用，等待3秒...')
        time.sleep(3)
        self.logger.info('启动应用，等待8秒启动时间...')
        self.tasker.controller.post_start_app("com.xunyou.rb").wait()
        time.sleep(3)
        # 判断是否出现了用户协议和隐私条款
        result_succeeded = self.tasker.post_task("existAndClickAgreement").wait().succeeded
        if result_succeeded:
            self.logger.error(f"存在用户协议和隐私条款，点击同意并继续")
            time.sleep(0.2)
            self.tasker.post_task("existAndClickAgreeAndContinueBtn").wait()
        time.sleep(4)
        self.callback_caller(caller)

    def check_is_home_page(self, is_back_home=True, max_attempts=5, is_reconnect=True):
        """
        检查当前是否在应用主页，如果不是则尝试返回主页

        通过检测任务按钮来判断是否在主页（城镇和野外）。如果不在主页且is_back_home为True，
        则通过按下BACK键尝试返回主页，最多尝试max_attempts次。
        如果尝试max_attempts次后仍未回到主页，则认为可能被顶号，调用重连方法。

        特殊处理：如果检测到在海岛页面（通过海岛仓库按钮识别），则根据is_back_home参数决定是否
        尝试返回城镇/野外页面。

        Args:
            is_back_home (bool): 是否尝试返回主页，默认为True
                                如果为False，则不会尝试返回主页操作
            max_attempts (int): 最大尝试返回主页的次数，默认为5次
            is_reconnect (bool): 是否尝试重连，默认为True。添加该参数防止回调循环

        Returns:
            bool: 如果在主页返回True，如果尝试max_attempts次后仍未回到主页则调用重连方法
        """
        self.logger.info('[首页检查]检查是否在首页')
        for i in range(max_attempts):
            # 判断是否在城镇或野外
            result_succeeded = self.tasker.post_task("existBookshelf").wait().succeeded
            if result_succeeded:
                return True
            else:
                self.logger.debug("不在主页，调用返回按钮")
                self.tasker.post_task("androidBack").wait()
                time.sleep(0.2)

        if is_reconnect:
            self.logger.debug(f"尝试{max_attempts}次后仍未回到主页，尝试重启应用")
            # 若循环五次后还没有返回主页，则判断是否被顶号了
            self.reconnect()
        else:
            self.logger.debug(f"尝试{max_attempts}次后仍未回到主页，停止继续检测，请检测设备")
            # 停止任务循环
            if self.error_callback is not None:
                self.error_callback()
            return False
