from logging import exception
import os,time,sys,json
import pyautogui as pg
import win32gui, win32ui, win32con
from ocr import result_recognition

def find_treasure_button(img_name):
        hyp_pos = pg.locateOnScreen(dir_name+'./ref_img/'+img_name, confidence=0.8, grayscale=True)
        if str(hyp_pos) == 'None':
            return [0,0]
        else:
            return [hyp_pos[0],hyp_pos[1]]

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

def locate_to_recorder():
    btn_1 = 'find_treasure_button.png'
    btn_2 = 'kingdom.png'
    btn_3 = 'entry.png'

    if find_treasure_button(btn_1) == [0,0]:
        print(f'没找到按钮')
        if find_treasure_button(btn_2) == [0,0]:
            print(f'没找到王国标识')
            if find_treasure_button(btn_3) == [0,0]:
                pass
            else:
                pos = find_treasure_button(btn_3)
                pg.click(pos[0]+10, pos[1]+10)
                time.sleep(5)
                if find_treasure_button(btn_1) != [0,0]:
                    print('进入王国')
                    pos = find_treasure_button(btn_1)
                    pg.click(pos[0]+10, pos[1]+10)
                else:
                    print('茫然不知身在何处')
        else:
            pos = find_treasure_button(btn_2)
            pg.click(pos[0]+10, pos[1]+10)
            time.sleep(5)
            pos = find_treasure_button(btn_1)
            pg.click(pos[0]+10, pos[1]+10)
    else :
        pos = find_treasure_button(btn_1)
        pg.click(pos[0]+10, pos[1]+10)

    time.sleep(5)


# 获取当前脚本的路径
dir_name = os.path.dirname(__file__)
# 自检进入王国
hwnd = win32gui.FindWindow(None, 'qqmusic')
btn_1 = 'find_treasure_button.png'
btn_2 = 'kingdom.png'
btn_3 = 'entry.png'
recoder_l = []
while True:
    locate_to_recorder()
    background_screenshot(hwnd)
    records = result_recognition(dir_name+'./screenshot.bmp')
    
    # 返回无记录的界面
    pos = find_treasure_button(btn_2)
    pg.click(pos[0]+10, pos[1]+10)
    time.sleep(2)
    print(records)
    rfile = open(dir_name+'./recoder.csv', 'a', encoding='utf8')
    rfile.write(records[0][1] + ',' + records[0][0] + '\n')
    rfile.close()
    # 先转换为时间数组
    last_record_timearray = time.strptime(records[0][1], "%Y-%m-%d %H:%M:%S") 
    # 转换为时间戳
    last_record_timeStamp = int(time.mktime(last_record_timearray))

    print(f'最后出货的时间戳为：{last_record_timeStamp}, 目标时间戳：{last_record_timeStamp + 60}')
    present_time = last_record_timeStamp
    while present_time <= last_record_timeStamp + 60:
        present_time = int(time.time())
        print(f"当前时间为：{present_time}, {time.strftime('%Y-%m-%d T%H:%M:%S',time.localtime(present_time))}")
        time.sleep(5)
