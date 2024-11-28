import configparser
import os
from log_config import logger

config_path = "PDI.ini"
config = configparser.ConfigParser()


def process_id_list(id_string):
    """
    处理用户 ID 和作品 ID 列表字符串，去除空格并按 '|' 分隔，返回有效 ID 列表。

    参数:
        id_string (str): 用 '|' 分隔的 ID 列表字符串，可能包含空格。

    返回:
        list: 处理后的 ID 列表。
    """
    if not id_string.strip():
        return []

    # 首先按 '|' 分割，再按空格分割每部分，去除多余空格
    return [item.strip() for part in id_string.split("|") for item in part.split() if item.strip()]


def load_config(debug=True):
    """
    加载配置文件，如果配置文件不存在则创建一个默认配置文件。

    参数:
        logger (logging.Logger): 用于记录日志的 logger 对象。
        debug (bool): 是否启用调试模式，默认开启（True），启用后记录更详细的日志。

    返回:
        dict: 返回包含配置项的字典，如果配置文件未找到则返回额外的提示信息标志。
    """

    # 如果配置文件不存在，则创建一个默认配置文件
    if not os.path.exists(config_path):
        logger.info(f"配置文件 {config_path} 不存在，正在创建默认配置...")

        # 写入默认配置
        config["DEFAULT"] = {
            "PHPSESSID": "",  # 用户需要在这里填写 PHPSESSID
            "Presets": "1",  # 使用预设值（1：启用，0：用户输入）
            "USER_IDS": "",  # 可选：默认用户 ID 列表，使用逗号分隔
            "ARTWORK_IDS": "",  # 可选：默认作品 ID 列表，使用逗号分隔
            "debug": "True",  # 新增配置项，启用调试模式（默认为 True）
            "artwork_threads": 2,  # 默认作品线程数
            "img_threads": 3,  # 默认图片线程数
            "down_path": ""
        }

        # 手动写入注释（确保以UTF-8编码写入）
        with open(config_path, "w", encoding="utf-8") as configfile:
            configfile.write("# PDI.ini 配置文件示例\n")
            configfile.write("# 请按照说明配置 PHPSESSID、预设使用选项以及用户 ID 和作品 ID\n\n")
            configfile.write("[DEFAULT]\n")
            configfile.write("# PHPSESSID 是必填项，请在这里填写你的pixiv的php会话id PHPSESSID\n")
            configfile.write("PHPSESSID = PHPSESSID\n\n")
            configfile.write("# Presets 是一个开关，设置为 1 表示启用预设，设置为 0 表示用户输入\n")
            configfile.write("Presets = 1\n\n")
            configfile.write("# USER_IDS 是一个可选项，用于指定预设的用户 ID 列表，使用逗号分隔\n")
            configfile.write("USER_IDS = \n\n")
            configfile.write("# ARTWORK_IDS 是一个可选项，用于指定预设的作品 ID 列表，使用逗号分隔\n")
            configfile.write("ARTWORK_IDS = \n\n")
            configfile.write("# debug 是一个开关，如果为true会有更详细的日志\n")
            configfile.write("debug = True\n\n")
            configfile.write("# 线程数设置，默认作品线程数为 2，图片线程数为 3\n")
            configfile.write("artwork_threads = 2\n")
            configfile.write("image_threads = 3\n")
            configfile.write("# 是一个必须项，用于指定下载路径，你也可以不填，不填会提示你输入\n")
            configfile.write("# 示例: 下载路径配置\n")
            configfile.write('#down_path = D:\\download\\xxxx \n')
            configfile.write("down_path = ")

        logger.info(f"已创建默认配置文件 {config_path}，请设置 PHPSESSID 和其他值后重新运行程序。")
        return {"need_restart": True}  # 返回额外的标志，表明需要用户手动配置并重启程序

    # 读取配置文件时，指定编码为 UTF-8
    config.read(config_path, encoding="utf-8")

    # 获取配置项并处理数据，确保去除前后空格
    PHPSESSID = config["DEFAULT"].get("PHPSESSID", "").strip()
    Presets = int(config["DEFAULT"].get("Presets", "1").strip())
    debug_mode = config["DEFAULT"].get("debug", "True").strip().lower() == "true"

    # 获取预设的用户 ID 和作品 ID，并进行处理
    USER_IDS = process_id_list(config["DEFAULT"].get("USER_IDS", "").strip())
    ARTWORK_IDS = process_id_list(config["DEFAULT"].get("ARTWORK_IDS", "").strip())

    # 获取线程数配置，默认为 2（作品）和 3（图片）
    artwork_threads = int(config["DEFAULT"].get("artwork_threads", "2").strip())
    image_threads = int(config["DEFAULT"].get("img_threads", "3").strip())
    # down_path
    down_path = config["DEFAULT"].get("down_path", "")

    logger.warning("已加载配置文件，但未检查 USER_IDS 和 ARTWORK_IDS 是否为空字符串。")

    # 检查 PHPSESSID 是否设置为默认值（为空字符串或为 'PHPSESSID'）
    if PHPSESSID == "" or PHPSESSID == "PHPSESSID":
        logger.error("PHPSESSID 为空或为默认值 'PHPSESSID'，请在 config.ini 中设置有效的 PHPSESSID 后重新运行程序。")
        return {"need_restart": True}  # 返回额外的标志，表明需要用户手动配置并重启程序

    # 如果 USER_IDS 或 ARTWORK_IDS 为空字符串，且 Presets 为 1，跳过预设并启用用户输入
    if (not USER_IDS and not ARTWORK_IDS):
        if Presets == 1:
            logger.warning("配置文件中 USER_IDS 或 ARTWORK_IDS 为空，虽然 Presets 设置为 1，但将跳过预设，启用用户输入。")
            Presets = 0  # 强制跳过预设，启用用户输入

    # 根据 debug 参数决定是否记录详细的调试信息
    logger.debug(f"读取的配置: {dict(config['DEFAULT'])}")

    logger.info(
        f"成功加载配置：PHPSESSID={PHPSESSID}, Presets={Presets}, USER_IDS={USER_IDS}, ARTWORK_IDS={ARTWORK_IDS}")
    logger.info(f"线程设置：作品线程数={artwork_threads}, 图片线程数={image_threads}")

    # 返回配置字典，键值对形式
    return {
        "PHPSESSID": PHPSESSID,
        "USER_IDS": USER_IDS,
        "ARTWORK_IDS": ARTWORK_IDS,
        "Presets": Presets,
        "debug_mode": debug_mode,
        "artwork_threads": artwork_threads,
        "img_threads": image_threads,
        "need_restart": False,  # 配置已成功加载
        "down_path": down_path
    }


config.optionxform = str  # 保证键名的大小写不变


def save_config(key, value, section="DEFAULT"):
    """
    仅更新配置中的指定键的值，保留其他内容不变。

    参数:
        key (str): 配置键。
        value (str): 配置值。
        section (str): 配置节，默认为 "DEFAULT"。
    """
    # 加载配置文件
    config.read(config_path, encoding="utf-8")

    # 如果是修改 DEFAULT 部分
    if section == "DEFAULT":
        # 更新默认配置中的键值
        if config.has_option(section, key):
            config.set(section, key, value)
        else:
            logger.warning(f"键 {key} 不在 {section} 部分中。")
    else:
        # 如果是其他节，先检查节是否存在，如果不存在则添加该节
        if not config.has_section(section):
            config.add_section(section)

        # 更新指定的键值
        if config.has_option(section, key):
            config.set(section, key, value)
        else:
            logger.warning(f"键 {key} 不在 {section} 部分中。")

    # 将更新后的配置写回文件，保留原始的注释
    with open(config_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)

    logger.info(f"成功更新配置：{section} -> {key} = {value}")
