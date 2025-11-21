#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代币管理器
负责代币的管理、消耗、过期处理等
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from typing import List

from utils.logger import get_logger
from core.config_manager import get_config_manager
from utils.time_utils import TimeUtils


@dataclass
class BalanceInfo:
    """代币信息类"""
    device_serial: str  # 设备序列号
    amount: int  # 代币数量
    balance: int  # 余额
    expire_time: datetime  # 过期时间，格式: yyyy-MM-dd HH:mm:ss

    def __init__(self, device_serial: str, amount: int, balance: int, expire_time: datetime):
        self.device_serial = device_serial
        self.amount = amount
        self.balance = balance
        self.expire_time = expire_time

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "device_serial": self.device_serial,
            "amount": self.amount,
            "balance": self.balance,
            "expire_time": TimeUtils.format(self.expire_time),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BalanceInfo':
        """从字典创建实例"""
        return cls(
            device_serial=data["device_serial"],
            amount=data["amount"],
            balance=data["balance"],
            expire_time=TimeUtils.strptime(data["expire_time"]),
        )


class BalanceRecord:
    """代币使用记录"""

    def __init__(self, device_serial: str, novel_name: str, chapter_name: str,
                 coins_used: int, timestamp: str):
        self.device_serial = device_serial
        self.novel_name = novel_name
        self.chapter_name = chapter_name
        self.coins_used = coins_used
        self.timestamp = timestamp  # 格式: yyyy-MM-dd HH:mm:ss

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "device_serial": self.device_serial,
            "novel_name": self.novel_name,
            "chapter_name": self.chapter_name,
            "coins_used": self.coins_used,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BalanceRecord':
        """从字典创建实例"""
        record = cls(
            data["device_serial"],
            data["novel_name"],
            data["chapter_name"],
            data["coins_used"],
            data["timestamp"]
        )
        return record


