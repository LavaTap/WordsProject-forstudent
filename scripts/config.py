"""
WordsProject-forstudent - 配置文件

定义项目全局配置路径和数据库配置

Copyright (c) 2024 WordsProject-forstudent Authors
"""

import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path，支持直接运行 python scripts/xxx.py
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _get_project_root() -> Path:
    """
    获取项目根目录。

    支持两种运行方式：
    1. python app.py - 直接运行
    2. python -m scripts.xxx - 模块方式运行

    Returns:
        项目根目录路径
    """
    # 优先使用环境变量指定的项目根目录
    project_root = os.getenv('PROJECT_ROOT')
    if project_root:
        return Path(project_root).resolve()

    # 从当前文件向上查找项目标记文件
    current = Path(__file__).resolve().parent
    markers = ['app.py', 'requirements.txt', '.git']

    # 向上查找直到找到项目标记
    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent

    # 回退：使用父级目录（scripts/ 的父级）
    return Path(__file__).resolve().parent.parent


class Config:
    """
    项目配置类。

    提供项目路径、数据库路径等配置的初始化和管理。
    """

    def __init__(self) -> None:
        """初始化配置路径。"""
        self.BASE_DIR: Path = _get_project_root()
        self.DATA_DIR: Path = self.BASE_DIR / "data"

        # 预定义路径
        self.WORD_LISTS: Path = self.DATA_DIR / "word_lists"
        self.CUSTOM: Path = self.WORD_LISTS / "custom"
        self.MATCHED: Path = self.DATA_DIR / "word_lists" / "matched"
        self.CEDICT: Path = self.DATA_DIR / "cedict_ts.u8.txt"
        self.AFTER: Path = self.CUSTOM / "after"
        self.UN_MATCHED: Path = self.CUSTOM / "un_matched"

        self.CET: Path = self.WORD_LISTS / "local"

        # 数据库配置
        self.DB_PATH: Path = self.DATA_DIR / "users.db"
        self.SECRET_KEY: str = 'your-secret-key'

    def ensure_dirs(self) -> "Config":
        """
        确保必要的目录存在。

        Returns:
            返回自身以支持链式调用
        """
        for path in [self.CUSTOM, self.MATCHED]:
            path.mkdir(parents=True, exist_ok=True)
        return self

    def debug_paths(self) -> dict[str, str]:
        """
        调试用：返回所有路径的字符串形式。

        Returns:
            包含所有路径的字典
        """
        return {
            key: str(getattr(self, key))
            for key in dir(self)
            if key.isupper() and isinstance(getattr(self, key), Path)
        }


if __name__ == "__main__":
    # 调试：打印所有路径
    config = Config().ensure_dirs()
    print("项目根目录:", config.BASE_DIR)
    print("\n所有路径配置:")
    for key, value in config.debug_paths().items():
        print(f"  {key}: {value}")
