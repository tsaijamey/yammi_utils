import pretty_errors
pretty_errors.configure(
 separator_character = '*',
 filename_display    = pretty_errors.FILENAME_EXTENDED,
 line_number_first   = True,
 display_link        = True,
 lines_before        = 5,
 lines_after         = 2,
 line_color          = pretty_errors.RED + '> ' + pretty_errors.default_config.line_color,
 code_color          = '  ' + pretty_errors.default_config.line_color,
 truncate_code       = True,
 display_locals      = True
 )
pretty_errors.blacklist('c:/python310')

import os
import control_scrcpy_lib as csl
import pyautogui
import time
import win32gui,win32ui,win32con
from ocr import result_recognition

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
        time.sleep(1)
        pyautogui.click()
        time.sleep(3)
        
        # 为识别结果进行的截图，存为同目录下的screenshot.bmp
        background_screenshot(hwnd)

        records = result_recognition(dirname_+'./screenshot.bmp')
    
        # 返回无记录的界面
        kingdom_title_pos = csl.find_element(hwnd, dirname_+'./kingdom_title.png', 0.80)
        if kingdom_title_pos != [0,0]:
            (x, y) = kingdom_title_pos
            pyautogui.moveTo(x, y)
            time.sleep(1)
            pyautogui.click()
            time.sleep(3)
        print(records)
        name = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯','圆号']
        result = name.index(records[0][0]) + 1

    return [str(result), records[0][1]]

    

if __name__ == '__main__':
    dirname_ = os.path.dirname(__file__)
    hwnd = csl.get_hwd('qqmusic')

    # 循环记录
    while True:
        record_button_pos = csl.find_element(hwnd, dirname_+'./find_treasure_button.png', 0.80)
        if record_button_pos != [0,0]:
            (x, y) = record_button_pos
            pyautogui.moveTo(x, y)
            time.sleep(1)
            pyautogui.click()
            time.sleep(3)
            
            # 为识别结果进行的截图，存为同目录下的screenshot.bmp
            background_screenshot(hwnd)

            records = result_recognition(dirname_+'./screenshot.bmp')
        
            # 返回无记录的界面
            kingdom_title_pos = csl.find_element(hwnd, dirname_+'./kingdom_title.png', 0.80)
            if kingdom_title_pos != [0,0]:
                (x, y) = kingdom_title_pos
                pyautogui.moveTo(x, y)
                time.sleep(1)
                pyautogui.click()
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