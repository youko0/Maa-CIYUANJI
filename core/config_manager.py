#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理器
负责读取、保存和管理配置文件
"""

import json
from pathlib import Path
from typing import Any, Dict

from utils.logger import get_logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "configs/config.json", stats_file: str = "configs/stats.json"):
        self.config_file = Path(config_file)
        self.stats_file = Path(stats_file)
        self.logger = get_logger()
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载配置和状态
        self.config_data = self._load_json_file(self.config_file)
        self.stats_data = self._load_json_file(self.stats_file)
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """加载JSON文件"""
        if not file_path.exists():
            # 创建空的配置文件
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件 {file_path} 失败: {e}")
            return {}
    
    def _save_json_file(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"保存配置文件 {file_path} 失败: {e}")
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config_data.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.config_data[key] = value
    
    def get_stat(self, key: str, default: Any = None) -> Any:
        """获取状态项"""
        return self.stats_data.get(key, default)
    
    def set_stat(self, key: str, value: Any) -> None:
        """设置状态项"""
        self.stats_data[key] = value
    
    def save(self) -> bool:
        """保存所有配置和状态"""
        config_success = self._save_json_file(self.config_file, self.config_data)
        stats_success = self._save_json_file(self.stats_file, self.stats_data)
        return config_success and stats_success
    
    def save_config(self) -> bool:
        """保存配置文件"""
        return self._save_json_file(self.config_file, self.config_data)
    
    def save_stats(self) -> bool:
        """保存状态文件"""
        return self._save_json_file(self.stats_file, self.stats_data)