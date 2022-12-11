import os
import time
import platform

POS = {
    'MUSIC':'193 1167',
    'LIVE':'1075 1859',
    'ROOM':'596 987',
    'KD':'894 1816',
    'CHAT':'151 1810',
    'SEND':'1112 1284',
}

def send_home():
    commands = 'adb shell input keyevent 3'
    os.popen(commands).read()

def open_music():
    commands = 'adb shell input tap '+POS['MUSIC']
    os.popen(commands).read()

def kill_music():
    commands = 'adb shell am force-stop com.tencent.qqmusic'
    os.popen(commands).read()

def detect_music():
    if platform.system().lower() == 'windows':
        commands = 'adb shell ps -A | findstr qqmusic'
    elif platform.system().lower() == 'linux':
        commands = 'adb shell ps -A | grep qqmusic'
    if len(os.popen(commands).read()) > 0:
        return True
    else:
        return False

def into_live():
    commands = 'adb shell input tap '+POS['LIVE']
    os.popen(commands).read()

def into_room():
    commands = 'adb shell input tap '+POS['ROOM']
    os.popen(commands).read()

def open_kd():
    commands = 'adb shell input tap '+POS['KD']
    os.popen(commands).read()

def open_chat():
    commands = 'adb shell input tap '+POS['CHAT']
    os.popen(commands).read()

def send_chat():
    commands = 'adb shell input tap '+POS['SEND']
    os.popen(commands).read()



def main():
    # while True:
    if detect_music() == False:
        open_music()
        time.sleep(15)
        into_live()
        time.sleep(5)
        into_room()
        time.sleep(5)
        open_kd()
        time.sleep(5)
    else:
        kill_music()
        time.sleep(2)
        open_music()
        time.sleep(15)
        into_live()
        time.sleep(5)
        into_room()
        time.sleep(5)
        open_kd()
        time.sleep(5)
        