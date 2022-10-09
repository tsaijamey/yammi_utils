import win32con, win32gui, win32ui, win32api
import pyautogui
from PIL import Image

# 根据窗口标题，获得窗口句柄
def get_hwd(title:str) -> str:
    hwnd = win32gui.FindWindow(0, title)
    return hwnd

# 找到窗口并移动到指定位置
def find_move_window(hwnd:str, pos_x:int, pos_y:int):
    x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
    win32gui.MoveWindow(hwnd, pos_x, pos_y, x2-x1, y2-y1, True)

# 找到窗口中的指定资源，返回资源的屏幕位置
def find_element(hwnd:str, element_path:str) -> list[int,int]:
    '''
    :hwnd:              窗口句柄
    :element_path:      元素的图片路径
    '''
    element = Image.open(element_path)
    locs_list = list(pyautogui.locateAllOnScreen(element, confidence=0.82))
    return locs_list

# 点击指定位置
def click_screen(position:list[int,int]):
    pass