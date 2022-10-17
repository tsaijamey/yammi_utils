from datetime import datetime
import os
import time
from rich.console import Console
from rich.theme import Theme
console = Console(theme=Theme({
    "pre": "bold purple blink",  # predict
    "re": "cyan bold blink",   # result
    "st": "#e3e3e3",  # statement
    "wa": "red bold",   # warning
    }))

from cnocr import CnOcr
import re


def screenshot_via_adb():
    '''通过adb让设备截屏并传输回脚本相对路径下的img目录
    '''
    DIR = os.path.dirname(__file__)
    os.popen("adb shell input tap 1067 627").read()
    time.sleep(3)
    os.popen("adb shell screencap -p /storage/emulated/0/Download/shot.png").read()
    console.print(os.popen("adb pull /storage/emulated/0/Download/shot.png "+ DIR + './img/shot.png').read())
    os.popen("adb shell input tap 147 415").read()

def treasure_result_ocr(file_path:str) -> list:
    '''寻宝记录进行ocr识别
    输入：文件路径
    输出：list
    '''
    ocr = CnOcr()
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']
    ocr_list = ocr.ocr(file_path)
    name_list = []
    time_list = []
    treasure_result = []
    for i in range(len(ocr_list)):
        for item in items:
            name_ = re.findall(item, ocr_list[i]['text'])
            if len(name_) == 1:
                name_list.append(name_[0])

        t = re.findall(r'\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}', ocr_list[i]['text'])
        if len(t) == 1:
            time_ = time.strptime(t[0], "%Y-%m-%d %H:%M:%S")
            time_stamp = int(time.mktime(time_))
            time_list.append([t[0], time_stamp])
            
    treasure_result.append(name_list)
    treasure_result.append(time_list)
    # console.print(treasure_result)

    return treasure_result

def compare_time(start_time:datetime,time_gap:int):
    '''对比输入的时间，等待58秒后的下一回合
    '''
    last_record_timearray = time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    last_record_timeStamp = int(time.mktime(last_record_timearray))
    latest_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(last_record_timeStamp + 58))
    console.print(f'[st]下回合时间：[/st][pre]{latest_time}[/pre]')
    while int(time.time()) <= last_record_timeStamp + time_gap:
        if last_record_timeStamp + time_gap - int(time.time()) < 6:
            console.print(f"倒计时：[re]{last_record_timeStamp + time_gap - int(time.time())}[/re]秒")
        time.sleep(1)

def item_sum(item_record:list) -> list[int]:
    '''统计输入的物品列表中，各物品总数
    '''
    dict = ['钢琴', '小提琴', '吉他', '贝斯', '架子鼓', '竖琴', '萨克斯风', '圆号']
    item_merge = []
    counter = []

    # 输入的列表是 [时间,物品] 把物品抽离出来，合并到单独的列表
    for each in item_record:
        item_merge.append(each[1])
    # 按照
    for each in dict:
        counter.append(item_merge.count(each))
    return counter

def item_offset(item_counter:list) -> list[float]:
    '''
    输入：乐器数量统计列表，形如：[20, 20, 19, 19, 4, 2, 1, 0]，左右对应顺序 = 钢琴->圆号
    输出：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->圆号
    '''
    rates = [0.200, 0.200, 0.200, 0.200, 0.091, 0.046, 0.037, 0.026]
    all = sum(item_counter)
    offset = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    for i in range(8):
        offset[i] = round(100*(item_counter[i]/all - rates[i]), 2)

    return offset

def position_sorted(offset:list) -> list[str,int]:
    '''
    输入：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->圆号
    输出：[乐器编号, 偏移值] 的2d数组，形如：[[大, y], [大, y], [小, y], [小, y], [小, y], [小, y], [大, y], [大, y]]
    输出的排序：[7,6,4,1,2,3,5,8]，左右侧之和都是18
    '''
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']
    input_sort = [list(t) for t in zip(items[0:8],offset[0:8])]
    input_sort.sort(key=lambda x: x[1], reverse=1)

    return input_sort
