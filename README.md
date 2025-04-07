
# 机票价格提醒工具（支持微信提醒）

本工具利用[携程 API](https://github.com/liangen1/-xiechengjipiao_aip)实时监控机票价格，并在价格变化超过设定值时，通过微信推送通知用户。该工具基于 `pushplus` 实现微信消息推送功能。

> **注意**：本工具仅供个人学习和研究使用，禁止用于商业用途。

## 功能特点

- **全新图形界面**：直观易用的中文界面，轻松配置和监控价格变化。
- 支持单程票和往返票的价格监控。
- 实时价格对比，价格变化时自动微信通知提醒。
- 配置简单，支持多日期、多城市监控。
- **配置持久化**：自动保存和加载配置，重启程序不丢失设置。

## 使用方法

### 方法一：直接使用可执行文件（推荐）

1. 下载最新版本的 `default.exe` 文件
2. 双击运行程序
3. 在"配置设置"标签页中输入监控参数
4. 点击"保存配置"按钮保存设置
5. 切换到"价格监控"标签页，点击"开始监控"按钮开始监控价格

### 方法二：从源码运行

1. **环境要求**：  
   本工具依赖 `Python 3.6` 及以上版本，推荐在 `Python 3.8` 上运行。

2. **下载代码**：  
   克隆或下载本项目代码，并进入对应的目录：

   ```bash
   git clone https://github.com/davidwushi1145/flightAlert.git
   cd flightAlert
   ```

3. **创建虚拟环境**：  
   使用如下命令创建并激活 Python 虚拟环境：

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux / macOS
   venv\Scripts\activate  # Windows
   ```

4. **安装依赖包**：  
   运行以下命令安装所需依赖包：

   ```bash
   pip install requests pillow tkinter
   ```

5. **运行GUI程序**：  
   配置完成后，运行以下命令启动GUI程序：

   ```bash
   python flight_alert_gui.py
   ```

6. **或者运行命令行版本**：  
   如果需要使用命令行版本，可以编辑 `config.json` 文件后运行：

   ```bash
   python flight_alert.py
   ```

## `config.json` 文件配置说明

- `dateToGo`：需要监控的出发日期（日期格式为 `YYYY-MM-DD`）。
- `placeFrom`：出发城市的机场代码（见下方机场代码表）。
- `placeTo`：到达城市的机场代码（见下方机场代码表）。
- `flightWay`：机票类型，单程票用 `OneWay`，往返票用 `Roundtrip`。
- `sleepTime`：查询间隔时间，单位为秒，推荐设置为 `600` 秒（即十分钟查询一次）。
- `priceStep`：价格变化的阈值，当价格变化超过该值时触发微信提醒。
- `SCKEY`：`pushplus` 的 token，详见[pushplus 文档](https://www.pushplus.plus/doc/)获取方法。

## GUI界面使用说明

### 配置设置页面

在程序的"配置设置"标签页中，你可以设置以下参数：

- **监控日期**：需要监控的出发日期（格式为 `YYYYMMDD`，用逗号分隔多个日期）。
- **出发机场代码**：出发城市的机场代码（见下方机场代码表）。
- **到达机场代码**：到达城市的机场代码（见下方机场代码表）。
- **航程类型**：选择 `Oneway`（单程）或 `Roundtrip`（往返）。
- **检查间隔**：查询间隔时间，单位为秒。
- **价格变动阈值**：价格变化的阈值，当价格变化超过该值时触发微信提醒。
- **PushPlus推送令牌**：`pushplus` 的 token，用于发送微信通知。

完成设置后，点击"保存配置"按钮保存配置。

### 价格监控页面

在"价格监控"标签页中：

1. 点击"开始监控"按钮开始价格监控
2. "当前价格"区域显示最新检测到的价格
3. "活动日志"区域显示程序运行状态和价格变化记录
4. 需要停止监控时，点击"停止监控"按钮

## 机场代码对照表

以下是部分常用城市的机场代码：

| 城市   | 机场代码 | 城市   | 机场代码 |
| ------ | -------- | ------ | -------- |
| 北京   | BJS      | 上海   | SHA      |
| 广州   | CAN      | 深圳   | SZX      |
| 成都   | CTU      | 杭州   | HGH      |
| 武汉   | WUH      | 西安   | SIA      |
| 重庆   | CKG      | 青岛   | TAO      |
| 长沙   | CSX      | 南京   | NKG      |
| 厦门   | XMN      | 昆明   | KMG      |
| 济南   | TNA      | 福州   | FOC      |
| 南昌   | KHN      | 厦门   | XMN      |

更多城市机场代码请参见[完整列表](https://www.iata.org/en/publications/directories/code-search/).

## 注意事项

- 建议监控的日期不要设置太长或已经过期的日期，以免无法获取机票信息。
- `pushplus` 微信推送功能需要在 `pushplus` 平台上注册并获取 `SCKEY`。
- 程序会自动将配置文件保存在用户的 AppData 目录，确保程序在关闭后仍能保留设置。

## 参考项目

- 本工具改进自 [flightAlert](https://github.com/omegatao/flightAlert)

## 版权声明

本程序仅供个人学习研究，禁止用于商业用途。请尊重版权，不得将本工具用于任何违反相关法律法规的行为。