class BalanceManager:
    """余额管理器"""

    def __init__(self):
        self.config_manager = get_config_manager()
        self.logger = get_logger()

        self.device_balances: Dict[str, List[BalanceInfo]] = {}

        # 加载代币使用记录
        self.records: List[BalanceRecord] = []
        self._load_balances()
        self._load_records()

    def _load_balances(self):
        """从配置文件加载余额信息"""
        try:
            info_datas = self.config_manager.get_config("device_balances", {})
            self.device_balances = {}
            for device_serial, balance_infos in info_datas.items():
                self.device_balances[device_serial] = [BalanceInfo.from_dict(info) for info in balance_infos]
            self.logger.info(f"加载了 {len(self.device_balances)} 个设备的余额信息")
        except Exception as e:
            self.logger.error(f"加载余额信息失败: {e}")

    def save_balances(self):
        """保存余额信息到配置文件"""
        try:
            info_datas = {}
            for device_serial, balance_infos in self.device_balances.items():
                info_datas[device_serial] = [info.to_dict() for info in balance_infos]
            self.config_manager.set_config("device_balances", info_datas)
            self.config_manager.save()
            self.logger.info("余额信息保存成功")
        except Exception as e:
            self.logger.error(f"保存余额信息记录失败: {e}")

    def _load_records(self):
        """从配置文件加载代币使用记录"""
        try:
            records_data = self.config_manager.get_config("coin_records", {})
            self.records = [BalanceRecord.from_dict(record_data) for record_data in records_data]
            self.logger.info(f"加载了 {len(self.records)} 条代币使用记录")
        except Exception as e:
            self.logger.error(f"加载代币使用记录失败: {e}")

    def save_records(self):
        """保存代币使用记录到配置文件"""
        try:
            records_data = [record.to_dict() for record in self.records]
            self.config_manager.set_config("coin_records", records_data)
            self.config_manager.save()
            self.logger.info("代币使用记录保存成功")
        except Exception as e:
            self.logger.error(f"保存代币使用记录失败: {e}")

    def init_balance(self, device_serial: str):
        """初始化余额信息"""
        if device_serial not in self.device_balances:
            self.device_balances[device_serial] = []

    def add_balance(self, device_serial: str, amount: int, expire_time: datetime) -> List[BalanceInfo]:
        """为设备添加代币（签到获得）"""
        try:
            # 创建新的代币对象
            balance_info = BalanceInfo(device_serial=device_serial, amount=amount, balance=amount, expire_time=expire_time)

            # 获取设备现有的代币
            device_balance_list = self.get_device_balance_list(device_serial)
            device_balance_list.append(balance_info)

            # 保存更新后的代币信息
            # self._save_device_coins(device_serial, device_coins)

            expire_time_str = expire_time.strftime("%Y-%m-%d %H:%M:%S")
            self.logger.info(f"为设备 {device_serial} 添加 {amount} 个代币，过期时间: {expire_time_str}")
            return device_balance_list
        except Exception as e:
            self.logger.error(f"为设备 {device_serial} 添加代币失败: {e}")
            return []

    def refresh_balance(self, device_serial: str, balance_info_list: List[BalanceInfo]):
        """刷新设备的代币信息"""
        device_balance_list = self.get_device_balance_list(device_serial)
        # 将device_balance_list替换为device_balance_list，但不改变其引用
        device_balance_list[:] = []
        device_balance_list.extend(balance_info_list)
        return True

    def get_device_balance_list(self, device_serial: str) -> List[BalanceInfo]:
        """获取设备的代币信息"""
        return self.device_balances.get(device_serial)

    def _save_device_coins(self, device_serial: str, coins: List[BalanceInfo]):
        """保存设备的代币信息"""
        try:
            all_coins = self.config_manager.get_config("balances", {})
            all_coins[device_serial] = [coin.to_dict() for coin in coins]
            self.config_manager.set_config("coins", all_coins)
            self.config_manager.save()
        except Exception as e:
            self.logger.error(f"保存设备 {device_serial} 的代币信息失败: {e}")

    def get_total_balance(self, device_serial: str) -> int:
        """获取设备代币总余额"""
        try:
            coins = self.get_device_balance_list(device_serial)
            total_balance = sum(coin.balance for coin in coins)
            return total_balance
        except Exception as e:
            self.logger.error(f"计算设备 {device_serial} 代币总余额失败: {e}")
            return 0

    def get_total_balance_all_devices(self) -> int:
        """获取所有设备代币总余额"""
        try:
            all_coins = self.config_manager.get_config("balances", {})
            total_balance = 0
            for device_serial in all_coins:
                total_balance += self.get_total_balance(device_serial)
            return total_balance
        except Exception as e:
            self.logger.error(f"计算所有设备代币总余额失败: {e}")
            return 0

    def get_nearest_expire_time(self, device_serial: str) -> Optional[str]:
        """获取设备最近的代币过期时间"""
        try:
            coins = self.get_device_balance_list(device_serial)
            if not coins:
                return None

            # 找到最近的过期时间
            expire_times = [datetime.strptime(coin.expire_time, "%Y-%m-%d %H:%M:%S") for coin in coins]
            nearest_expire = min(expire_times)
            return nearest_expire.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            self.logger.error(f"获取设备 {device_serial} 最近代币过期时间失败: {e}")
            return None

    def consume_coins(self, device_serial: str, novel_name: str, chapter_name: str,
                      amount: int) -> bool:
        """消耗代币购买章节"""
        try:
            # 获取设备代币
            coins = self.get_device_balance_list(device_serial)
            if not coins:
                self.logger.warning(f"设备 {device_serial} 没有可用代币")
                return False

            # 按过期时间排序（优先使用即将过期的代币）
            coins.sort(key=lambda x: datetime.strptime(x.expire_time, "%Y-%m-%d %H:%M:%S"))

            # 计算总余额是否足够
            total_balance = sum(coin.balance for coin in coins)
            if total_balance < amount:
                self.logger.warning(f"设备 {device_serial} 代币余额不足，需要: {amount}，现有: {total_balance}")
                return False

            # 消耗代币
            remaining_amount = amount
            for coin in coins:
                if remaining_amount <= 0:
                    break

                if coin.balance > 0:
                    if coin.balance >= remaining_amount:
                        # 当前代币余额足够支付
                        coin.balance -= remaining_amount
                        remaining_amount = 0
                    else:
                        # 当前代币余额不足，全部扣除
                        remaining_amount -= coin.balance
                        coin.balance = 0

            # 保存更新后的代币信息
            self._save_device_coins(device_serial, coins)

            # 记录使用情况
            record = BalanceRecord(
                device_serial=device_serial,
                novel_name=novel_name,
                chapter_name=chapter_name,
                coins_used=amount,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            self.records.append(record)
            self.save_records()

            self.logger.info(f"设备 {device_serial} 成功消耗 {amount} 个代币购买小说 {novel_name} 章节 {chapter_name}")
            return True
        except Exception as e:
            self.logger.error(f"设备 {device_serial} 消耗代币失败: {e}")
            return False

    def get_records_by_device(self, device_serial: str) -> List[BalanceRecord]:
        """获取指定设备的代币使用记录"""
        try:
            return [record for record in self.records if record.device_serial == device_serial]
        except Exception as e:
            self.logger.error(f"获取设备 {device_serial} 的代币使用记录失败: {e}")
            return []

    def get_all_records(self) -> List[BalanceRecord]:
        """获取所有代币使用记录"""
        return self.records.copy()


# 全局余额管理器实例
_BALANCE_MANAGER = None


def get_balance_manager():
    """获取全局余额管理器实例"""
    global _BALANCE_MANAGER
    if _BALANCE_MANAGER is None:
        _BALANCE_MANAGER = BalanceManager()
    return _BALANCE_MANAGER
