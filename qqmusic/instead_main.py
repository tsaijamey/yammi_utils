'''新版的主程序
'''


# 引用库
from base64 import encode
from rich.console import Console
from rich.theme import Theme
console = Console(theme=Theme({
    "pre": "bold purple blink",  # predict
    "re": "cyan bold blink",   # result
    "st": "#e3e3e3",  # statement
    "wa": "red bold",   # warning
    }))
import time
import datetime
import os


# 自定义库
import instead_lib as inlib

# 预设变量
DIR = os.path.dirname(__file__)


if __name__ == '__main__':
    
    try:
        # 初始化时间
        inlib.screenshot_via_adb()
        # 返回值是 [[名称] , [[时间, 时间戳]]]
        recent_result = inlib.treasure_result_ocr(DIR + './img/shot.png')
        start_time = recent_result[1][0][1]
        
        total = 4
        item_history = []
        time_history = []
        record_history = []
        for each in recent_result[0]:
            item_history.insert(0, each)
        
        for each in recent_result[1]:
            time_history.insert(0,each[0])

        r = open(DIR+'./auto.csv', 'a', encoding='utf8')
        for i in range(4):
            record_history.append([time_history[i],item_history[i]])
            r.write(time_history[i]+','+item_history[i]+'\n')
        r.close()
        console.print('[st]最新记录：[/st]')
        console.print(record_history[-5:])
        total = 4

        while True:
            inlib.compare_time(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)) , 58)
            start_time += 58
            inlib.screenshot_via_adb()

            # 返回值是 [[名称] , [[时间, 时间戳]]]
            recent_result = inlib.treasure_result_ocr(DIR + './img/shot.png')
            if len(record_history) > 20:
                record_history.pop(0)
            record_history.append([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)),recent_result[0][0]])
            r = open(DIR+'./auto.csv', 'a', encoding='utf8')
            r.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)) + ',' + recent_result[0][0] + '\n')
            r.close()
            console.print('[st]最新记录：[/st]')
            console.print(record_history[-5:])
            total += 1
            console.print(f'总数：{total}')

    except Exception as e:
        console.print(e)