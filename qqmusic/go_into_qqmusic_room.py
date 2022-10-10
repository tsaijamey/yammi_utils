import control_scrcpy_lib as csl
import os
import pyautogui
import time
import keyboard
import random

dirname_ = os.path.dirname(__file__)
print(dirname_)
hwnd = csl.get_hwd('qqmusic')
csl.find_move_window(hwnd, 0, 0)

# 找图标，如果存在会返回中心坐标[int,int]，如果不存在，会返回[0,0]，所以要判断一下返回的值具体是什么
t = 0
while t < 3:
    app_icon_pos = csl.find_element(hwnd, dirname_+'./qqmusic.png', 0.94)
    if app_icon_pos == [0,0]:
        print("没找到QQ音乐App的图标")
        # 当图标没找到，无论当前屏幕处于什么样的情况，只考虑返回到桌面，所以按scrcpy的快捷键alt+h
        # 这个操作结束后，应该重新寻找qq音乐图标，所以这个段落应该处于循环内
        # 为了避免死循环，考虑只循环有限次数
        keyboard.press_and_release('alt+h, space')
        
        t += 1
    else:
        # 找到并点击qq音乐图标，然后退出循环
        print(f"QQ音乐图标中心点在：{app_icon_pos}")
        (x, y) = app_icon_pos
        time.sleep(.5)
        pyautogui.click(x, y)
        break

if t == 3:
    print("失败于找qq音乐图标的环节，退出运行。")
    exit(-1)

zhibo_icon_1_pos = csl.find_element(hwnd, dirname_+'./zhibo_channel.png', 0.80)
zhibo_icon_2_pos = csl.find_element(hwnd, dirname_+'./zhibo_channel_activated.png', 0.80)
if zhibo_icon_1_pos != [0,0]:
    print(f"直播频道图标中心点在：{zhibo_icon_1_pos}")
    (x, y) = zhibo_icon_1_pos
    pyautogui.moveTo(x, y)
    time.sleep(1)
    pyautogui.click()
elif zhibo_icon_2_pos != [0,0]:
    print(f"直播频道图标中心点在：{zhibo_icon_2_pos}")
    (x, y) = zhibo_icon_2_pos
    pyautogui.moveTo(x, y)
    time.sleep(1)
    pyautogui.click()
    time.sleep(3)
else:
    print('没找到直播频道图标')


hot_channel_pos = csl.find_element(hwnd, dirname_+'./hot_channel.png', 0.80)
if hot_channel_pos != [0,0]:
    (x, y) = hot_channel_pos
    print(f'热门标签的坐标：{x} | {y}')
    if y < 180:
        x_offset = random.random() * 200
        y_offset = random.random() * 200
        x, y = x+int(x_offset), y+int(y_offset)
        print(f'无关注的房间在线，将点击位置：{x} | {y}')
        pyautogui.moveTo(x, y)
        time.sleep(1)
        pyautogui.click()
    else:
        more_room_pos = csl.find_element(hwnd, dirname_+'./more_room.png', 0.80)
        (x, y) = more_room_pos
        x = x - 100
        print(f'有关注的房间在线，将点击位置：{x} | {y}')
        pyautogui.moveTo(x, y)
        time.sleep(1)
        pyautogui.click()

kingdom_pos = csl.find_element(hwnd, dirname_+'./kingdom.png', 0.80)
if kingdom_pos != [0,0]:
    (x, y) = kingdom_pos
    print(f'找到音乐王国入口，将点击位置：{x} | {y}')
    pyautogui.moveTo(x, y)
    time.sleep(1)
    pyautogui.click()