# -*- coding: utf-8 -*-
"""
应用程序常量定义
"""

# 应用程序基本信息
APP_NAME = "Maa-CIYUANJI"
# alpha版：内部测试版
# beta版：公开测试版
APP_VERSION = "0.1.0"
APP_AUTHOR = "can"

# 日志级别 DEBUG、INFO、ERROR
LOG_LEVEL = "DEBUG"

# 状态码定义
STATUS_READY = 0
STATUS_LOADING = 1
STATUS_PROCESSING = 2
STATUS_COMPLETED = 3
STATUS_ERROR = -1

# 风险级别定义
RISK_HIGH = "高危"
RISK_MEDIUM = "中危"
RISK_LOW = "低危"

# 默认窗口尺寸（参考helper-wjdr-python）
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
MIN_WIDTH = 600
MIN_HEIGHT = 400