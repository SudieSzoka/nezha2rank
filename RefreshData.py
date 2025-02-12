import urllib.request
import urllib.error
import json
import time
from datetime import datetime

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
        data["total"] = "{:.2f}".format(round(new_total/10000, 2))
        if exchange_rate is not None:
            data["exchange_rate"] = "{:.2f}".format(round(1/exchange_rate, 2))
        data['update_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')
        
        # 保存数据
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        # 读取票房数据
        file_2 = "全球票房.json"
        with open(file_2, "r",encoding='utf-8') as f:
            data = json.load(f)
        data['哪吒2：魔童闹海']['全球票房'] = int(new_total*10000*exchange_rate)
        # 保存数据
        with open(file_2, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
            
    except Exception as e:
        send_feishu_alert(f"文件操作失败: {str(e)}")

def main():
    # 获取票房数据
    timestamp = int(time.time() * 1000)
    url = f'https://www.zgdypw.cn/data/searchDayBoxOffice.json?timestamp={timestamp}'
    
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                total = data["data"]["top10Films"][0]["filmTotalSales"]
                
                # 获取汇率
                exchange_rate = get_exchange_rate()
                
                # 更新数据文件
                update_data_file(total, exchange_rate)
                
                print(f"更新成功！总票房：{total}，当前汇率：{exchange_rate}")
            else:
                send_feishu_alert(f"票房接口返回错误状态码: {response.status}")
                
    except urllib.error.HTTPError as e:
        send_feishu_alert(f"票房接口HTTP错误: {str(e)}")
    except urllib.error.URLError as e:
        send_feishu_alert(f"票房接口网络错误: {str(e)}")
    except Exception as e:
        send_feishu_alert(f"未知错误: {str(e)}")

if __name__ == "__main__":
    main()