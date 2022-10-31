import os
import time
from instead_lib import check_screen_via_adb


while True:
    t = check_screen_via_adb()    
    if 'com.tencent.qqmusic.business.live.ui.HalfScreenWebViewActivity' in t:
        print('Status is OK,' , t)
    else:
        print('Wrong status.')
    time.sleep(10)