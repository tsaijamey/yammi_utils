'''测试通过win32库，从后台像窗口发送信息
文档:           https://learncodebygaming.com/blog/how-to-send-inputs-to-multiple-windows-and-minimized-windows-with-python
虚拟键：        http://www.kbdedit.com/manual/low_level_vk_list.html
用到的Sched2    https://pypi.org/project/sched2/，一个循环事件调度器
'''

import sched
from time import sleep, time
import win32gui, win32ui, win32con, win32api

import os
import control_scrcpy_lib as csl

def make_pycwnd(hwnd):       
        PyCWnd = win32ui.CreateWindowFromHandle(hwnd)
        return PyCWnd

def press(pycwnd):
        pycwnd.SendMessage(win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        pycwnd.SendMessage(win32con.WM_KEYUP, win32con.VK_RETURN, 0)

def f_click(pycwnd,x,y):
        lParam = y | x
        pycwnd.SendMessage(win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        pycwnd.SendMessage(win32con.WM_LBUTTONUP, 0, lParam)


VK_KEY_H        = 0x48
VK_KEY_ALT      = 0xA4
dirname_ = os.path.dirname(__file__)
hwnd = csl.get_hwd('qqmusic')
pycwnd = make_pycwnd(hwnd)
win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, VK_KEY_ALT, 0)
win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, VK_KEY_H, 0)
win32api.SendMessage(hwnd, win32con.WM_KEYUP, VK_KEY_ALT, 0)
win32api.SendMessage(hwnd, win32con.WM_KEYUP, VK_KEY_H, 0)