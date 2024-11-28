import random
import time
from log_config import logger


# 增加一个函数处理 429 错误并重试
def handle_429_error(url, headers, cookies):
    """处理 429 错误，进行指数退避（Exponential Backoff）"""
    delay = random.uniform(5, 20)  # 随机延时 5 到 10 秒
    logger.warning(f"遇到 429 错误，等待 {delay:.2f} 秒后重试...")
    time.sleep(delay)  # 等待后重试
