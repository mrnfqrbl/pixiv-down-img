import requests
from log_config import logger


def fetch_user_artworks(user_id, headers, cookies):
    logger.debug("fetch_user_artworks函数被调用")
    logger.debug(f"传入信息: user_id={user_id}, headers={headers}, cookies={cookies}")
    """
    获取指定用户的作品 ID 列表.

    参数:
        user_id (str): 用户 ID.
        headers (dict): 请求头信息.
        cookies (dict): 用户验证的 cookies.
        logger (logging.Logger): 用于记录日志的 logger 对象。

    返回:
        list: 用户的作品 ID 列表。如果没有作品，则返回空列表。
    """
    url = f"https://www.pixiv.net/ajax/user/{user_id}/profile/all"
    # 使用 logger 记录正在请求的日志
    logger.info(f"正在请求用户 {user_id} 的作品信息...")

    try:
        # 发送请求获取用户的作品信息
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()  # 确保请求成功

        # 解析响应数据
        data = response.json()
        logger.info(f"完整url:{url}")
        logger.debug(f"返回的数据: {data}")  # 打印完整的返回数据用于调试

        if data.get("error") is False:  # 如果请求没有错误
            illusts = data["body"].get("illusts", {})

            # 如果作品是字典格式
            if isinstance(illusts, dict):
                # 直接返回字典的所有键（作品 ID）
                illust_ids = list(illusts.keys())  # 获取作品 ID 列表

                if illust_ids:
                    logger.info(f"成功获取 {user_id} 的 {len(illust_ids)} 个作品 ID。")
                else:
                    logger.warning(f"用户 {user_id} 没有作品。")

                return illust_ids  # 返回作品 ID 列表

            else:
                logger.warning(f"警告：作品数据结构不符合预期，无法解析作品 ID。")
                return []  # 返回空列表

        else:
            logger.error(f"错误：未能正确获取用户 {user_id} 的作品信息。")
            return []  # 如果请求发生错误，返回空列表

    except requests.exceptions.RequestException as e:
        logger.error(f"请求错误: {e}")
        return []  # 请求失败时返回空列表
