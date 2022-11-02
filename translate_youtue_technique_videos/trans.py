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

print(transcript_text)

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
options.add_argument('headless')
options.add_argument('--window-size=700x700')
options.add_argument("--incognito")

# executable_path 的方法在新版本的selenium里已经被弃用了，会有错误提示：
    ## C:\Users\MagicData\AppData\Local\Temp\ipykernel_1896\126912059.py:12: DeprecationWarning: executable_path has been deprecated, please pass in a Service object
# 解决办法：https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python
# driver = webdriver.Chrome(options=options,executable_path="C:\Python310\chromedriver.exe")

import clipboard
import time

translated = []

try:
    # 打开deepl.com的链接
    driver = driver = webdriver.Chrome(options=options)
    driver.get('https://deepl.com')
    for i in range(len(transcript_text)):
        # 因为 deepl.com 的防爬虫机制做得很好，所以不要试图通过后端请求的方式去完成翻译，那样即便是一时爽，后面需要迭代的工作会很多，所以还是用前台方式访问，通过它本身的页面功能完成翻译。
        # 要追求低成本地解决问题
        clipboard.copy('')
        clipboard.copy(transcript_text[i])
        input_area = driver.find_element(By.CSS_SELECTOR, 'div.lmt__inner_textarea_container textarea')
        input_area.send_keys(Keys.SHIFT, Keys.INSERT)
        clipboard.copy('')

        # 页面上往往会出现 cookies 确认按钮，这个按钮是欧盟的GDPR法规约束导致的，很多国外的网站上都有，所以尽量等一下
        wait_times = 0
        while wait_times < 3:
            try:
                cookies_btn = driver.find_element(By.CSS_SELECTOR, '#dl_cookieBanner > div > div > div > span > button')
                if cookies_btn.is_enabled():
                    cookies_btn.click()
            except Exception as e:
                # print(e)
                pass

            wait_times += 1
            time.sleep(1)

        # 获取翻译完的结果。
        # 因为采用页面前台进行翻译，所以要充分考虑翻译结果延迟的情况。
        RESULT = False
        while RESULT == False:
            try:
                xpath = '/html/body/div[3]/main/div[5]/div/div[2]/section[2]/div[3]/div[6]/div/div/div[2]/span[2]/span/span/button'
                find_copy_btn = driver.find_element(By.XPATH, xpath)
                find_copy_btn.click()

                # 读取剪贴板进行检查。
                text = clipboard.paste()
                if len(text) > 0:
                    RESULT = True
                    # translated.append(text)
                    f = open(DIR+'./translated.txt', 'a', encoding='utf8')
                    f.write(time_node_list[i]+'\n')
                    f.write(transcript_text[i]+'\n')
                    f.write(text+'\n')
                    f.close()

                    r = open(DIR+'./attr.txt', 'w', encoding='utf8')
                    r.write('i='+ str(i) + '\n')
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

        if i % 10 == 0:
            driver.close()
            time.sleep(5)
            driver = webdriver.Chrome(options=options)
            driver.get('https://deepl.com')
except Exception as e:
    print(e)