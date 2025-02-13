import urllib.request
import urllib.error
import urllib.parse
import json
import time
from datetime import datetime, timedelta  # 添加 timedelta 导入

# 配置文件路径
DATA_FILE = "data.json"
# 飞书机器人Webhook地址（需要替换为实际地址）
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/7906662a-b6bd-4b44-8828-057ab46043f7"

def send_feishu_alert(message):
    """发送飞书警报"""
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "msg_type": "text",
        "content": {
            "text": f"报警：{message}"
        }
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(FEISHU_WEBHOOK, data=data, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print("飞书消息发送失败")
    except Exception as e:
        print(f"飞书消息发送错误: {str(e)}")

def get_exchange_rate():
    """获取人民币兑美元汇率"""
    url = "https://api.exchangerate-api.com/v4/latest/CNY"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data["rates"]["USD"]
    except Exception as e:
        send_feishu_alert(f"汇率接口请求失败: {str(e)}")
        return None

def update_data_file(new_total, exchange_rate):
    """更新数据文件"""
    try:
        # 读取现有数据
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"total": 0, "exchange_rate": 0}
        
        # 更新数据
        data["total"] = "{:.2f}".format(round(new_total, 2))
        if exchange_rate is not None:
            data["exchange_rate"] = "{:.2f}".format(round(1/exchange_rate, 2))
        beijing_time = datetime.utcnow() + timedelta(hours=8)
        data['update_time'] = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存数据
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        # 读取票房数据
        file_2 = "全球票房.json"
        with open(file_2, "r",encoding='utf-8') as f:
            data = json.load(f)
        data['哪吒2：魔童闹海']['全球票房'] = int(new_total*100000000*exchange_rate)
        # 保存数据
        with open(file_2, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
            
    except Exception as e:
        send_feishu_alert(f"文件操作失败: {str(e)}")

def main():
    # 获取票房数据
    timestamp = int(time.time() * 1000)
    url = "https://piaofang.maoyan.com/dashboard-ajax"
    
    try:
        params = {
            "orderType": 0,
            "uuid": "7517ebb7-13b4-4fe0-9476-72b94240f2f8",
            "timeStamp": timestamp,
            "User-Agent": "TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMS4wLjAuMCBTYWZhcmkvNTM3LjM2",
            "index": 563,
            "channelId": 40009,
            "sVersion": 2,
            "signKey": "cdd2683d6b7fc02b618b6020e3de70cf",
            "WuKongReady": "h5"
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,en-GB;q=0.7",
            "Connection": "keep-alive",
            "Cookie": "_lxsdk_cuid=194fd16925bc8-0d099aff7ec1f5-26011851-1fa400-194fd16925bc8; _lxsdk=194fd16925bc8-0d099aff7ec1f5-26011851-1fa400-194fd16925bc8",
            "Referer": "https://piaofang.maoyan.com/dashboard",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "X-FOR-WITH": "l2t4PedxzCv9dfusWCm5mLRqQqg7pvIPnHx2kUdvD8MElRBPmS1nxxN7QOhKPysoKelFKrpEQJvOpdFc5zaMDFRFxeyxJXf8b3RNJbcOYmcc+L/J9sjBKWY8A1nveztFxe8HenKerbrt956/KJfWecgif48+HbQmO7BPLvIpRo8hBeP9Ye6DmGXsxRgW/RPbW0sLJxxLOIAfE/3F+WUJ/K4TLddn3ajpEeOitCqrOCo=",
            "mygsig": '{"m1":"0.0.2","m2":0,"ms1":"55f2ff818bd5393f6224d711e3cac87e","ts":1739412908971}',
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not=A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }

        # 将参数编码为URL查询字符串
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"

        # 创建请求对象
        req = urllib.request.Request(full_url, headers=headers)

        # 发送请求并获取响应
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            data = json.loads(response_data)['movieList']['data']['list']

        totalRevenue = ''
        for dt in data:
            if dt['movieInfo']['movieName'] == '哪吒之魔童闹海':
                totalRevenue = dt['sumBoxDesc']
        if totalRevenue != "":
            total = float(totalRevenue[:-1])
            exchange_rate = get_exchange_rate()
            # print(float(totalRevenue[:-1]))
            update_data_file(total, exchange_rate)
        # with urllib.request.urlopen(url) as response:
        #     if response.status == 200:
        #         data = json.loads(response.read().decode())
        #         total = data["data"]["top10Films"][0]["filmTotalSales"]
                
        #         # 获取汇率
        #         exchange_rate = get_exchange_rate()
                
        #         # 更新数据文件
        #         update_data_file(total, exchange_rate)
                
        #         print(f"更新成功！总票房：{total}，当前汇率：{exchange_rate}")
        #     else:
        #         send_feishu_alert(f"票房接口返回错误状态码: {response.status}")
                
    except urllib.error.HTTPError as e:
        send_feishu_alert(f"票房接口HTTP错误: {str(e)}")
    except urllib.error.URLError as e:
        send_feishu_alert(f"票房接口网络错误: {str(e)}")
    except Exception as e:
        send_feishu_alert(f"未知错误: {str(e)}")

if __name__ == "__main__":
    main()
