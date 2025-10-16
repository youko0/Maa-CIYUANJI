from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from maa.toolkit import AdbDevice


@dataclass
class DeviceInfo:
    """设备信息包装类"""
    name: str
    address: str
    adb_path: str
    connected: bool = False
    screencap_methods: int = 0
    input_methods: int = 0
    config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
    
    @classmethod
    def from_adb_device(cls, adb_device: AdbDevice) -> 'DeviceInfo':
        """从AdbDevice创建DeviceInfo实例"""
        return cls(
            name=adb_device.name,
            address=adb_device.address,
            adb_path=str(adb_device.adb_path),
            screencap_methods=adb_device.screencap_methods,
            input_methods=adb_device.input_methods,
            config=adb_device.config
        )
    
    def to_adb_device(self) -> AdbDevice:
        """转换为AdbDevice实例"""
        import pathlib
        return AdbDevice(
            name=self.name,
            address=self.address,
            adb_path=pathlib.Path(self.adb_path),
            screencap_methods=self.screencap_methods,
            input_methods=self.input_methods,
            config=self.config
        )