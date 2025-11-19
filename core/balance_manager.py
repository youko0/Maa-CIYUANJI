#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代币管理器
负责代币的管理、消耗、过期处理等
"""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, asdict
from typing import List

from utils.logger import get_logger
from core.config_manager import ConfigManager


@dataclass
class BalanceInfo:
    """代币信息类"""
    amount: int  # 代币数量
    expire_time: str  # 过期时间，格式: yyyy-MM-dd HH:mm:ss
    balance: int  # 余额
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BalanceInfo':
        """从字典创建实例"""
        return cls(
            amount=data["amount"],
            expire_time=data["expire_time"],
            balance=data["balance"]
        )


class BalanceRecord:
    """代币使用记录"""
    
    def __init__(self, device_address: str, novel_name: str, chapter_name: str, 
                 coins_used: int, timestamp: str):
        self.device_address = device_address
        self.novel_name = novel_name
        self.chapter_name = chapter_name
        self.coins_used = coins_used
        self.timestamp = timestamp  # 格式: yyyy-MM-dd HH:mm:ss
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "device_address": self.device_address,
            "novel_name": self.novel_name,
            "chapter_name": self.chapter_name,
            "coins_used": self.coins_used,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BalanceRecord':
        """从字典创建实例"""
        record = cls(
            data["device_address"],
            data["novel_name"],
            data["chapter_name"],
            data["coins_used"],
            data["timestamp"]
        )
        return record


class BalanceManager:
    """代币管理器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.logger = get_logger()
        
        # 加载代币使用记录
        self.records: List[BalanceRecord] = []
        self._load_records()
    
    def _load_records(self):
        """从配置文件加载代币使用记录"""
        try:
            records_data = self.config_manager.get_config("coin_records", [])
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
    
    def add_coins(self, device_address: str, amount: int) -> List[BalanceInfo]:
        """为设备添加代币（签到获得）"""
        try:
            # 计算过期时间（7天后）
            expire_time = datetime.now() + timedelta(days=7)
            expire_time_str = expire_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 创建新的代币对象
            coin = BalanceInfo(amount=amount, expire_time=expire_time_str, balance=amount)
            
            # 获取设备现有的代币
            device_coins = self.get_device_coins(device_address)
            device_coins.append(coin)
            
            # 保存更新后的代币信息
            self._save_device_coins(device_address, device_coins)
            
            self.logger.info(f"为设备 {device_address} 添加 {amount} 个代币，过期时间: {expire_time_str}")
            return device_coins
        except Exception as e:
            self.logger.error(f"为设备 {device_address} 添加代币失败: {e}")
            return []
    
    def get_device_coins(self, device_address: str) -> List[BalanceInfo]:
        """获取设备的代币信息"""
        try:
            # 从配置中获取设备代币信息
            all_coins = self.config_manager.get_config("coins", {})
            device_coins_data = all_coins.get(device_address, [])
            device_coins = [BalanceInfo.from_dict(coin_data) for coin_data in device_coins_data]
            
            # 过滤掉已过期的代币
            now = datetime.now()
            valid_coins = []
            for coin in device_coins:
                expire_time = datetime.strptime(coin.expire_time, "%Y-%m-%d %H:%M:%S")
                if expire_time > now:
                    valid_coins.append(coin)
                else:
                    self.logger.info(f"代币已过期，数量: {coin.amount}，过期时间: {coin.expire_time}")
            
            # 更新配置（移除过期代币）
            if len(valid_coins) != len(device_coins):
                self._save_device_coins(device_address, valid_coins)
            
            return valid_coins
        except Exception as e:
            self.logger.error(f"获取设备 {device_address} 的代币信息失败: {e}")
            return []
    
    def _save_device_coins(self, device_address: str, coins: List[BalanceInfo]):
        """保存设备的代币信息"""
        try:
            all_coins = self.config_manager.get_config("coins", {})
            all_coins[device_address] = [coin.to_dict() for coin in coins]
            self.config_manager.set_config("coins", all_coins)
            self.config_manager.save()
        except Exception as e:
            self.logger.error(f"保存设备 {device_address} 的代币信息失败: {e}")
    
    def get_total_balance(self, device_address: str) -> int:
        """获取设备代币总余额"""
        try:
            coins = self.get_device_coins(device_address)
            total_balance = sum(coin.balance for coin in coins)
            return total_balance
        except Exception as e:
            self.logger.error(f"计算设备 {device_address} 代币总余额失败: {e}")
            return 0
    
    def get_total_balance_all_devices(self) -> int:
        """获取所有设备代币总余额"""
        try:
            all_coins = self.config_manager.get_config("coins", {})
            total_balance = 0
            for device_address in all_coins:
                total_balance += self.get_total_balance(device_address)
            return total_balance
        except Exception as e:
            self.logger.error(f"计算所有设备代币总余额失败: {e}")
            return 0
    
    def get_nearest_expire_time(self, device_address: str) -> Optional[str]:
        """获取设备最近的代币过期时间"""
        try:
            coins = self.get_device_coins(device_address)
            if not coins:
                return None
            
            # 找到最近的过期时间
            expire_times = [datetime.strptime(coin.expire_time, "%Y-%m-%d %H:%M:%S") for coin in coins]
            nearest_expire = min(expire_times)
            return nearest_expire.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            self.logger.error(f"获取设备 {device_address} 最近代币过期时间失败: {e}")
            return None
    
    def consume_coins(self, device_address: str, novel_name: str, chapter_name: str, 
                      amount: int) -> bool:
        """消耗代币购买章节"""
        try:
            # 获取设备代币
            coins = self.get_device_coins(device_address)
            if not coins:
                self.logger.warning(f"设备 {device_address} 没有可用代币")
                return False
            
            # 按过期时间排序（优先使用即将过期的代币）
            coins.sort(key=lambda x: datetime.strptime(x.expire_time, "%Y-%m-%d %H:%M:%S"))
            
            # 计算总余额是否足够
            total_balance = sum(coin.balance for coin in coins)
            if total_balance < amount:
                self.logger.warning(f"设备 {device_address} 代币余额不足，需要: {amount}，现有: {total_balance}")
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
            self._save_device_coins(device_address, coins)
            
            # 记录使用情况
            record = BalanceRecord(
                device_address=device_address,
                novel_name=novel_name,
                chapter_name=chapter_name,
                coins_used=amount,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            self.records.append(record)
            self.save_records()
            
            self.logger.info(f"设备 {device_address} 成功消耗 {amount} 个代币购买小说 {novel_name} 章节 {chapter_name}")
            return True
        except Exception as e:
            self.logger.error(f"设备 {device_address} 消耗代币失败: {e}")
            return False
    
    def get_records_by_device(self, device_address: str) -> List[BalanceRecord]:
        """获取指定设备的代币使用记录"""
        try:
            return [record for record in self.records if record.device_address == device_address]
        except Exception as e:
            self.logger.error(f"获取设备 {device_address} 的代币使用记录失败: {e}")
            return []
    
    def get_all_records(self) -> List[BalanceRecord]:
        """获取所有代币使用记录"""
        return self.records.copy()