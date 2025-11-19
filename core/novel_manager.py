#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小说管理器
负责小说的添加、删除、识别进度管理等
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from utils.logger import get_logger
from core.config_manager import ConfigManager


class NovelInfo:
    """小说信息类"""
    
    def __init__(self, name: str, start_chapter: int = 1, end_chapter: int = 9999):
        self.name = name
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.current_chapter = start_chapter
        self.last_recognize_time: Optional[str] = None
        self.is_active = True  # 是否启用
        self.progress = 0.0  # 识别进度百分比
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "start_chapter": self.start_chapter,
            "end_chapter": self.end_chapter,
            "current_chapter": self.current_chapter,
            "last_recognize_time": self.last_recognize_time,
            "is_active": self.is_active,
            "progress": self.progress
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NovelInfo':
        """从字典创建实例"""
        novel = cls(
            data["name"],
            data.get("start_chapter", 1),
            data.get("end_chapter", 9999)
        )
        novel.current_chapter = data.get("current_chapter", novel.start_chapter)
        novel.last_recognize_time = data.get("last_recognize_time")
        novel.is_active = data.get("is_active", True)
        novel.progress = data.get("progress", 0.0)
        return novel


class ChapterInfo:
    """章节信息类"""
    
    def __init__(self, name: str, content: str, device_address: str):
        self.name = name
        self.content = content
        self.device_address = device_address
        self.recognize_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "content": self.content,
            "device_address": self.device_address,
            "recognize_time": self.recognize_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChapterInfo':
        """从字典创建实例"""
        chapter = cls(
            data["name"],
            data["content"],
            data["device_address"]
        )
        chapter.recognize_time = data.get("recognize_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return chapter


class NovelManager:
    """小说管理器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.logger = get_logger()
        self.novels: Dict[str, NovelInfo] = {}  # name -> NovelInfo
        
        # 创建小说数据目录
        self.novels_dir = Path("novels")
        self.novels_dir.mkdir(exist_ok=True)
        
        # 加载已保存的小说信息
        self._load_novels()
    
    def _load_novels(self):
        """从配置文件加载小说信息"""
        try:
            novels_data = self.config_manager.get_config("novels", {})
            for name, novel_data in novels_data.items():
                self.novels[name] = NovelInfo.from_dict(novel_data)
            self.logger.info(f"加载了 {len(self.novels)} 本小说")
        except Exception as e:
            self.logger.error(f"加载小说信息失败: {e}")
    
    def save_novels(self):
        """保存小说信息到配置文件"""
        try:
            novels_data = {name: novel.to_dict() for name, novel in self.novels.items()}
            self.config_manager.set_config("novels", novels_data)
            self.config_manager.save()
            self.logger.info("小说信息保存成功")
        except Exception as e:
            self.logger.error(f"保存小说信息失败: {e}")
    
    def add_novel(self, name: str, start_chapter: int = 1, end_chapter: int = 9999) -> bool:
        """添加新小说"""
        try:
            if name in self.novels:
                self.logger.warning(f"小说 {name} 已存在")
                return False
            
            novel = NovelInfo(name, start_chapter, end_chapter)
            self.novels[name] = novel
            
            # 创建小说目录
            novel_dir = self.novels_dir / name
            novel_dir.mkdir(exist_ok=True)
            
            self.save_novels()
            self.logger.info(f"添加小说 {name} 成功")
            return True
        except Exception as e:
            self.logger.error(f"添加小说 {name} 失败: {e}")
            return False
    
    def remove_novel(self, name: str) -> bool:
        """移除小说"""
        try:
            if name not in self.novels:
                self.logger.warning(f"小说 {name} 不存在")
                return False
            
            del self.novels[name]
            self.save_novels()
            self.logger.info(f"移除小说 {name} 成功")
            return True
        except Exception as e:
            self.logger.error(f"移除小说 {name} 失败: {e}")
            return False
    
    def disable_novel(self, name: str) -> bool:
        """停用小说"""
        try:
            if name not in self.novels:
                self.logger.warning(f"小说 {name} 不存在")
                return False
            
            self.novels[name].is_active = False
            self.save_novels()
            self.logger.info(f"停用小说 {name} 成功")
            return True
        except Exception as e:
            self.logger.error(f"停用小说 {name} 失败: {e}")
            return False
    
    def enable_novel(self, name: str) -> bool:
        """启用小说"""
        try:
            if name not in self.novels:
                self.logger.warning(f"小说 {name} 不存在")
                return False
            
            self.novels[name].is_active = True
            self.save_novels()
            self.logger.info(f"启用小说 {name} 成功")
            return True
        except Exception as e:
            self.logger.error(f"启用小说 {name} 失败: {e}")
            return False
    
    def get_all_novels(self) -> List[NovelInfo]:
        """获取所有小说"""
        return list(self.novels.values())
    
    def get_active_novels(self) -> List[NovelInfo]:
        """获取启用的小说"""
        return [novel for novel in self.novels.values() if novel.is_active]
    
    def start_recognize(self, name: str) -> bool:
        """开始识别指定小说"""
        try:
            if name not in self.novels:
                self.logger.warning(f"小说 {name} 不存在")
                return False
            
            novel = self.novels[name]
            if not novel.is_active:
                self.logger.warning(f"小说 {name} 已停用")
                return False
            
            # 更新识别时间
            novel.last_recognize_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_novels()
            
            self.logger.info(f"开始识别小说 {name}")
            return True
        except Exception as e:
            self.logger.error(f"开始识别小说 {name} 失败: {e}")
            return False
    
    def save_chapter(self, novel_name: str, chapter_info: ChapterInfo) -> bool:
        """保存章节内容"""
        try:
            if novel_name not in self.novels:
                self.logger.warning(f"小说 {novel_name} 不存在")
                return False
            
            # 创建章节文件
            novel_dir = self.novels_dir / novel_name
            chapter_file = novel_dir / f"{chapter_info.name}.json"
            
            with open(chapter_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_info.to_dict(), f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"保存章节 {chapter_info.name} 到小说 {novel_name} 成功")
            return True
        except Exception as e:
            self.logger.error(f"保存章节 {chapter_info.name} 到小说 {novel_name} 失败: {e}")
            return False
    
    def export_novel_to_txt(self, novel_name: str) -> bool:
        """导出小说为txt文件"""
        try:
            if novel_name not in self.novels:
                self.logger.warning(f"小说 {novel_name} 不存在")
                return False
            
            novel_dir = self.novels_dir / novel_name
            if not novel_dir.exists():
                self.logger.warning(f"小说目录 {novel_name} 不存在")
                return False
            
            # 收集所有章节内容
            chapters_content = []
            for chapter_file in novel_dir.glob("*.json"):
                try:
                    with open(chapter_file, 'r', encoding='utf-8') as f:
                        chapter_data = json.load(f)
                        chapter_info = ChapterInfo.from_dict(chapter_data)
                        chapters_content.append(f"章节: {chapter_info.name}\n{chapter_info.content}\n\n")
                except Exception as e:
                    self.logger.error(f"读取章节文件 {chapter_file} 失败: {e}")
                    continue
            
            # 写入txt文件
            txt_file = novel_dir / f"{novel_name}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.writelines(chapters_content)
            
            self.logger.info(f"导出小说 {novel_name} 为txt文件成功")
            return True
        except Exception as e:
            self.logger.error(f"导出小说 {novel_name} 为txt文件失败: {e}")
            return False