"""
WordsProject-forstudent - 日志工具模块

提供统一的日志记录功能

Copyright (c) 2024 WordsProject-forstudent Authors
"""

import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import logging


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器。

    Args:
        name: 日志记录器名称

    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler('project.log')
        formatter = logging.Formatter(
            '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
