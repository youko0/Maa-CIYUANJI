# -*- coding: utf-8 -*-
"""
设备任务线程
仿照helper-wjdr-python的线程设计，每个设备独立运行任务线程
避免多设备之间的任务阻塞
"""

import math
import threading
import time
from typing import Optional, Callable
from datetime import datetime, timedelta
from PySide6.QtCore import QThread, Signal, QObject

from maa.tasker import Tasker

from modules.game_logger import GameLoggerFactory
from modules.page_manager import PageManager
from modules.user_logic import UserLogic


class DeviceTaskRunner(QObject):
    """
    设备任务线程类
    仿照helper-wjdr-python的GameLogicThread设计
    每个设备独立运行自己的任务线程
    """

    # 定义信号
    # log_message = Signal(str)  # 日志消息
    task_completed = Signal(str, str)  # device_serial, task_name
    user_data_updated = Signal(str, object)  # device_serial, user_data
    execution_stopped = Signal(str)  # device_serial

    def __init__(self, device_serial: str, task_name=""):
        super().__init__()
        self.device_serial = device_serial
        self.task_name = task_name  # 任务名称：(signIn、initialized、ocrBalance、ocrNovel)
        self.logger = GameLoggerFactory.get_logger(device_serial)
        self._running = True
        self._sleep_interrupted = False  # 添加中断休眠标志

        self.stop_event = threading.Event()  # 停止任务事件。线程事件对象，用于线程间通信
        self.stopped_event = threading.Event()  # 线程已完全停止事件。线程事件对象，用于线程间通信
        self.stopped_event.set()  # 初始状态为已停止

        # 页面管理器
        self.page_manager = PageManager(self.device_serial, self._on_execution_stopped)
        self.user_logic = UserLogic(self.device_serial, self.user_data_updated)
        
        # 线程结束回调
        self._on_finished_callback = None

    def set_on_finished_callback(self, callback):
        """设置线程结束时的回调函数"""
        self._on_finished_callback = callback

    def run(self):
        """
        线程主执行函数
        """
        # 标记线程开始运行
        self.stopped_event.clear()
        try:
            self.logger.info(f"设备 {self.device_serial} 任务线程启动")

            # 执行游戏逻辑循环
            try:
                if not self.stop_event.is_set():
                    if self.task_name == "signIn":
                        self.logger.info(f"[系统]开始执行签到任务")
                        self.page_manager.check_is_home_page()
                        self.user_logic.sign_in()
                    elif self.task_name == "refreshBalance":
                        self.logger.info(f"[系统]开始执行刷新余额任务")
                        self.page_manager.check_is_home_page()
                        self.user_logic.refresh_balance()
                if self.stop_event.is_set():
                    return


            except Exception as e:
                self.logger.error(f"执行游戏逻辑时出错： {str(e)}", True)
                # 出错后休眠一段时间再重试
                self._interruptible_sleep(10)

        except Exception as e:
            error_msg = f"任务线程异常: {str(e)}"
            self.logger.error(error_msg)
        finally:
            self.stopped_event.set()  # 标记已停止
            self.logger.info(f"设备 {self.device_serial} 任务线程结束")
            # 调用结束回调
            if self._on_finished_callback:
                self._on_finished_callback(self.device_serial)

    def game_main(self):
        """        游戏主逻辑（按照固定顺序检查并执行各项任务）        """
        if self.stop_event.is_set():
            return

    def _interruptible_sleep(self, seconds: int):
        """
        可中断的休眠

        Args:
            seconds: 休眠秒数
        """
        if seconds > 0:
            self.logger.info(f'[系统]无紧急任务，休眠{seconds}秒')
            for _ in range(seconds):
                if not self._running or self._sleep_interrupted:
                    if self._sleep_interrupted:
                        self.logger.info('[系统]休眠被用户中断，立即执行任务')
                        self._sleep_interrupted = False  # 重置中断标志
                    break
                time.sleep(1)

    def interrupt_sleep(self):
        """中断当前休眠，用于立即执行任务"""
        self._sleep_interrupted = True
        self.logger.info('[系统]收到立即执行请求，准备中断休眠')

    def _emit_log_message(self, message: str):
        """发送日志消息"""
        # self.log_message.emit(message)
        pass

    def _emit_user_data_update(self, device_serial: str):
        """发送用户信息更新信号"""
        self.user_data_updated.emit(device_serial)

    def _emit_task_completed(self, device_serial: str, task_name: str):
        """发送任务完成信号"""
        self.task_completed.emit(device_serial, task_name)

    def _on_execution_stopped(self, device_serial: str):
        """处理执行停止信号"""
        self.execution_stopped.emit(device_serial)

    def stop(self):
        """停止线程"""
        self._running = False
        self.stop_event.set()
        
    def is_running(self) -> bool:
        """检查线程是否正在运行"""
        return self._running and not self.stopped_event.is_set()

    def wait_stopped(self, timeout=None):
        """等待 runner 完全停止"""
        self.logger.info(f"等待当前任务结束...")
        return self.stopped_event.wait(timeout)
