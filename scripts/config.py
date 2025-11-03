from pathlib import Path

class Config:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent.resolve()
        self.DATA_DIR = self.BASE_DIR / "data"

        # 预定义路径
        self.WORD_LISTS = self.DATA_DIR / "word_lists"
        self.CUSTOM = self.WORD_LISTS / "custom"
        self.MATCHED = self.DATA_DIR / "word_lists" / "matched"
        self.CEDICT = self.DATA_DIR / "cedict_ts.u8.txt"
        self.AFTER = self.CUSTOM / "after"
        self.UN_MATCHED = self.CUSTOM / "un_matched"

        self.CET = self.WORD_LISTS / "local" 

        # 数据库配置
        self.DB_PATH = self.DATA_DIR / "users.db"
        self.SECRET_KEY = 'your-secret-key'

    def ensure_dirs(self):
        for path in [self.CUSTOM, self.MATCHED]:
            path.mkdir(parents=True, exist_ok=True)
        return self


# 使用示例
if __name__ == "__main__":
    config = Config().ensure_dirs()
