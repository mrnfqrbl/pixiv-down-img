import os
import json
import re
import rate_limited_requests as requests
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import IncompleteRead
from log_config import logger


# 创建一个会自动重试的 requests session
def get_session():
    session = requests.Session()
    retry = Retry(
        total=3,  # 设置最大重试次数
        backoff_factor=1,  # 设置每次重试的等待时间间隔（即 1, 2, 4 秒递增）
        status_forcelist=[500, 502, 503, 504, 429],  # 针对这些 HTTP 错误进行重试
        allowed_methods=["GET"],  # 对 GET 请求进行重试（已更新为 allowed_methods）
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


# 清理文件路径中的非法字符

# def clean_filename_part(part):
#     # 使用正则表达式清理文件名中的非法字符（保留字母、数字、下划线、横杠、空格等）
#     return re.sub(r'[<>:"/\\|?*]', '_', part)

def clean_filename_part(part):
    # 使用正则表达式清理文件名中的非法字符（保留字母、数字、下划线、横杠、空格等）
    return re.sub(r'[<>:"/\\|?*]', '_', part)


# 清理整个路径
def clean_path(path):
    # 判断 path 是否为 Path 对象
    if isinstance(path, Path):
        # 获取驱动器和路径的各部分
        drive, *path_parts = path.parts
    else:
        # 如果是字符串路径，先转换为 Path 对象
        path_obj = Path(path)
        drive, *path_parts = path_obj.parts

    # 对每一部分进行清理（跳过驱动器部分）
    cleaned_parts = [drive] + [clean_filename_part(part) for part in path_parts]

    # 重新组合为 Path 对象，并返回
    return Path(*cleaned_parts)


def download_image(
        img_url, save_path, headers, cookies, user_stats, skipped_stats,
        error_dict_file="error.json", max_retries=3
):
    session = get_session()  # 使用自定义的带有重试机制的 session
    retry_count = 0  # 记录单图片的重试次数
    success = False  # 是否成功下载标志

    # 确保作品名称中的非法字符被清理
    save_path = clean_path(save_path)

    # 确保目录路径合法并存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    while retry_count < max_retries and not success:
        try:
            ext = "jpg" if img_url.lower().endswith(".jpg") else "png"
            save_path_with_ext = f"{save_path}.{ext}"
            save_path_with_ext = clean_path(save_path_with_ext)  # 再次清理完整路径

            # 检查文件是否已经存在
            if os.path.exists(save_path_with_ext):
                skipped_stats["file_exists"][save_path_with_ext] = skipped_stats["file_exists"].get(save_path_with_ext,
                                                                                                    0) + 1
                skipped_stats["skipped_images_count"] += 1  # 跳过的总图片数量
                logger.debug(f"文件已存在，跳过下载: {save_path_with_ext}")
                return

            # 下载图片
            logger.debug(f"开始下载图片: {img_url} 到 {save_path_with_ext}")
            response = session.get(img_url, headers=headers, cookies=cookies, timeout=(5, 5))
            response.raise_for_status()  # 如果状态码不是 200，会抛出异常

            # 保存图片到文件
            with open(save_path_with_ext, "wb") as file:
                file.write(response.content)

            # 更新统计数据
            user_id = Path(save_path).parts[-2]  # 提取用户 ID
            if user_id not in user_stats:
                user_stats[user_id] = {"artworks": 0, "images": 0}

            user_stats[user_id]["images"] += 1
            logger.debug(f"图片已成功保存到: {save_path_with_ext}")
            success = True  # 标记为成功下载

        except (requests.exceptions.RequestException, IncompleteRead) as e:
            retry_count += 1
            logger.warning(f"下载失败，重试 {retry_count}/{max_retries} 次: {img_url}")

            # 如果达到最大重试次数，记录错误
            if retry_count == max_retries:
                try:
                    # 获取路径信息（清理非法字符后的信息）
                    user_name = clean_path(Path(save_path).parts[-3])  # 用户名称
                    artwork_name = clean_path(Path(save_path).parts[-2])  # 作品名称
                    artwork_id = Path(save_path).parts[-1]  # 作品 ID

                    # 生成图片的唯一键
                    image_seq = len(skipped_stats["error_dict"].get(user_name, {}).get(artwork_name, {})) + 1
                    image_key = f"{artwork_name}-{artwork_id}-{image_seq}"

                    # 错误信息
                    error_info = {
                        "url": img_url,
                        "最终保存路径": save_path_with_ext,
                        "图片错误原因": str(e),
                    }

                    # 更新错误字典
                    if user_name not in skipped_stats["error_dict"]:
                        skipped_stats["error_dict"][user_name] = {}

                    if artwork_name not in skipped_stats["error_dict"][user_name]:
                        skipped_stats["error_dict"][user_name][artwork_name] = {}

                    skipped_stats["error_dict"][user_name][artwork_name][image_key] = error_info

                    # 更新统计数据
                    skipped_stats["download_failed"][save_path] = skipped_stats["download_failed"].get(save_path, 0) + 1
                    skipped_stats["skipped_images_count"] += 1

                    # 确保可以写入错误信息到文件
                    with open(error_dict_file, "w", encoding="utf-8") as f:
                        json.dump(skipped_stats["error_dict"], f, ensure_ascii=False, indent=4)

                    logger.error(f"下载图片 {save_path_with_ext} 失败: {e}")

                except Exception as err:
                    logger.error(f"记录错误到 {error_dict_file} 失败: {err}")
