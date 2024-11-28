# log_config.py
import loguru
import sys

# 创建并配置 logger 对象
logger = loguru.logger


def setup_logger(debug=True):
    """
    设置日志记录器，输出日志到控制台和文件。

    参数:
        debug (bool): 如果为 True，日志级别为 DEBUG，否则为 INFO。
    """
    logger.remove()  # 移除默认的日志处理器
    log_level = "DEBUG" if debug else "INFO"
    logger.add(
        sys.stdout,
        level=log_level,
        colorize=True  # 启用颜色输出
    )

    # 设置文件日志处理器（如果需要记录到文件）
    logger.add("PDI.log", level=log_level, rotation="3 MB", compression="zip")


# 调用 setup_logger 配置日志
setup_logger(debug=True)
