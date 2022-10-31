'''准备工作
把转录文本从Youtube视频上复制下来，存到transcrpit.txt文件
'''


import os
import pyautogui
from rich.console import Console

console = Console()
DIR = os.path.dirname(__file__)
print(DIR+'\\transcript.txt')
text_content = open(DIR+'\\transcript.txt','r', encoding='utf8')

content_list = []
for line in text_content:
    line = line.strip()
    content_list.append(line)


'''
在已经存了内容的列表中，格式是：时间、英文内容、时间。  
需要辨别时间格式，遇到这类格式就跳过。  
1. 时间格式，根据实际情况，分为2种，一种是只有分秒的时间，另一种是带小时的时间。  
2. 带小时的时间是包含了分秒格式的，所以，只需要检查分秒。

如果不是时间格式的，说明是内容，对应的内容去Deepl.com进行翻译  
把翻译的内容存下来。  

最后需要按照时间点，存储所有的翻译内容。  
所以首先要从原有的数据中提取出时间点来，与翻译结果合并为一个列表。  
'''

import re

transcript_text = []
time_node_list = []
for each in content_list:
    m_s = re.findall(r'\d{1,2}:\d{1,2}', each)
    # h_m_s = re.findall(r'\d{1,2}:\d{1,2}:\d{1,2}', each)
    if len(m_s) > 0:
        time_node_list.append(each)
    else:        
        # 确认输出的都是转录的文本了。
        transcript_text.append(each)


console.print(len(transcript_text))


'''
格式化的问题

因为字幕的断句是根据时间轴来的，所以如果我们直接按时间分割去翻译对应的字幕，会出现一些翻译的内容断章取义，从而无法获得最佳的翻译结果。
如果仅仅直白地翻译，那么用Deepl也就没有了意义。

所以我们需要对字幕文件进行一些断句的合并和分割处理。
'''

for i in range(len(transcript_text)):
    if '. ' in transcript_text[i] and transcript_text[i][-1] != '.':
        # print(each)
        pos = transcript_text[i].find('.')
        if round(pos/len(transcript_text[i]), 2) < 0.50:
            sentences = transcript_text[i].split('.')
            transcript_text[i-1] = transcript_text[i-1] + ' ' + sentences[0] + '.'
            sentences.pop(0)
            transcript_text[i] = ''
            for each in sentences:
                transcript_text[i] += each
        elif round(pos/len(transcript_text[i]), 2) > 0.50:
            sentences = transcript_text[i].split('.')
            transcript_text[i+1] = sentences[-1] + ' ' + transcript_text[i+1]
            sentences = sentences[:-1]
            transcript_text[i] = ''
            for each in sentences:
                transcript_text[i] += each
            transcript_text[i] = transcript_text[i] + '.'


'''
逐个提取transcript_text的内容，去Deepl.com进行翻译。
需要用到的库，是selenium，以及对应的webdriver（此处用的是Google家的Chrome内核驱动）
'''

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 初始化浏览器的设置项，然后初始化一个浏览器对象
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# options.add_argument('headless')
options.add_argument('--window-size=700x700')
options.add_argument("--incognito")

# executable_path 的方法在新版本的selenium里已经被弃用了，会有错误提示：
    ## C:\Users\MagicData\AppData\Local\Temp\ipykernel_1896\126912059.py:12: DeprecationWarning: executable_path has been deprecated, please pass in a Service object
# 解决办法：https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python
# driver = webdriver.Chrome(options=options,executable_path="C:\Python310\chromedriver.exe")
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager


import clipboard
import time
import win32_control as winc

if os.path.exists(DIR+'./attr.txt'):
    read_attr = open(DIR+'./attr.txt', 'r', encoding='utf8')
    for line in read_attr:
        line = line.strip()
        x = int(line)+1
else:
    x = 0

translated = []
driver = webdriver.Chrome(options=options)
driver.get('https://deepl.com')
t = 0



for i  in range(x,len(transcript_text)):
    if t > 9:
        driver.quit()
        time.sleep(1)
        driver = webdriver.Chrome(options=options)
        driver.get('https://deepl.com')
        time.sleep(1)
        
        t = 0
    
    # 等待翻译页面上的输入区域出现
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="panelTranslateText"]/div/div[2]/section[1]/div[3]/div[2]'))
    )
    _, hwnd = winc.get_window_pos('DeepL翻译：全世界最准确的翻译')
    print(hwnd)
    winc.move_window(hwnd, -2200, 0, 800, 600, False)

    exit(-1)

    # 花 3秒检查cookie提示
    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="dl_cookieBanner"]/div/div/div/span/button'))
    )

    if EC.presence_of_element_located((By.XPATH, '//*[@id="dl_cookieBanner"]/div/div/div/span/button')):
        cookies = driver.find_element(By.XPATH, '//*[@id="dl_cookieBanner"]/div/div/div/span/button')
        cookies.click()
        time.sleep(.5)
        console.print('清除cookie按钮')

    clipboard.copy('')
    clipboard.copy(transcript_text[i])
    # 先在输入区域点一下
    input_area = driver.find_element(By.XPATH, '//*[@id="panelTranslateText"]/div/div[2]/section[1]/div[3]/div[2]/textarea')
    input_area.click()
    console.print('点击输入区域')
    time.sleep(.5)
    # 用快捷键的方式输入文本
    pyautogui.keyDown('ctrl')
    pyautogui.press('v')
    pyautogui.keyUp('ctrl')


    time.sleep(.5)
    console.print('粘贴原文')

    
    clipboard.copy('')
    console.print('清空剪贴板')


    RESULT = False
    while RESULT == False:
        try:
            
            # 复制按钮点一下
            xpath = '//*[@id="panelTranslateText"]/div/div[2]/section[2]/div[3]/div[6]/div/div/div[2]/span[2]/span/span/button'
            find_copy_btn = driver.find_element(By.XPATH, xpath)
            find_copy_btn.click()
            console.print('尝试复制译文')

            # 读取剪贴板进行检查。
            text = clipboard.paste()
            if len(text) > 0:
                RESULT = True
                console.print('获得译文')
                f = open(DIR+'./translated.txt', 'a', encoding='utf8')
                f.write(time_node_list[i]+'\n')
                f.write(transcript_text[i]+'\n')
                f.write(text+'\n')
                f.close()

                r = open(DIR+'./attr.txt', 'w', encoding='utf8')
                r.write(str(i) + '\n')
                r.close()
                
                print(f'待翻译的文本：\n\n{transcript_text[i]}\n')
                print(f'译文：\n\n{text}')
                print('*'*50 ,'\n')
                
                # 获取内容后，要记得点一下翻译文本区域的清除
                xpath = '//*[@id="translator-source-clear-button"]'
                clear_src_btn = driver.find_element(By.XPATH, xpath)
                clear_src_btn.click()
                time.sleep(1)
        except Exception as e:
            print(e)

    t += 1