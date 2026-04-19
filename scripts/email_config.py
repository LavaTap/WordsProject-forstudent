"""
WordsProject-forstudent - 邮件配置模块

定义SMTP邮件发送配置

Copyright (c) 2024 WordsProject-forstudent Authors
"""

import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# SMTP邮件配置
SMTP_CONFIG = {
    'host': 'smtp.qq.com',
    'port': 465,
    'username': 'your_email@qq.com',
    'password': 'your_smtp_auth_code',  # QQ邮箱授权码
    'sender_email': 'your_email@qq.com',
    'sender_name': 'WordsProject 验证系统'
}
