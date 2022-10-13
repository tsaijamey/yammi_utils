from distutils.command.config import config
from kiwisolver import Expression
from sympy import EX
import win32con, win32gui, win32ui, win32api
import pyautogui
from PIL import Image
import time
from rich.console import Console



# 根据窗口标题，获得窗口句柄
def get_hwd(title:str) -> str:
    hwnd = win32gui.FindWindow(0, title)
    return hwnd

# 找到窗口并移动到指定位置
def find_move_window(hwnd:int, pos_x:int, pos_y:int):
    x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
    win32gui.MoveWindow(hwnd, pos_x, pos_y, x2-x1, y2-y1, True)

# 找到窗口中的指定资源，返回资源的屏幕位置
def find_element(hwnd:int, element_path:str, conf:float) -> list:
    '''
    :hwnd:              窗口句柄，用于确保窗口处于激活状态
    :element_path:      元素的图片路径
    :conf:              找图调用opencv内置模型所需的置信度
    '''
    console = Console()
    # 首先需要激活这个窗口，否则pyautogui无法找到。它只能找到屏幕顶层的内容。
    # 激活后要等1-2秒，因为激活的动作有时间延迟。
    # win32gui.ShowWindow(hwnd,1)
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(2)
        element = Image.open(element_path)
        locs_list = list(pyautogui.locateAllOnScreen(element, confidence=conf))
        time.sleep(.5)
        # win32gui.ShowWindow(hwnd,0)

        # 这里要判断找的结果是否存在，因为可能返回空值
        if len(locs_list) > 0:
            left, top, width, height = locs_list[0][0], locs_list[0][1], locs_list[0][2], locs_list[0][3]
            return [left+int(width/2), top+int(height/2)]
        else:
            return [0,0]
    except Exception as e:
        console.print(f"{'*'*20} Error Info {'*'*20}\n{e}\n{'*'*20} Info End {'*'*20}")

def pyautogui_click(hwnd,x,y):
    # win32gui.ShowWindow(hwnd,1)
    # win32gui.SetForegroundWindow(hwnd)

    pyautogui.moveTo(x, y)
    time.sleep(.5)
    pyautogui.click()

    # win32gui.ShowWindow(hwnd,0)