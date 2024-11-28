# config.py
import json
from log_config import logger


class Config:
    def __init__(self):
        # 初始化配置项
        self.logger = logger
        self.PHPSESSID = ""
        self.USER_IDS = []
        self.ARTWORK_IDS = []
        self.Presets = 1
        self.debug_mode = False
        self.HEADERS = {}
        self.COOKIES = {}
        self.user_stats = {
            "download_failed": {},  # 初始为空字典
            "success": {},
            "file_exists": {},
        }
        self.skipped_stats = {"skipped_images_count": 0, 'file_exists': {}, 'error_dict': {}}
        self.error_dict = {}
        self.img_threads = 3
        self.artwork_threads = 2
        self.down_path = ""

    def store_config(self, config_data):
        """
        存储配置项并缓存到类中
        参数:
            config_data: 包含配置项的字典
            logger: 用于记录日志
        """
        # 使用传入的配置数据更新类的配置项
        self.PHPSESSID = config_data.get("PHPSESSID", "")
        self.USER_IDS = config_data.get("USER_IDS", [])
        self.ARTWORK_IDS = config_data.get("ARTWORK_IDS", [])
        self.Presets = config_data.get("Presets", 1)
        self.debug_mode = config_data.get("debug_mode", False)
        self.logger = logger
        self.img_threads = config_data.get("img_threads", 3)
        self.artwork_threads = config_data.get("artwork_threads", 2)
        self.down_path = config_data.get("down_path", "")

        # 日志记录
        self.logger.info(
            f"配置已缓存：PHPSESSID={self.PHPSESSID}, USER_IDS={self.USER_IDS}, ARTWORK_IDS={self.ARTWORK_IDS}, Presets={self.Presets}, debug_mode={self.debug_mode}")

        # 设置请求头和 cookies
        self.HEADERS = {
            "Referer": "https://www.pixiv.net/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        self.COOKIES = {
            "PHPSESSID": self.PHPSESSID
        }

        # 完成缓存后输出
        self.logger.info(f"配置缓存成功，当前配置：{self}")

    def __repr__(self):
        return f"Config(PHPSESSID={self.PHPSESSID}, USER_IDS={self.USER_IDS}, ARTWORK_IDS={self.ARTWORK_IDS}, Presets={self.Presets}, debug_mode={self.debug_mode})"


config = Config()
