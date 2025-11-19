# -*- coding: utf-8 -*-
"""
MaaFramework设备管理器
用于替代原有的Airtest设备连接逻辑，实现设备隔离、任务调度和用户信息管理
"""

import logging
import datetime
import json
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict

import maa
# MaaFramework相关导入
from maa.tasker import Tasker
from maa.toolkit import Toolkit, AdbDevice
from maa.resource import Resource
from maa.controller import AdbController

from core.config_manager import ConfigManager
from core.domain.device_info import DeviceInfo


class MaaFrameworkManager:
    """
    基于MaaFramework的设备管理器
    负责设备连接、资源管理和设备隔离
    """

    def __init__(self, resource_path: str = "assets/resource", config_manager: ConfigManager = None):
        """
        初始化MaaFramework环境
        
        Args:
            resource_path: 资源路径
        """
        # 初始化工具包选项
        Toolkit.init_option("./")

        # 创建资源实例
        self.resource = Resource()
        # self.resource.use_cpu()
        self.resource_path = resource_path

        self.config_manager = config_manager

        # 存储设备实例的字典
        self.device_instances: Dict[str, Tasker] = {}

        # 存储设备控制器的字典
        self.device_controllers: Dict[str, AdbController] = {}

        # 存储设备信息的字典
        self.device_infos: Dict[str, DeviceInfo] = {}

        # 初始化日志
        self.logger = logging.getLogger(__name__)

        # 注册自定义识别和动作
        self._register_custom_recognitions()
        self._register_custom_actions()

        # 加载资源包
        self._load_resources()
        # 加载设备名
        self._load_device_names()

    def _register_custom_recognitions(self):
        """注册自定义识别"""
        # 这里可以注册项目特定的识别逻辑
        pass

    def _register_custom_actions(self):
        """注册自定义动作"""
        # 这里可以注册项目特定的动作逻辑
        pass

    def _load_resources(self):
        """加载识别资源包"""
        try:
            if not os.path.exists(self.resource_path):
                self.logger.warning(f"资源路径不存在: {self.resource_path}")
                return

            self.logger.info(f"MaaFW版本：{maa.Library.version()}")
            self.logger.info(f"开始加载资源包: {self.resource_path}")
            res_job = self.resource.post_bundle(self.resource_path)
            res_job.wait()

            if res_job.status.succeeded:
                self.logger.info("资源包加载成功")
            else:
                self.logger.error("资源包加载失败")

        except Exception as e:
            self.logger.error(f"加载资源包时出错: {e}")
            # 即使出错也要初始化游戏逻辑处理器

    def _load_device_names(self):
        """从配置文件加载小说信息"""
        pass
        # try:
        #     novels_data = self.config_manager.get_config("devices", {})
        #     for name, novel_data in novels_data.items():
        #         self.novels[name] = NovelInfo.from_dict(novel_data)
        #     self.logger.info(f"加载了 {len(self.novels)} 本小说")
        # except Exception as e:
        #     self.logger.error(f"加载小说信息失败: {e}")

    def find_devices(self) -> List[AdbDevice]:
        """
        查找可用的ADB设备
        
        Returns:
            设备列表
        """
        try:
            devices = Toolkit.find_adb_devices()
            seen_addresses = set()
            unique_devices = []
            for device in devices:
                if device.address not in seen_addresses:
                    seen_addresses.add(device.address)
                    unique_devices.append(device)
            self.logger.info(f"找到 {len(unique_devices)} 个设备")
            return unique_devices
        except Exception as e:
            self.logger.error(f"查找设备时出错: {e}")
            return []

    def connect_device(self, device_info: AdbDevice) -> Tasker:
        """
        连接到指定设备
        
        Args:
            device_info: 设备信息对象
            
        Returns:
            设备对应的Tasker实例
        """
        try:
            device_serial = device_info.address  # 使用设备地址作为唯一标识符

            self.logger.info(f"开始连接设备: {device_info.name} ({device_serial})")

            # 创建ADB控制器实例
            controller = AdbController(
                adb_path=device_info.adb_path,
                address=device_info.address,
                screencap_methods=device_info.screencap_methods,
                input_methods=device_info.input_methods,
                config=device_info.config,
            )

            # 连接设备并等待完成
            connect_job = controller.post_connection()
            connect_job.wait()

            if not connect_job.status.succeeded:
                raise Exception("Device connection failed")

            # 创建任务器实例
            tasker = Tasker()

            # 绑定资源和控制器到任务器
            tasker.bind(self.resource, controller)

            # 检查任务器是否初始化成功
            if not tasker.inited:
                raise Exception("Failed to init MAA tasker")

            # 存储设备实例
            self.device_instances[device_serial] = tasker
            self.device_controllers[device_serial] = controller
            self.device_infos[device_serial] = DeviceInfo(device_serial)

            self.logger.info(f"设备连接成功: {device_serial}")
            return tasker

        except Exception as e:
            self.logger.error(f"连接设备 {device_info.address} 失败: {e}")
            raise

    def disconnect_device(self, device_serial: str):
        """
        断开设备连接
        
        Args:
            device_serial: 设备序列号
        """
        try:
            if device_serial in self.device_instances:
                # 清理资源
                if device_serial in self.device_controllers:
                    del self.device_controllers[device_serial]

                del self.device_instances[device_serial]
                self.logger.info(f"设备已断开: {device_serial}")
        except Exception as e:
            self.logger.error(f"断开设备 {device_serial} 时出错: {e}")

    def get_device_tasker(self, device_serial: str) -> Optional[Tasker]:
        """
        获取设备对应的Tasker实例
        
        Args:
            device_serial: 设备序列号
            
        Returns:
            设备对应的Tasker实例
        """
        return self.device_instances.get(device_serial)

    def get_connected_device_serial_list(self) -> List[str]:
        """
        获取已连接的设备序列号列表
        
        Returns:
            已连接设备的序列号列表
        """
        return list(self.device_instances.keys())

    def is_device_connected(self, device_serial: str) -> bool:
        """
        检查设备是否已连接
        
        Args:
            device_serial: 设备序列号
            
        Returns:
            是否已连接
        """
        return device_serial in self.device_instances

    def get_connected_device_info_list(self) -> List[DeviceInfo]:
        """
        获取已连接的设备序列号列表

        Returns:
            已连接设备的序列号列表
        """
        return list(self.device_infos.values())
