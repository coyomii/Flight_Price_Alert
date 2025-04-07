import json
import os
import time

import requests

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(current_dir, 'config.json')


def push_message(message, token):
    send_url = f'https://www.pushplus.plus/send?token={token}&title=jp&content={message}'
    requests.get(send_url)


if __name__ == "__main__":
    # 读取json配置文件
    with open(config_path, 'r') as f:
        config = json.load(f)

    # 基础URL
    baseUrl = "https://flights.ctrip.com/itinerary/api/12808/lowestPrice?"

    # 初始目标价格字典，用于存储每个日期的目标价格
    targetPrices = {date: 0 for date in config["dateToGo"]}
    noTargetPrices = {date: 0 for date in config["dateToGo"]}

    while True:
        # 获取直飞和非直飞的机票信息
        direct_response = requests.get(
            f'{baseUrl}flightWay={config["flightWay"]}&dcity={config["placeFrom"]}&acity={config["placeTo"]}&direct'
            f'=true&army=false')
        non_direct_response = requests.get(
            f'{baseUrl}flightWay={config["flightWay"]}&dcity={config["placeFrom"]}&acity={config["placeTo"]}&army=false')

        if direct_response.status_code != 200 or direct_response.json()["status"] == 2:
            print("无法获取直飞机票信息,等待30s后重新尝试获取")
            for i in range(30):
                print(".", end="")
                time.sleep(1)
            print("\n等待完毕，尝试重新获取机票信息")
            continue

        if non_direct_response.status_code != 200 or non_direct_response.json()["status"] == 2:
            print("无法获取非直飞机票信息,等待30s后重新尝试获取")
            for i in range(30):
                print(".", end="")
                time.sleep(1)
            print("\n等待完毕，尝试重新获取机票信息")
            continue

        # 解析返回的JSON数据
        direct_results = direct_response.json()["data"]["oneWayPrice"][0]
        non_direct_results = non_direct_response.json()["data"]["oneWayPrice"][0]

        for date in config["dateToGo"]:
            if date not in direct_results or date not in non_direct_results:
                print(f"未能找到指定日期{date}的机票价格，请检查日期是否过长或者是过期日期")
            else:
                direct_price = direct_results[date]
                non_direct_price = non_direct_results[date]

                print(f'直飞价格:{direct_price} 非直飞价格:{non_direct_price}')

                if targetPrices[date] == 0:
                    # 第一次获取的价格，分别记录直飞和非直飞的价格
                    print(f'第一次获取{date}的票价，请检查微信推送')
                    push_message(
                        f'第一次推送，{date}的直飞价格{direct_price}，非直飞价格{non_direct_price} - 当前时间:{time.strftime("%H-%M-%S", time.localtime())}',
                        config["SCKEY"])
                    targetPrices[date] = direct_price
                    if noTargetPrices[date] == 0:
                        noTargetPrices[date] = non_direct_price

                else:
                    # 检查价格变化，判断是否超过阈值
                    if abs(direct_price - targetPrices[date]) >= config["priceStep"]:
                        push_message(
                            f'{date}的直飞价格变化超过设定值，当前价格{direct_price}, 变化:{direct_price - targetPrices[date]}, 当前时间:{time.strftime("%H:%M:%S", time.localtime())}',
                            config["SCKEY"])
                        targetPrices[date] = direct_price  # 更新直飞价格

                    if abs(non_direct_price - noTargetPrices[date]) >= config["priceStep"]:
                        push_message(
                            f'{date}的非直飞价格变化超过设定值，当前价格{non_direct_price}, 变化:{non_direct_price - noTargetPrices[date]}, 当前时间:{time.strftime("%H:%M:%S", time.localtime())}',
                            config["SCKEY"])
                        noTargetPrices[date] = non_direct_price  # 更新非直飞价格

        print(f'当前轮次查询完毕，等待{config["sleepTime"]}s后继续查询价格')
        time.sleep(config["sleepTime"])
