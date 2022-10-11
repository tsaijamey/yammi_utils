import os
import control_scrcpy_lib as csl
import pyautogui
import time
import win32gui,win32ui,win32con
from ocr import result_recognition
from rich.console import Console

console = Console()

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

def get_latest_result():
    dirname_ = os.path.dirname(__file__)
    hwnd = csl.get_hwd('qqmusic')
    record_button_pos = csl.find_element(hwnd, dirname_+'./find_treasure_button.png', 0.80)
    if record_button_pos != [0,0]:
        (x, y) = record_button_pos
        pyautogui.moveTo(x, y)
        time.sleep(.5)
        pyautogui.click()
        time.sleep(2)
        
        # 为识别结果进行的截图，存为同目录下的screenshot.bmp
        background_screenshot(hwnd)

        try:
            records = result_recognition(dirname_+'./screenshot.bmp')
        except Exception as e:
            console.print(e)
            console.print('未检测到数据')
            exit(-1)

        # 返回无记录的界面
        kingdom_title_pos = csl.find_element(hwnd, dirname_+'./kingdom_title.png', 0.80)
        if kingdom_title_pos != [0,0]:
            (x, y) = kingdom_title_pos
            pyautogui.moveTo(x, y)
            time.sleep(.5)
            pyautogui.click()
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