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

read_list = []
console = Console()
save_list = []

def read_clipboard():
    text = clipboard.paste()
    return text

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
    if key == keyboard.Key.f8:
        console.print(save_list)
        clear(save_list)
    elif key == keyboard.Key.esc:
        # Stop listener
        clear(save_list)
        return False
    else:
        append_list(read_list)
        unique(read_list)

def print_list(a_list:list):
    console.print(a_list)

def append_list(a_list:list):
    a_list.append(read_clipboard())

def unique(a_list:list):
    unique_list = []
    for each in a_list:
        if each not in unique_list:
            unique_list.append(each)
    return unique_list

def clear(a_list:list):
    a_list = []
    return True

def save(a_list:list):
    save_list = unique(a_list)


# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()