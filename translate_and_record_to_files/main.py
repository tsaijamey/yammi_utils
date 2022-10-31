'''一个捕获翻译需求并把翻译结果存到本地文件的后台工具
需求场景：
1. 浏览外文网站时，阅读外文有困难，需要逐字逐句阅读，最好的方法是将其翻译成中文再阅读
2. 采用Microsoft Edge的侧边翻译插件，它支持快捷键，在翻译后可以通过快捷键捕获翻译结果

实现步骤：
1. F7启动读取剪贴板的程序段，全部读到列表里；
2. F8停止读取剪贴板；
3. 轮循一遍列表内容，排除重复的，存成一个文本文档，文档名为剪贴板的第一句话

关键的库：
pynput：用于监听键盘鼠标，同时还能实施键盘和鼠标操作。
Docs：https://pypi.org/project/pynput/
'''


# test
# key_ = ''
# while True:
#     key_ = input('捕获输入')
#     if key_ != '':
#         print(key_)
#         key_ = ''

# 总结：失败，input是个键盘的有效输入，修饰键无法输入。


# keyboard监听方案
# import keyboard
# while True:
#     if keyboard.read_key() == "p":
#         print("You pressed p")
#         break


# pynput监听方案



from pynput import keyboard
import clipboard
from rich.console import Console
import os
import time

console = Console()
read_list = []
start_work = 0

def read_clipboard():
    text = clipboard.paste()
    return text

def append_list():
    global read_list
    read_list.append(read_clipboard())

def unique(a_list:list):
    unique_list = []
    for each in a_list:
        if each not in unique_list:
            unique_list.append(each)
    global read_list
    read_list = unique_list

def print_list(a_list:list):
    console.print('The content to write:')
    console.print(a_list)

def write_file():
    global read_list
    time_stamp = str(int(time.time()))
    DIR = os.path.dirname(__file__)
    w = open(DIR + './auto_' + time_stamp + '.txt', 'w', encoding='utf8')
    for each in read_list:
        w.write(each + '\n')
    w.close()


def clear():
    global read_list
    read_list = []

# 键盘按下监控
def on_press(key):
    try:
        print('Alphanumeric key pressed: {0} '.format(
            key.char))
    except AttributeError:
        print('special key pressed: {0}'.format(
            key))

def on_release(key):
    print('Key released: {0}'.format(
        key))
    global start_work
    if key == keyboard.Key.f7:
        start_work = 1
    if key == keyboard.Key.f8:
        start_work = 0
        print_list(read_list)
        write_file()
        clear()
    elif key == keyboard.Key.esc:
        # Stop listener
        clear()
        return False
    elif start_work == 1 and key != keyboard.Key.f7 and key != keyboard.Key.esc and key != keyboard.Key.f8:
        # 将剪贴板的内容追加到 read_list
        append_list()
        unique(read_list)


# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()