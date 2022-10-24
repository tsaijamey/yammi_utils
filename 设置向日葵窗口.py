from window_ import window_control_lib as wcl

current_hwnd = wcl.get_window_handle('Yammi-Dell-1')
if current_hwnd > 0:
    x           = -2220
    y           = 214
    n_width     = -1222+2220
    n_height    = 808-214
    b_repaint   = True
    # rect = win32gui.GetWindowRect(current_hwnd)
    # print(rect)
    wcl.move_window(current_hwnd, x, y, n_width, n_height, b_repaint)
