"""
小说处理模块
负责小说内容识别、保存和管理
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from config_manager import ConfigManager
from logger import app_logger


class NovelProcessor:
    """小说处理器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        # 确保novels目录存在
        self.novels_dir = "novels"
        if not os.path.exists(self.novels_dir):
            os.makedirs(self.novels_dir)
    
    def save_chapter_content(self, novel_name: str, chapter_name: str, 
                           content: Dict[str, Any], device_id: str) -> bool:
        """
        保存章节内容到JSON文件
        
        Args:
            novel_name: 小说名称
            chapter_name: 章节名称
            content: 章节内容
            device_id: 设备ID
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 创建小说目录
            novel_dir = os.path.join(self.novels_dir, novel_name)
            if not os.path.exists(novel_dir):
                os.makedirs(novel_dir)
            
            # 创建章节文件路径
            chapter_file = os.path.join(novel_dir, f"{chapter_name}.json")
            
            # 准备章节数据
            chapter_data = {
                "novel_name": novel_name,
                "chapter_name": chapter_name,
                "content": content,
                "device_id": device_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 保存到JSON文件
            with open(chapter_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, ensure_ascii=False, indent=4)
            
            # 更新进度状态
            self.config_manager.update_novel_progress(novel_name, chapter_name, device_id)
            
            app_logger.log_novel_action("保存章节", novel_name, f"章节: {chapter_name}, 设备: {device_id}")
            return True
        except Exception as e:
            app_logger.error(f"保存章节内容失败: {e}")
            return False
    
    def is_chapter_processed(self, novel_name: str, chapter_name: str) -> bool:
        """
        检查章节是否已被处理
        
        Args:
            novel_name: 小说名称
            chapter_name: 章节名称
            
        Returns:
            bool: 是否已处理
        """
        return self.config_manager.is_chapter_processed(novel_name, chapter_name)
    
    def get_novel_chapters(self, novel_name: str) -> List[str]:
        """
        获取小说的所有章节列表
        
        Args:
            novel_name: 小说名称
            
        Returns:
            List[str]: 章节列表
        """
        novel_dir = os.path.join(self.novels_dir, novel_name)
        if not os.path.exists(novel_dir):
            return []
        
        chapters = []
        for filename in os.listdir(novel_dir):
            if filename.endswith(".json"):
                chapter_name = filename[:-5]  # 去掉.json后缀
                chapters.append(chapter_name)
        
        return chapters
    
    def export_novel_to_txt(self, novel_name: str, output_path: str) -> bool:
        """
        导出小说为TXT文件
        
        Args:
            novel_name: 小说名称
            output_path: 输出文件路径
            
        Returns:
            bool: 是否导出成功
        """
        try:
            novel_dir = os.path.join(self.novels_dir, novel_name)
            if not os.path.exists(novel_dir):
                raise FileNotFoundError(f"小说目录不存在: {novel_dir}")
            
            # 获取所有章节
            chapters = self.get_novel_chapters(novel_name)
            if not chapters:
                raise FileNotFoundError(f"未找到小说章节: {novel_name}")
            
            # 按章节名排序
            chapters.sort()
            
            # 写入TXT文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"小说: {novel_name}\n")
                f.write("=" * 50 + "\n\n")
                
                for chapter_name in chapters:
                    chapter_file = os.path.join(novel_dir, f"{chapter_name}.json")
                    try:
                        with open(chapter_file, 'r', encoding='utf-8') as cf:
                            chapter_data = json.load(cf)
                            
                        # 写入章节标题
                        f.write(f"\n\n第{chapter_name}章\n")
                        f.write("-" * 30 + "\n")
                        
                        # 写入章节内容（这里假设内容在content字段中）
                        content = chapter_data.get("content", {})
                        # 根据实际内容结构调整提取方式
                        if isinstance(content, dict):
                            # 如果内容是字典，尝试提取文本
                            text_content = content.get("text", str(content))
                            f.write(text_content)
                        else:
                            # 如果内容是其他类型，直接转换为字符串
                            f.write(str(content))
                    except Exception as e:
                        f.write(f"\n[无法读取章节 {chapter_name}: {str(e)}]\n")
            
            app_logger.log_novel_action("导出小说", novel_name, f"导出路径: {output_path}")
            return True
        except Exception as e:
            app_logger.error(f"导出小说失败: {e}")
            return False
    
    def get_device_chapters(self, novel_name: str, device_id: str) -> List[str]:
        """
        获取指定设备已处理的章节列表
        
        Args:
            novel_name: 小说名称
            device_id: 设备ID
            
        Returns:
            List[str]: 该设备处理的章节列表
        """
        novel_progress = self.config_manager.get_stats().get("novel_progress", {})
        if novel_name not in novel_progress:
            return []
        
        device_chapters = []
        for chapter, info in novel_progress[novel_name].items():
            if info.get("device_id") == device_id:
                device_chapters.append(chapter)
        
        return device_chapters


# 示例使用
if __name__ == "__main__":
    # 创建配置管理器和小说处理器
    config_manager = ConfigManager()
    processor = NovelProcessor(config_manager)
    
    # 示例：保存章节内容
    sample_content = {
        "text": "这是小说章节的内容...",
        "images": ["image1.jpg", "image2.jpg"]
    }
    
    # 保存章节
    success = processor.save_chapter_content(
        "测试小说", 
        "第一章", 
        sample_content, 
        "device_001"
    )
    print(f"保存章节结果: {success}")
    
    # 检查章节是否已处理
    processed = processor.is_chapter_processed("测试小说", "第一章")
    print(f"章节是否已处理: {processed}")
    
    # 导出小说
    export_success = processor.export_novel_to_txt("测试小说", "test_novel.txt")
    print(f"导出小说结果: {export_success}")