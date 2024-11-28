import random
import time
from pathlib import Path
from download import clean_path
from artwork_details import fetch_artwork_info, fetch_image_urls
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdi_config import config
from log_config import logger


# 下载作品的所有图片
def download_artwork_images(artwork_id, user_id, down_path, img_threads):
    HEADERS, COOKIES = config.HEADERS, config.COOKIES
    user_stats, skipped_stats, error_dict = config.user_stats, config.skipped_stats, config.error_dict

    try:
        user_id, user_name, illust_title = fetch_artwork_info(artwork_id, HEADERS, COOKIES)
        if not user_id or not user_name or not illust_title:
            user_stats["download_failed"].setdefault(user_id, {"artworks": 0, "images": 0})
            user_stats["download_failed"][user_id]["artworks"] += 1  # 跳过作品数量
            logger.warning(f"作品 {artwork_id} 信息获取失败，跳过该作品。")
            return

        re_artwork_folder = Path(f"{down_path}/{user_name}-{user_id}/{illust_title}-{artwork_id}")

        artwork_folder = clean_path(re_artwork_folder)
        logger.debug(f"下载路径:{artwork_folder}")

        artwork_folder.mkdir(parents=True, exist_ok=True)
        img_urls = fetch_image_urls(artwork_id, HEADERS, COOKIES)

        # 统计每个用户下载的图片数量
        user_stats["success"].setdefault(user_id, {"artworks": 0, "images": 0})
        user_stats["success"][user_id]["artworks"] += 1

        # 使用线程池下载图片
        logger.debug(f"这是img_threads在调用前的类型,{type(img_threads)}")
        with ThreadPoolExecutor(max_workers=img_threads) as img_executor:
            futures = []
            for index, img_url in enumerate(img_urls, start=1):
                img_name = f"{illust_title}-{artwork_id}-{index}"
                save_path = artwork_folder / img_name

                # logger.debug(f"正在下载图片 {img_url} 到 {save_path}")

                # 检查是否已下载此图片
                if save_path.exists():
                    user_stats["file_exists"].setdefault(user_id, {"artworks": 0, "images": 0})
                    user_stats["file_exists"][user_id]["images"] += 1  # 跳过图片数量
                    continue  # 如果文件已存在，跳过该图片

                # 添加请求延迟（随机 10 到 200 毫秒）
                time.sleep(random.uniform(0.01, 0.2))  # 随机延迟 10 到 200 毫秒

                from download import download_image
                futures.append(img_executor.submit(download_image, img_url, save_path, HEADERS, COOKIES, user_stats,
                                                   skipped_stats))

            # 等待所有图片下载任务完成
            for future in as_completed(futures):
                future.result()

    except Exception as e:
        user_stats["download_failed"].setdefault(user_id, {"artworks": 0, "images": 0})
        user_stats["download_failed"][user_id]["artworks"] += 1  # 跳过作品数量

        # 记录完整的错误堆栈
        logger.error(f"下载作品 {artwork_id} 时出错：{e}")
        logger.error("详细的错误堆栈信息:")
        logger.error(traceback.format_exc())  # 打印完整的错误堆栈

        # 记录错误信息到 error_dict
        if user_id not in error_dict:
            error_dict[user_id] = {}
        if illust_title not in error_dict[user_id]:
            error_dict[user_id][illust_title] = []

        # 添加错误类型和详细信息
        error_details = {
            "错误消息": str(e),
            "错误类型": type(e).__name__,  # 错误类型（如 ValueError, TypeError 等）
            "错误堆栈": traceback.format_exc(),  # 错误堆栈
            "作品id": artwork_id,  # 作品ID
            "作品标题": illust_title  # 作品标题
        }
        error_dict[user_id][illust_title].append(error_details)

        # 打印错误以便更直观地调试
        logger.error(f"错误详情: {error_details}")
