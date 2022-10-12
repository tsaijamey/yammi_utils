'''
<模块> OCR识别
文档：https://zhuanlan.zhihu.com/p/384620684
库：pip install cnocr (https://pypi.org/project/cnocr/)
库依赖：https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/，安装第一项（解决问题的文档：https://cloud.tencent.com/developer/article/1997666）
'''

from cnocr import CnOcr
from rich.console import Console

console = Console()

def result_recognition(img_path):
    records = []  # 定义一个空列表，用来存放识别出来的结果
    ocr = CnOcr()
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']
    try_ = 1
    try_times = 0
    while try_ == 1 and try_times < 5:
        res = ocr.ocr(img_path)
        # console.print(res)
        for i in range(len(res)):
            if res[i]['text'] in items:
                if ' ' not in res[i+1]['text']:
                    time = res[i+1]['text'][:10] + ' ' + res[i+1]['text'][-8:]
                else:
                    time = res[i+1]['text']
                single_record = [res[i]['text'], time]    #res[i]对应物品名称，res[i+1]对应其回合时间
                records.append(single_record)
            elif '萨克斯风' in res[i]['text']:
                time = res[i]['text'][4:]
                single_record = ['萨克斯风', time]
                records.append(single_record)

        if len(records) > 4:
            records.remove(records[-1])

        for each in records:
            try_ = 0
            if len(each[0]) <= 1 or len(each[1]) <= 1:
                try_ = 1
                try_times += 1
                console.print("发现识别错误")
                console.print(f"当前错误记录：{records}")
    
    console.print(f"识别结果：{records}")
    return records

def button_recognition(img_path):
    ocr = CnOcr()
    res = ocr.ocr(img_path)
    for each in res:
        if each['text'] == '寻宝记录':
            position = each['position'].tolist()
            break
        else:
            position = []

    if position != []:
        click_position = [position[0][0]+10, position[0][1]+10]
        return click_position
    else:
        return '错误：未找到寻宝记录'

def num_recognition(img_path):
    ocr = CnOcr(cand_alphabet='12345678')
    res = ocr.ocr(img_path)
    return res


# print(button_recognition("D:\OneDrive\Work\Kingdom\code\screenshot.bmp"))