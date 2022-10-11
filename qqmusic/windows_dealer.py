'''
资料：
How To Send Inputs to Multiple Windows / Minimized Windows with Python. Or Die Trying：
https://www.youtube.com/watch?v=J3fatZ2OVIU

Python win32api SendMesage：
https://stackoverflow.com/questions/14788036/python-win32api-sendmesage

Is there a way to send a click event to a window in the background in python?
https://stackoverflow.com/questions/59285854/is-there-a-way-to-send-a-click-event-to-a-window-in-the-background-in-python

How to send keystrokes to a window?
https://stackoverflow.com/questions/2113950/how-to-send-keystrokes-to-a-window

激活窗口并截图
https://zhuanlan.zhihu.com/p/97574557
'''

import win32con, win32gui, win32ui, win32api
import os
from PIL import ImageGrab
import time
import control_scrcpy_lib as csl
from ocr import result_recognition


def get_window_pos(name):
    name = name
    handle = win32gui.FindWindow(0, name)

    # 获取窗口句柄
    if handle == 0:
        return None
    else:
        return win32gui.GetWindowRect(handle), handle

# (x1, y1, x2, y2), handle = get_window_pos('M2102K1C')

# 设为高亮
def activate_window(handle):
    win32gui.SetForegroundWindow(handle)

# 截图
def grab_png(x1,y1,x2,y2):
    img_ready = ImageGrab.grab((x1, y1, x2, y2))
    path =  os.path.dirname(__file__) + './ocr.png'
    img_ready.save(path)
    return True

# 【不能最小化】后台捕获窗口并截图：https://stackoverflow.com/questions/53551676/python-screenshot-of-background-inactive-window
def background_screenshot(hwnd):
    wDC = win32gui.GetWindowDC(hwnd)
    x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, x2-x1, y2-y1)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(x2-x1, y2-y1) , dcObj, (0,0), win32con.SRCCOPY)
    dataBitMap.SaveBitmapFile(cDC, os.path.dirname(__file__)+'./screenshot.bmp')
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

def move_window(hwnd, x, y, n_width, n_height, b_repaint):
    win32gui.MoveWindow(hwnd, x - 7, y - 7, n_width, n_height, b_repaint)

def click(hWnd, x, y):
    x1, y1, x2, y2 = win32gui.GetWindowRect(hWnd)
    # move_window(hWnd,0,0,x2-x1,y2-y1,True)
    lParam = win32api.MAKELONG(x, y)

    # hWnd1= win32gui.FindWindowEx(hWnd, None, None, None)
    # win32gui.PostMessage(hWnd1, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    # win32gui.PostMessage(hWnd1, win32con.WM_LBUTTONUP, None, lParam)

    win32gui.PostMessage(hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(hWnd, win32con.WM_LBUTTONUP, None, lParam)
    print('点了')





hwnd = win32gui.FindWindow(None, 'qqmusic')

dirname_ = os.path.dirname(__file__)
record_button_pos = csl.find_element(hwnd, dirname_+'./find_treasure_button.png', 0.80)
if record_button_pos != [0,0]:
    (x, y) = record_button_pos
    
    time.sleep(2)
else:
    print('没找到')
    exit(-2)


print(records)
exit(-1)

# 先转换为时间数组
last_record_timearray = time.strptime(records[0][1], "%Y-%m-%d %H:%M:%S") 
# 转换为时间戳
last_record_timeStamp = int(time.mktime(last_record_timearray))
print(f'最后的时间记录为：{last_record_timeStamp}')


present_time = int(time.time())
print(f'当前时间为：{present_time}')
