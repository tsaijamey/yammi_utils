'''
<模块> OCR识别
文档：https://zhuanlan.zhihu.com/p/384620684
库：pip install cnocr (https://pypi.org/project/cnocr/)
库依赖：https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/，安装第一项（解决问题的文档：https://cloud.tencent.com/developer/article/1997666）
'''

from cnocr import CnOcr
from rich.console import Console
import os
import pyautogui
import time
import win32gui,win32ui,win32con
from rich.console import Console

# 自定义库
import control_scrcpy_lib as csl

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

def background_screenshot(hwnd):
    wDC = win32gui.GetWindowDC(hwnd)
    x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, x2-x1, y2-y1)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(x2-x1, y2-y1) , dcObj, (0,0), win32con.SRCCOPY)
    dataBitMap.SaveBitmapFile(cDC, os.path.dirname(__file__)+'./img/screenshot.bmp')
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

def get_latest_result(*args):
    dirname_ = os.path.dirname(__file__)
    hwnd = csl.get_hwd('qqmusic')

    # 这里比较容易出错，所以设计成循环检查。
    # 理论上说，运行过程中，app的状态不太会变化。
    record_button_pos = [0,0]
    while record_button_pos == [0,0]:
        record_button_pos = csl.find_element(hwnd, dirname_+'./img/find_treasure_button.png', 0.80)
        if record_button_pos != [0,0]:
            (x, y) = record_button_pos
            csl.pyautogui_click(hwnd,x,y)
            time.sleep(2)
            
            # 为识别结果进行的截图，存为同目录下的screenshot.bmp
            background_screenshot(hwnd)

            try:
                records = result_recognition(dirname_+'./img/screenshot.bmp')
            except Exception as e:
                console.print(e)
                console.print('未检测到数据')
                exit(-1)

            # 返回无记录的界面
            kingdom_title_pos = csl.find_element(hwnd, dirname_+'./img/kingdom_title.png', 0.80)
            if kingdom_title_pos != [0,0]:
                (x, y) = kingdom_title_pos
                csl.pyautogui_click(hwnd,x,y)
                time.sleep(.5)     
            else:
                console.print('界面异常')
                exit(-1)
        
            name = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']
            result = name.index(records[0][0]) + 1

    return [str(result), records[0][1]]

    

if __name__ == '__main__':
    dirname_ = os.path.dirname(__file__)
    hwnd = csl.get_hwd('qqmusic')
    background_screenshot(hwnd)

    # 循环记录
    while True:
        record_button_pos = csl.find_element(hwnd, dirname_+'./img/find_treasure_button.png', 0.80)
        if record_button_pos != [0,0]:
            (x, y) = record_button_pos
            csl.pyautogui_click(hwnd,x,y)
            time.sleep(3)
            
            # 为识别结果进行的截图，存为同目录下的screenshot.bmp
            background_screenshot(hwnd)

            records = result_recognition(dirname_+'./img/screenshot.bmp')
        
            # 返回无记录的界面
            kingdom_title_pos = csl.find_element(hwnd, dirname_+'./img/kingdom_title.png', 0.80)
            if kingdom_title_pos != [0,0]:
                (x, y) = kingdom_title_pos
                csl.pyautogui_click(hwnd,x,y)
                time.sleep(3)
            print(records)

            rfile = open(dirname_+'./recoder.csv', 'a', encoding='utf8')
            rfile.write(records[0][1] + ',' + records[0][0] + '\n')
            rfile.close()
            # 先转换为时间数组
            last_record_timearray = time.strptime(records[0][1], "%Y-%m-%d %H:%M:%S") 
            # 转换为时间戳
            last_record_timeStamp = int(time.mktime(last_record_timearray))

            print(f'最后出货的时间戳为：{last_record_timeStamp}, 目标时间戳：{last_record_timeStamp + 60}\n')
            present_time = last_record_timeStamp
            while present_time <= last_record_timeStamp + 60:
                present_time = int(time.time())
                # print(f"当前时间为：{present_time}, {time.strftime('%Y-%m-%d T%H:%M:%S',time.localtime(present_time))}")
                time.sleep(5)



# print(button_recognition("D:\OneDrive\Work\Kingdom\code\screenshot.bmp"))