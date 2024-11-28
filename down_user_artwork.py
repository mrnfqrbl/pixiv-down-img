# 下载用户的所有作品

from pdi_config import config

from concurrent.futures import ThreadPoolExecutor, as_completed
from log_config import logger


def download_user_artworks(user_id, down_path, artwork_threads, img_threads):
    from user_artworks import fetch_user_artworks
    HRADERS = config.HEADERS
    COOKIES = config.COOKIES
    artwork_ids = fetch_user_artworks(user_id, HRADERS, COOKIES)

    if not artwork_ids:
        logger.warning(f"用户 {user_id} 没有作品可下载，跳过该用户。")
        return

    logger.info(f"开始下载用户 {user_id} 的 {len(artwork_ids)} 个作品...")

    # 为每个作品 ID 启动下载任务
    # print("这是art_threads在调用前的类型",type(artwork_threads))
    with ThreadPoolExecutor(max_workers=artwork_threads) as user_executor:
        futures = []
        from artwork_down import download_artwork_images
        for artwork_id in artwork_ids:
            futures.append(user_executor.submit(download_artwork_images, artwork_id, user_id, down_path, img_threads))

        # 等待所有作品下载任务完成
        for future in as_completed(futures):
            future.result()
