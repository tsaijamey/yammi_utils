'''本脚本主要实施购买动作
'''

import os
import sys
import time

DICT_TEXT = {
    '1'     : '钢琴',
    '2'     : '小提琴',
    '3'     : '吉他',
    '4'     : '贝斯',
}

DICT_POS = {
    '钢琴'      : '360 1570',
    '小提琴'    : '613 1603',
    '吉他'      : '909 1629',
    '贝斯'      : '447 1833',
    '确认使用'  : '855 2200',
    '确认成功'  : '540 1584',
}

if __name__ == '__main__':
    t = len(sys.argv)
     
    # 检查传入的参数数量
    if t > 1:
        # os.popen("adb shell input tap " + DICT_POS['确认成功']).read()
        time.sleep(0.5)
        params = []
        for each in sys.argv:
            params.append(each)

        print(params)

        params.pop(0)
        count = int(params[-1])
        params.pop()
        options = []        
        for each in params:
            if DICT_TEXT[each]:
                options.append(DICT_TEXT[each])
        
        print(options)
        for each in options:
            
            for i in range(count):
                os.popen("adb shell input tap " + DICT_POS[each]).read()
        
        time.sleep(0.5)
        os.popen("adb shell input tap " + DICT_POS['确认使用']).read()
    else:
        os.popen("adb shell input tap " + DICT_POS['确认成功']).read()