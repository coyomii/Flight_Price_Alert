import json
import os
import time
import requests
import logging
from datetime import datetime # 用于获取当前时间

# --- WxPusher 配置 ---
# 从环境变量读取敏感信息
WXPUSHER_TOKEN = os.getenv("WXPUSHER_TOKEN")
WXPUSHER_UID = os.getenv("WXPUSHER_UID")

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('monitor')

# WxPusher 通知函数
def notify_user(contents, summarys):
    """使用 WxPusher 发送通知"""
    if not WXPUSHER_TOKEN or not WXPUSHER_UID:
        logger.error("WxPusher TOKEN 或 UID 未在环境变量中设置，无法发送通知。")
        return None

    url = 'http://wxpusher.zjiecode.com/api/send/message'
    # 添加基本的 Content-Type header
    headers = {'Content-Type': 'application/json'}
    datas = {
        "appToken": WXPUSHER_TOKEN,
        "content": contents,
        "summary": summarys,
        "contentType": 1,  # 1 表示文本
        "topicIds": [],
        "uids": [WXPUSHER_UID],
        "url": "" # 可选，点击消息跳转的 URL
    }
    try:
        response = requests.post(url=url, headers=headers, json=datas, timeout=10) # 添加超时
        response.raise_for_status() # 检查 HTTP 错误状态
        response_json = response.json()

        # 清理内容中的换行符以便于日志记录
        cleaned_contents = contents.replace('\n', ' ')
        if response_json.get("code") == 1000:
            logger.info(f"WxPusher 通知发送成功: {summarys}")
            logger.info(f"WxPusher 通知内容: {cleaned_contents}")
        else:
            logger.error(f"WxPusher 通知发送失败: API返回错误 {response_json}")
            logger.error(f"失败的通知内容: {cleaned_contents}")
        return response_json
    except requests.exceptions.RequestException as e:
        logger.error(f"WxPusher 通知发送请求失败: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"WxPusher 通知处理失败: {str(e)}")
        return None

# --- 主逻辑 ---
if __name__ == "__main__":
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(current_dir, 'config.json')

    # 读取json配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"错误：配置文件 {config_path} 未找到。")
        exit(1)
    except json.JSONDecodeError:
        logger.error(f"错误：配置文件 {config_path} 格式错误。")
        exit(1)

    # --- 初始化或读取上次价格 ---
    # 使用 setdefault 确保即使 config.json 中没有这些键，也能安全访问
    config.setdefault("lastDirectPrices", {})
    config.setdefault("lastNonDirectPrices", {})

    # 基础URL
    baseUrl = "https://flights.ctrip.com/itinerary/api/12808/lowestPrice?"

    # 标志位，标记是否有配置被更新
    config_updated = False

    # --- 获取机票信息 ---
    try:
        direct_response = requests.get(
            f'{baseUrl}flightWay={config["flightWay"]}&dcity={config["placeFrom"]}&acity={config["placeTo"]}&direct'
            f'=true&army=false', timeout=20) # 添加超时
        direct_response.raise_for_status() # 检查 HTTP 错误
        direct_data = direct_response.json()

        non_direct_response = requests.get(
            f'{baseUrl}flightWay={config["flightWay"]}&dcity={config["placeFrom"]}&acity={config["placeTo"]}&army=false',
             timeout=20) # 添加超时
        non_direct_response.raise_for_status() # 检查 HTTP 错误
        non_direct_data = non_direct_response.json()

    except requests.exceptions.Timeout:
        logger.error("请求携程 API 超时。")
        exit(1) # 超时则退出，下次 Action 再试
    except requests.exceptions.RequestException as e:
        logger.error(f"请求携程 API 时发生错误: {e}")
        exit(1) # 其他请求错误也退出
    except json.JSONDecodeError:
        logger.error("解析携程 API 响应 JSON 时失败。")
        exit(1) # JSON 解析失败则退出

    # 检查 API 返回状态
    if direct_data.get("status") == 2 or direct_data.get("data") is None:
        logger.warning(f"无法获取 {config['placeFrom']}->{config['placeTo']} 的直飞机票信息。API 消息: {direct_data.get('msg', '无')}")
        # 可以选择退出或继续处理非直飞
        # exit(1) # 如果直飞必须有，则退出

    if non_direct_data.get("status") == 2 or non_direct_data.get("data") is None:
        logger.warning(f"无法获取 {config['placeFrom']}->{config['placeTo']} 的非直飞机票信息。API 消息: {non_direct_data.get('msg', '无')}")
        # 可以选择退出或继续处理直飞
        # exit(1) # 如果非直飞必须有，则退出

    # --- 解析和比较价格 ---
    # 安全地获取价格数据，避免因 data 为 None 出错
    direct_results = {}
    if direct_data.get("data") and direct_data["data"].get("oneWayPrice"):
        direct_results = direct_data["data"]["oneWayPrice"][0] # 假设总是第一个元素

    non_direct_results = {}
    if non_direct_data.get("data") and non_direct_data["data"].get("oneWayPrice"):
        non_direct_results = non_direct_data["data"]["oneWayPrice"][0] # 假设总是第一个元素

    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 获取当前时间字符串

    for date in config["dateToGo"]:
        # 使用 .get 获取价格，如果日期不存在则返回 None
        direct_price = direct_results.get(date)
        non_direct_price = non_direct_results.get(date)

        # 获取上次记录的价格，如果日期首次出现，默认为 0 或 None (用 0 便于比较)
        last_direct_price = config["lastDirectPrices"].get(date, 0)
        last_non_direct_price = config["lastNonDirectPrices"].get(date, 0)

        logger.info(f"日期: {date}")

        # --- 处理直飞价格 ---
        if direct_price is None:
            logger.warning(f"未能获取 {date} 的直飞价格。")
        else:
            logger.info(f"  当前直飞价格: {direct_price}, 上次记录价格: {last_direct_price}")
            if last_direct_price == 0: # 首次记录该日期的价格
                message_content = (f"【首次推送】\n日期: {date}\n出发地: {config['placeFrom']}\n目的地: {config['placeTo']}\n"
                                   f"直飞价格: {direct_price}\n查询时间: {current_time_str}")
                message_summary = f"首次推送-{date}直飞¥{direct_price}"
                notify_user(message_content, message_summary)
                config["lastDirectPrices"][date] = direct_price
                config_updated = True
            elif abs(direct_price - last_direct_price) >= config["priceStep"]:
                change = direct_price - last_direct_price
                change_str = f"+{change}" if change > 0 else str(change)
                message_content = (f"【价格变动提醒】\n日期: {date}\n出发地: {config['placeFrom']}\n目的地: {config['placeTo']}\n"
                                   f"类型: 直飞\n当前价格: {direct_price}\n上次价格: {last_direct_price}\n"
                                   f"价格变化: {change_str}\n查询时间: {current_time_str}")
                message_summary = f"{date}直飞价格变动 {change_str} (¥{direct_price})"
                notify_user(message_content, message_summary)
                config["lastDirectPrices"][date] = direct_price
                config_updated = True
            # else: # 价格未变动或变动未达阈值，无需通知，也无需更新 last price

        # --- 处理非直飞价格 ---
        if non_direct_price is None:
            logger.warning(f"未能获取 {date} 的非直飞价格。")
        else:
            logger.info(f"  当前非直飞价格: {non_direct_price}, 上次记录价格: {last_non_direct_price}")
            if last_non_direct_price == 0: # 首次记录该日期的价格
                message_content = (f"【首次推送】\n日期: {date}\n出发地: {config['placeFrom']}\n目的地: {config['placeTo']}\n"
                                   f"非直飞价格: {non_direct_price}\n查询时间: {current_time_str}")
                message_summary = f"首次推送-{date}非直飞¥{non_direct_price}"
                notify_user(message_content, message_summary)
                config["lastNonDirectPrices"][date] = non_direct_price
                config_updated = True
            elif abs(non_direct_price - last_non_direct_price) >= config["priceStep"]:
                change = non_direct_price - last_non_direct_price
                change_str = f"+{change}" if change > 0 else str(change)
                message_content = (f"【价格变动提醒】\n日期: {date}\n出发地: {config['placeFrom']}\n目的地: {config['placeTo']}\n"
                                   f"类型: 非直飞\n当前价格: {non_direct_price}\n上次价格: {last_non_direct_price}\n"
                                   f"价格变化: {change_str}\n查询时间: {current_time_str}")
                message_summary = f"{date}非直飞价格变动 {change_str} (¥{non_direct_price})"
                notify_user(message_content, message_summary)
                config["lastNonDirectPrices"][date] = non_direct_price
                config_updated = True
            # else: # 价格未变动或变动未达阈值，无需通知，也无需更新 last price

    # --- 保存更新后的配置 ---
    if config_updated:
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False) # ensure_ascii=False 保证中文正常写入
            logger.info(f"配置文件 {config_path} 已更新。")
        except IOError as e:
            logger.error(f"无法写入配置文件 {config_path}: {e}")
    else:
        logger.info("价格无变化或变化未达阈值，配置文件未更新。")

    logger.info("机票价格检查完成。")
