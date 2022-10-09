import control_scrcpy_lib as csl

hwnd = csl.get_hwd('M2102K1C')
csl.find_move_window(hwnd, 0, 0)

print(hwnd)