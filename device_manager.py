"""
设备管理模块
负责使用MAA框架检测和管理Android设备
"""

from typing import List, Dict, Any
import json
from logger import app_logger


class DeviceInfo:
    """设备信息类"""
    
    def __init__(self, name: str, address: str, adb_path: str):
        self.name = name          # 设备名称
        self.address = address    # 连接地址（唯一标识）
        self.adb_path = adb_path  # ADB路径
        self.connected = False    # 连接状态
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "address": self.address,
            "adb_path": self.adb_path,
            "connected": self.connected
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceInfo':
        """从字典创建设备信息对象"""
        device = cls(data["name"], data["address"], data["adb_path"])
        device.connected = data.get("connected", False)
        return device
    
    def __str__(self):
        return f"{self.name} ({self.address})"


class DeviceManager:
    """设备管理器"""
    
    def __init__(self, config_file: str = "devices.json"):
        self.config_file = config_file
        self.devices: List[DeviceInfo] = []
        self.load_devices()
    
    def load_devices(self):
        """从配置文件加载设备信息"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.devices = [DeviceInfo.from_dict(device_data) for device_data in data]
            app_logger.info(f"从配置文件加载了 {len(self.devices)} 个设备")
        except FileNotFoundError:
            app_logger.info("设备配置文件不存在，将创建新的配置文件")
            self.devices = []
        except Exception as e:
            app_logger.error(f"加载设备配置文件失败: {e}")
            self.devices = []
    
    def save_devices(self):
        """保存设备信息到配置文件"""
        try:
            data = [device.to_dict() for device in self.devices]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            app_logger.info(f"设备信息已保存到 {self.config_file}")
        except Exception as e:
            app_logger.error(f"保存设备配置文件失败: {e}")
    
    def detect_devices(self) -> List[DeviceInfo]:
        """
        检测可用的Android设备
        注意：这里模拟MAA框架的设备检测功能
        实际使用时应调用MAA框架的API
        """
        # 模拟检测到的设备
        detected_devices = [
            DeviceInfo("模拟器1", "127.0.0.1:62001", "/path/to/adb1"),
            DeviceInfo("模拟器2", "127.0.0.1:62002", "/path/to/adb2"),
            DeviceInfo("手机1", "192.168.1.100:5555", "/path/to/adb3")
        ]
        
        app_logger.info(f"检测到 {len(detected_devices)} 个设备")
        return detected_devices
    
    def connect_device(self, device_address: str) -> bool:
        """
        连接指定设备
        
        Args:
            device_address: 设备连接地址
            
        Returns:
            bool: 连接是否成功
        """
        # 查找设备
        device = self.get_device_by_address(device_address)
        if not device:
            app_logger.warning(f"未找到设备: {device_address}")
            return False
        
        # 模拟连接过程
        # 实际使用时应调用MAA框架的连接API
        try:
            # 这里应该是实际的连接逻辑
            # 暂时模拟连接成功
            device.connected = True
            
            # 更新设备列表
            self.save_devices()
            
            app_logger.log_device_action("连接设备", device.name, f"地址: {device.address}")
            return True
        except Exception as e:
            app_logger.error(f"连接设备失败 {device_address}: {e}")
            return False
    
    def disconnect_device(self, device_address: str) -> bool:
        """
        断开指定设备
        
        Args:
            device_address: 设备连接地址
            
        Returns:
            bool: 断开是否成功
        """
        # 查找设备
        device = self.get_device_by_address(device_address)
        if not device:
            app_logger.warning(f"未找到设备: {device_address}")
            return False
        
        # 模拟断开过程
        try:
            device.connected = False
            
            # 更新设备列表
            self.save_devices()
            
            app_logger.log_device_action("断开设备", device.name, f"地址: {device.address}")
            return True
        except Exception as e:
            app_logger.error(f"断开设备失败 {device_address}: {e}")
            return False
    
    def get_device_by_address(self, address: str) -> DeviceInfo:
        """根据地址获取设备信息"""
        for device in self.devices:
            if device.address == address:
                return device
        return None  # type: ignore
    
    def get_connected_devices(self) -> List[DeviceInfo]:
        """获取已连接的设备列表"""
        return [device for device in self.devices if device.connected]
    
    def update_device_list(self, detected_devices: List[DeviceInfo]) -> None:
        """
        更新设备列表，合并新检测到的设备和已有的设备状态
        
        Args:
            detected_devices: 新检测到的设备列表
        """
        # 创建地址到设备的映射
        existing_devices = {device.address: device for device in self.devices}
        
        # 更新或添加设备
        updated_devices = []
        for detected_device in detected_devices:
            if detected_device.address in existing_devices:
                # 保留已有的连接状态
                existing_device = existing_devices[detected_device.address]
                detected_device.connected = existing_device.connected
                updated_devices.append(detected_device)
            else:
                # 新设备，默认未连接
                updated_devices.append(detected_device)
        
        self.devices = updated_devices
        self.save_devices()
        app_logger.info(f"设备列表已更新，共 {len(self.devices)} 个设备")


# 全局设备管理器实例
device_manager = DeviceManager()