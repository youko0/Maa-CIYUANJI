#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目配置脚本
配置MaaFramework资源文件
"""

import os
import shutil
from pathlib import Path


def configure_resources():
    """配置资源文件"""
    print("开始配置资源文件...")
    
    try:
        # 创建必要的目录
        resource_dir = Path("assets/resource")
        resource_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查MaaCommonAssets是否存在
        common_assets_dir = Path("assets/MaaCommonAssets")
        if not common_assets_dir.exists():
            print("警告: MaaCommonAssets目录不存在，请确保已下载子模块!")
            print("请运行以下命令下载子模块:")
            print("  git submodule update --init --recursive")
            return False
        
        # 配置OCR资源
        ocr_src_dir = common_assets_dir / "OCR"
        ocr_dst_dir = resource_dir / "model/ocr"
        
        if ocr_src_dir.exists():
            # 清理目标目录
            if ocr_dst_dir.exists():
                shutil.rmtree(ocr_dst_dir)
            
            # 复制OCR资源
            shutil.copytree(ocr_src_dir, ocr_dst_dir)
            print(f"OCR资源已配置: {ocr_dst_dir}")
        else:
            print("警告: OCR资源目录不存在!")
        
        # 配置pipeline资源
        pipeline_src_dir = resource_dir / "pipeline"
        pipeline_src_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建默认的pipeline文件（如果不存在）
        user_pipeline = pipeline_src_dir / "user.json"
        if not user_pipeline.exists():
            default_pipeline = {
                "Pipeline": {
                    "description": "默认Pipeline配置"
                }
            }
            import json
            with open(user_pipeline, 'w', encoding='utf-8') as f:
                json.dump(default_pipeline, f, ensure_ascii=False, indent=2)
            print(f"默认Pipeline文件已创建: {user_pipeline}")
        
        print("资源文件配置完成!")
        return True
        
    except Exception as e:
        print(f"资源配置过程中发生错误: {e}")
        return False


def main():
    print("次元姬小说助手 - 资源配置程序")
    print("=" * 40)
    
    if configure_resources():
        print("\n资源配置成功!")
        print("您现在可以运行项目了。")
    else:
        print("\n资源配置失败，请检查错误信息。")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())