import json

from log_config import logger


# 打印下载统计信息
def print_stats(user_stats, skipped_stats, error_dict):
    """打印下载统计信息"""
    for user_id, stats in user_stats["success"].items():
        logger.info(f"用户 {user_id} 下载了 {stats['artworks']} 个作品，共 {stats['images']} 张图。")

    for user_id, stats in user_stats["download_failed"].items():
        logger.info(f"用户 {user_id} 下载失败了 {stats['artworks']} 个作品，共 {stats['images']} 张图。")

    if skipped_stats.get("download_failed"):
        for file_path, fail_count in skipped_stats["download_failed"].items():
            logger.info(f"文件 {file_path} 下载失败，跳过了 {fail_count} 张图。")

    logger.info(f"总共跳过了 {skipped_stats['skipped_images_count']} 张图片。")

    with open("error.json", "w", encoding="utf-8") as f:
        json.dump(error_dict, f, ensure_ascii=False, indent=4)
