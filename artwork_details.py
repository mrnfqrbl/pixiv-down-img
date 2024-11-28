import requests
from log_config import logger
from handle_429 import handle_429_error


def fetch_artwork_info(artwork_id, headers, cookies):
    """
    获取作品的详细信息，包括用户 ID、用户名、作品标题.

    参数:
        artwork_id (str): 作品 ID.
        headers (dict): 请求头信息.
        cookies (dict): 用户验证的 cookies.
        logger (logging.Logger): 用于记录日志的 logger 对象.

    返回:
        tuple: 包含用户 ID、用户名、作品标题的元组 (user_id, user_name, illust_title).
    """
    url = f"https://www.pixiv.net/ajax/illust/{artwork_id}"
    logger.debug(f"正在请求作品 {artwork_id} 的详细信息...")

    try:
        # 发送请求获取作品信息
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()  # 确保请求成功

        data = response.json()  # 解析响应数据
        if data["error"] is False:
            illust_data = data["body"]
            logger.info(f"成功获取作品 {artwork_id} 的详细信息")
            return illust_data["userId"], illust_data["userName"], illust_data["illustTitle"]
        else:
            logger.warning(f"作品 {artwork_id} 获取失败，错误信息：{data.get('message', '无详细错误信息')}")
    except requests.exceptions.RequestException as e:
        logger.error(f"请求错误: {e}")
        # handle_429_error(url, headers,cookies)

    return None, None, None


def fetch_image_urls(artwork_id, headers, cookies):
    """
    获取作品的所有图片 URL 列表.

    参数:
        artwork_id (str): 作品 ID.
        headers (dict): 请求头信息.
        cookies (dict): 用户验证的 cookies.
        logger (logging.Logger): 用于记录日志的 logger 对象.

    返回:
        list: 图片 URL 列表.
    """
    url = f"https://www.pixiv.net/ajax/illust/{artwork_id}/pages"
    logger.debug(f"正在请求作品 {artwork_id} 的图片 URL 列表...")

    try:
        # 发送请求获取图片 URL 列表
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()  # 确保请求成功

        data = response.json()  # 解析响应数据
        if data["error"] is False:
            img_urls = [page["urls"]["original"] for page in data["body"]]
            logger.info(f"成功获取作品 {artwork_id} 的 {len(img_urls)} 张图片 URL")
            return img_urls
        else:
            logger.warning(f"作品 {artwork_id} 图片 URL 获取失败，错误信息：{data.get('message', '无详细错误信息')}")
    except requests.exceptions.RequestException as e:
        logger.error(f"请求错误: {e}")

    return []
