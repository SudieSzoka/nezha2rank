import pandas as pd
import json

file = '全球票房.xlsx'
df = pd.read_excel(file)

# 遍历df，转为json,json的key 为“中文”列的内容，value为该行的所有内容
def getJsonArray():
    data = {}
    for i in range(len(df)):
        row = df.iloc[i]
        data[row['中文名']] = row.to_dict()
    return data
if __name__ == '__main__':
    data = getJsonArray()
    with open('全球票房.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(data)
