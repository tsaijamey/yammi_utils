import win32gui

def get_window_handle(name):
    '''通过名字获得窗口句柄
    入参为窗口名字，默认为None，如果None，则返回当前窗口；非None，则找这个名字的窗口
    '''
    if name == None:
        hwnd = win32gui.GetForegroundWindow()
        print(f'激活的窗口句柄为：{hwnd}')
    else:
        hwnd = win32gui.FindWindow(0, name)
        if hwnd == 0:
            print(f'窗口名字可能错了？没找到')
        else:
            print(f'查找的窗口句柄为：{hwnd}')

    return hwnd
   
def move_window(current_hwnd, x, y, n_width, n_height, b_repaint):
    win32gui.MoveWindow(current_hwnd, x, y, n_width, n_height, b_repaint)

'''测试区域
'''

current_hwnd = get_window_handle('Yammi-Dell-1')
if current_hwnd > 0:
    x           = -2220
    y           = 214
    n_width     = -1222+2220
    n_height    = 808-214
    b_repaint   = True
    # rect = win32gui.GetWindowRect(current_hwnd)
    # print(rect)
    win32gui.MoveWindow(current_hwnd, x, y, n_width, n_height, b_repaint)
