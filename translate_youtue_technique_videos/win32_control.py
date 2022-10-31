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

虚拟键列表：
http://www.kbdedit.com/manual/low_level_vk_list.html
'''

import win32con, win32gui, win32ui, win32api
import os,time
from rich.console import Console



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

def get_window_size(hwnd):
    x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
    return [x2-x1, y2-y1]

def move_window(hwnd, x, y, n_width, n_height, b_repaint):
    # 补充：参数说明
    # hwnd 窗口句柄
    # x：左上角的x坐标
    # y：左上角的y坐标
    # nWidth：窗口宽度
    # nHeight：窗口高度
    # b_repaint：重绘窗口
    win32gui.MoveWindow(hwnd, x - 7, y - 7, n_width, n_height, b_repaint)

def click(hWnd, x, y):
    lParam = win32api.MAKELONG(x, y)

    win32gui.PostMessage(hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(hWnd, win32con.WM_LBUTTONUP, None, lParam)
    print('点了')
    

if __name__ == '__main__':
    console = Console()
    hwnd = win32gui.FindWindow(None, 'qqmusic')
    console.print(f'[bold purple]窗口句柄为[/bold purple]：[blue]{hwnd}[/blue]')
    background_screenshot(hwnd)
    window_size = get_window_size(hwnd)
    console.print(f'[purple]窗口尺寸为[/purple]：[blue]{window_size}[/blue]')
    move_window(hwnd, 500, 0, window_size[0], window_size[1], True)

    # EnumChildWindows参考来源：https://blog.csdn.net/nongcunqq/article/details/113578739
    child_window = []
    def all_child(hwnd,param):
        child_window.append(hwnd)
    win32gui.EnumChildWindows(hwnd, all_child, None)
    console.print(f'所有的子窗口如下：{child_window}')
    # 实测无用

    x, y = 0, 0
    lParam = win32api.MAKELONG(x, y)
    hwnd1= win32gui.FindWindowEx(hwnd, None, None, None)
    console.print(f'Ex方法找到的子句柄：{hwnd1}')

    while True:    
        win32gui.SendMessage(hwnd1, win32con.WM_LBUTTONDOWN, win32con.VK_LBUTTON, lParam)
        win32gui.SendMessage(hwnd1, win32con.WM_LBUTTONUP, None, lParam)
        x += 1
        y += 1
        lParam = win32api.MAKELONG(x, y)
        print(lParam)
    
    # win32gui.EnumChildWindows(hwnd,)

