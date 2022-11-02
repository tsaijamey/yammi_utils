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
    '钢琴'      : '301 990',
    '小提琴'    : '580 1018',
    '吉他'      : '919 1047',
    '贝斯'      : '393 1288',
    '确认使用'  : '935 1685',
    '确认成功'  : '611 1352',
    '完成'      : '1129 1290',
}
KEY_E = {
    '0' : '7',
    '1' : '8',
    '2' : '9',
    '3' : '10',
    '4' : '11',
    '5' : '12',
    '6' : '13',
    '7' : '14',
    '8' : '15',
    '9' : '16',

}

def close_popup():
    os.popen("adb shell input tap " + DICT_POS['确认成功']).read()

def buy(a,b,num):
    options = [a,b]
    count = num
    for each in options:
        os.popen("adb shell input tap " + DICT_POS[each]).read()
        time.sleep(1)
        for n in count:
            os.popen("adb shell input keyevent " + KEY_E[n]).read()
            time.sleep(0.5)
        os.popen("adb shell input tap " + DICT_POS['完成']).read()
        time.sleep(1)
    time.sleep(0.5)
    os.popen("adb shell input tap " + DICT_POS['确认使用']).read()

# if __name__ == '__main__':
#     t = len(sys.argv)
     
#     # 检查传入的参数数量
#     if t > 1:
#         # os.popen("adb shell input tap " + DICT_POS['确认成功']).read()
#         time.sleep(0.5)
#         params = []
#         for each in sys.argv:
#             params.append(each)

#         print(params)

#         params.pop(0)
#         count = str(params[-1])
#         params.pop()
#         options = []        
#         for each in params:
#             if DICT_TEXT[each]:
#                 options.append(DICT_TEXT[each])
        
#         print(options)
#         for each in options:
#             os.popen("adb shell input tap " + DICT_POS[each]).read()
#             time.sleep(1)
#             for num in count:
#                 os.popen("adb shell input keyevent " + KEY_E[num]).read()
#                 time.sleep(0.5)
#             os.popen("adb shell input tap " + DICT_POS['完成']).read()
#             time.sleep(1)
#         time.sleep(0.5)
#         os.popen("adb shell input tap " + DICT_POS['确认使用']).read()
#     else:
#         close_popup()