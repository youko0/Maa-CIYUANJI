import json
import os
from datetime import datetime
from typing import Dict, Any
from logger import app_logger


class ConfigManager:
    """配置和状态管理类"""
    
    def __init__(self, config_file: str = "config.json", stats_file: str = "stats.json"):
        self.config_file = config_file
        self.stats_file = stats_file
        self.config = self._load_config()
        self.stats = self._load_stats()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            default_config = {
                "target_novel": "",
                "start_chapter": "",
                "end_chapter": ""
            }
            self._save_config(default_config)
            return default_config
    
    def _load_stats(self) -> Dict[str, Any]:
        """加载状态文件"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认状态
            default_stats = {
                "coins": [],
                "novel_progress": {}
            }
            self._save_stats(default_stats)
            return default_stats
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            app_logger.info(f"配置文件已保存: {self.config_file}")
        except Exception as e:
            app_logger.error(f"保存配置文件失败: {e}")
    
    def _save_stats(self, stats: Dict[str, Any]) -> None:
        """保存状态文件"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=4)
            app_logger.info(f"状态文件已保存: {self.stats_file}")
        except Exception as e:
            app_logger.error(f"保存状态文件失败: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """更新配置"""
        self.config.update(config)
        self._save_config(self.config)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取状态"""
        return self.stats
    
    def update_stats(self, stats: Dict[str, Any]) -> None:
        """更新状态"""
        self.stats.update(stats)
        self._save_stats(self.stats)
    
    def add_coin(self, amount: int, expire_time: str) -> None:
        """添加代币"""
        coins = self.stats.get("coins", [])
        coin = {
            "amount": amount,
            "expire_time": expire_time,
            "balance": amount
        }
        coins.append(coin)
        self.stats["coins"] = coins
        self._save_stats(self.stats)
        app_logger.log_coin_action("添加代币", amount, f"过期时间: {expire_time}")
    
    def use_coins(self, amount: int) -> bool:
        """使用代币，优先使用即将过期的代币"""
        coins = self.stats.get("coins", [])
        if not coins:
            app_logger.warning("代币不足，无法使用")
            return False
        
        # 记录使用前的余额
        total_before = sum(coin["balance"] for coin in coins)
        
        # 按过期时间排序，即将过期的在前面
        coins.sort(key=lambda x: x["expire_time"])
        
        remaining = amount
        for coin in coins:
            if remaining <= 0:
                break
            
            if coin["balance"] > 0:
                if coin["balance"] >= remaining:
                    coin["balance"] -= remaining
                    remaining = 0
                else:
                    remaining -= coin["balance"]
                    coin["balance"] = 0
        
        if remaining > 0:
            # 代币不足
            app_logger.warning(f"代币不足，需要{amount}个，实际只有{total_before}个")
            return False
        
        self.stats["coins"] = coins
        self._save_stats(self.stats)
        app_logger.log_coin_action("使用代币", amount, f"使用前余额: {total_before}")
        return True
    
    def get_total_coins(self) -> int:
        """获取代币总余额"""
        coins = self.stats.get("coins", [])
        return sum(coin["balance"] for coin in coins)
    
    def update_novel_progress(self, novel_name: str, chapter: str, device_id: str) -> None:
        """更新小说识别进度"""
        novel_progress = self.stats.get("novel_progress", {})
        if novel_name not in novel_progress:
            novel_progress[novel_name] = {}
        
        novel_progress[novel_name][chapter] = {
            "device_id": device_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.stats["novel_progress"] = novel_progress
        self._save_stats(self.stats)
    
    def is_chapter_processed(self, novel_name: str, chapter: str) -> bool:
        """检查章节是否已被处理"""
        novel_progress = self.stats.get("novel_progress", {})
        if novel_name not in novel_progress:
            return False
        return chapter in novel_progress[novel_name]