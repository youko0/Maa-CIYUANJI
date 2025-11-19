# -*- coding: utf-8 -*-
"""
设备任务线程
仿照helper-wjdr-python的线程设计，每个设备独立运行任务线程
避免多设备之间的任务阻塞
"""

import logging
import threading
from typing import Optional, Callable

from maa.tasker import Tasker
from modules.device_task_runner import DeviceTaskRunner


class DeviceTaskThreadManager:
    """
    设备任务管理器
    管理多个设备的任务线程
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.device_threads: dict[str, DeviceTaskRunner] = {}

    def start_device_task(self, device_serial: str, tasker: Tasker, task_name: str) -> Optional[DeviceTaskRunner]:
        """
        启动设备任务线程
        
        Args:
            device_serial: 设备序列号
            tasker: MaaFramework tasker实例
            task_name: 任务名称：(signIn、initialized、ocrBalance、ocrNovel)
            
        Returns:
            创建的任务线程实例（用于连接信号），失败时返回None
        """
        try:
            # 检查是否已有线程在运行
            if device_serial in self.device_threads:
                existing_thread = self.device_threads[device_serial]
                if existing_thread.is_running():
                    self.logger.warning(f"设备 {device_serial} 的任务线程已在运行")
                    return existing_thread
                else:
                    # 清理已停止的线程
                    self._cleanup_thread(device_serial)

            # 创建新的任务线程
            runner = DeviceTaskRunner(device_serial, tasker, task_name)

            thread = threading.Thread(target=runner.run)
            thread.daemon = True  # 设置为守护线程（主程序退出时会自动终止守护线程）
            thread.start()

            self.device_threads[device_serial] = runner

            self.logger.info(f"设备 {device_serial} 任务线程启动成功")
            return runner

        except Exception as e:
            self.logger.error(f"启动设备 {device_serial} 任务线程失败: {e}", True)
            return None

    def stop_device_task(self, device_serial: str, stop_type) -> bool:
        """
        停止设备任务线程
        
        Args:
            device_serial: 设备序列号
            stop_type: 停止类型（stop 停止任务执行、close_tab 关闭设备tab、close_app 关闭应用）
            
        Returns:
            是否停止成功
        """
        try:
            if device_serial not in self.device_threads:
                self.logger.warning(f"设备 {device_serial} 没有运行的任务线程")
                return False

            thread = self.device_threads[device_serial]

            # 停止线程
            thread.stop()

            wait_time = None

            if stop_type == "close_app":
                # 关闭应用时，最多等待30秒
                wait_time = 1

            # 等待停止完成
            if thread.wait_stopped(wait_time):
                self.logger.info(f"设备 {device_serial} 任务线程已停止")
            else:
                self.logger.warning(f"设备 {device_serial} 任务线程停止超时，尝试强制关闭")

            return True
        except Exception as e:
            self.logger.error(f"停止设备 {device_serial} 任务线程失败: {e}")
            return False
        finally:
            # 清理线程
            self._cleanup_thread(device_serial)

    def get_running_devices(self) -> list[str]:
        """获取正在运行任务的设备列表"""
        running_devices = []
        for device_serial, thread in self.device_threads.items():
            if thread.is_running():
                running_devices.append(device_serial)
        return running_devices

    def is_device_running(self, device_serial: str) -> bool:
        """检查指定设备是否正在运行任务"""
        if device_serial in self.device_threads:
            return self.device_threads[device_serial].is_running()
        return False

    def _cleanup_thread(self, device_serial: str):
        """清理线程"""
        if device_serial in self.device_threads:
            thread = self.device_threads[device_serial]
            thread.deleteLater()
            del self.device_threads[device_serial]



# 全局设备任务管理器实例
_DEVICE_TASK_THREAD_MANAGER = None

def get_device_task_thread_manager():
    """获取全局设备任务管理器实例"""
    global _DEVICE_TASK_THREAD_MANAGER
    if _DEVICE_TASK_THREAD_MANAGER is None:
        _DEVICE_TASK_THREAD_MANAGER = DeviceTaskThreadManager()
    return _DEVICE_TASK_THREAD_MANAGER
