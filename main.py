import os
import time
import sys

from config_loader import load_config, save_config
from artwork_down import download_artwork_images
from log_config import setup_logger
from pdi_config import config

setup_logger()
from log_config import logger

logger = logger


def pdi_config():
    global logger
    config_data = load_config()

    if config_data and config_data.get("PHPSESSID"):
        config.store_config(config_data)  # 存储配置到 Config 类中
    else:
        logger.error("配置加载失败：缺少 PHPSESSID 或配置数据为空")
        time.sleep(5)
        sys.exit(1)  # 如果配置不完整，退出程序

    setup_logger(debug=config.debug_mode)


def global_exception_handler(exc_type, exc_value, exc_tb):
    """全局异常处理函数，捕获所有未处理的异常"""
    if exc_type is not KeyboardInterrupt:  # 排除手动终止程序的异常
        print(f"捕获到未处理的异常: {exc_value}")
        time.sleep(5)  # 延时5秒
        print("程序将在 5 秒后退出...")

    # 使用默认的异常处理方式打印异常信息
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def get_user_download_directory():
    # 判断操作系统
    if os.name == 'nt':  # Windows 系统
        try:
            # 打开注册表路径，Windows 默认的下载目录信息
            import winreg
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                          r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")

            # 先尝试获取 "Downloads" 键的值
            try:
                download_dir = winreg.QueryValueEx(registry_key, "Downloads")[0]
                # 如果找到了，则返回此路径
                if os.path.exists(download_dir):
                    return download_dir
            except FileNotFoundError:
                pass  # 如果没有找到 "Downloads" 键，继续查找 GUID 对应的路径

            # 定义 GUID 键名（这是下载目录的 GUID）
            download_guid = '{374DE290-123F-4565-9164-39C4925E467B}'

            # 尝试读取该 GUID 对应的下载目录
            download_dir = winreg.QueryValueEx(registry_key, download_guid)[0]

            # 关闭注册表键
            winreg.CloseKey(registry_key)

            # 如果路径存在，则返回
            if os.path.exists(download_dir):
                return download_dir
            else:
                print(f"下载目录 ({download_guid}) 无效！")
                sys.exit(1)  # 退出程序，因无法找到有效的下载目录

        except Exception as e:
            print(f"无法获取 Windows 下载目录：{e}")
            sys.exit(1)  # 退出程序，发生异常时

    else:  # Linux 或 macOS 系统
        # 默认的下载目录
        download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        if os.path.exists(download_dir):
            return download_dir
        else:
            print(f"下载目录 ({download_dir}) 无效！")
            sys.exit(1)  # 退出程序，因无法找到有效的下载目录


# 主程序
def main():
    pdi_config()
    # 使用缓存后的配置
    USER_IDS = config.USER_IDS
    ARTWORK_IDS = config.ARTWORK_IDS
    down_path = config.down_path
    if down_path == "":
        user_download_dir = get_user_download_directory()
        print("这是下载目录", user_download_dir)
        down_path = os.path.join(user_download_dir)
        logger.error(f"保存下路径：{down_path}")
        save_config("down_path", down_path, section="DEFAULT")

    HEADERS, COOKIES = config.HEADERS, config.COOKIES
    user_stats, skipped_stats, error_dict = config.user_stats, config.skipped_stats, config.error_dict
    img_threads = config.img_threads
    artwork_threads = config.artwork_threads

    # 打印配置内容
    logger.info(f"USER_IDS: {USER_IDS}")
    logger.info(f"ARTWORK_IDS: {ARTWORK_IDS}")
    logger.info(f"down_path: {down_path}")
    logger.debug(f"HEADERS: {HEADERS}")
    logger.debug(f"COOKIES: {COOKIES}")
    logger.debug(f"user_stats: {user_stats}")
    logger.debug(f"skipped_stats: {skipped_stats}")
    logger.debug(f"error_dict: {error_dict}")
    logger.debug(f"img_threads: {img_threads}")
    logger.debug(f"img_threads类型: {type(img_threads)}")
    logger.debug(f"artwork_threads: {type(artwork_threads)}")
    logger.debug(f"artwork_threads类型: {artwork_threads}")

    # 导入需要的模块
    from artwork_details import fetch_artwork_info
    from down_user_artwork import download_user_artworks

    # 检查 USER_IDS 是否为空，若不为空则下载用户作品
    if USER_IDS:
        for user_id in USER_IDS:
            logger.info(f"准备下载用户 {user_id}")
            download_user_artworks(user_id, down_path, artwork_threads, img_threads)
    else:
        logger.warning("USER_IDS 为空，跳过用户下载")

    # 检查 ARTWORK_IDS 是否为空，若不为空则下载单独作品
    if ARTWORK_IDS:
        for artwork_id in ARTWORK_IDS:
            logger.info(f"准备下载单独作品 {artwork_id}")

            user_id, user_name, artwork_name = fetch_artwork_info(artwork_id, HEADERS, COOKIES)
            logger.debug(f"作品信息: user_id={user_id}, user_name={user_name}, artwork_name={artwork_name}")
            logger.debug(f"图片线程main,{type(img_threads)}")
            download_artwork_images(artwork_id, user_id, down_path, img_threads)
    else:
        logger.warning("ARTWORK_IDS 为空，跳过作品下载")

    # 打印下载统计信息
    from print_stats import print_stats
    print_stats(user_stats, skipped_stats, error_dict)

    # 暂停 5 秒钟，便于查看日志
    time.sleep(5)

    # 退出程序
    sys.exit(0)


# 运行程序
if __name__ == "__main__":
    sys.excepthook = global_exception_handler
    main()
