'''新版的主程序
'''
# 引用库
from rich.console import Console
from rich.theme import Theme
console = Console(theme=Theme({
    "pre": "bold purple blink",  # predict
    }))
import time
import os
import traceback
import platform

# 自定义库
import instead_lib as inlib
import instead_buy as by
import pad_control as pdc

import openai
import json

# 预定义变量
DIR = os.path.dirname(__file__)             # 当前文件所在的目录
ITEMS = ['钢琴', '小提琴', '吉他', '贝斯', '架子鼓', '竖琴', '萨克斯风', '圆号']
DICT = {
    '钢琴': '1',
    '小提琴': '2',
    '吉他': '3',
    '贝斯': '4',
    '架子鼓': '5',
    '竖琴': '6',
    '萨克斯风': '7',
    '圆号': '8',
}   
CONFIGS = {
    'bullet':'0',
    'buy':'no',
    'chat':'no',
}

recent_result = []
start_timestamp = 0
item_history = []
time_history = []
records = []
total = 0

predicts = []

openai.api_key = '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'

# 预设变量
DIR = os.path.dirname(__file__)
# 获得当前日期
current_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
if platform.system().lower() == 'windows':
    shot_path = DIR + './img/shot.png'
    record_path = DIR+'./record-' + current_date + '.csv'
    if_buy = DIR+'./if_buy.txt'
    predict_log = DIR + './predict_log_' + current_date + '.csv'
elif platform.system().lower() == 'linux':
    shot_path = DIR + '/img/shot.png'
    record_path = DIR+'/auto2-' + current_date + '.csv'
    if_buy = DIR+'/if_buy.txt'
    predict_log = DIR + '/predict_log_' + current_date + '.csv'


if __name__ == '__main__':
    try:
        pdc.main()
        while True:
            recent_result = []
            while len(recent_result) == 0 or len(recent_result[0]) == 0:
                inlib.screenshot_via_adb('shot.png')
                try:
                    recent_result = inlib.treasure_result_ocr(shot_path)
                    
                except Exception as e:
                    pdc.main()
                    records = []

            # 区分第一次和后面的其他回合
            if start_timestamp == 0:

                # 获取第一次识别结果里的所有结果
                item_history.append(recent_result[0])
                time_history.append(recent_result[1][0])

                # 获得识别结果后，确定 计算时间的时间戳 如何计算
                start_timestamp = recent_result[1][1]
                records.append([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)), recent_result[0]])

                # 循环写入第一次识别的4个结果
                r = open(record_path, 'a', encoding='utf8')
                r.write(time_history[-1]+','+item_history[-1]+'\n')
                r.close()
                total = 1
            else:
                records.append([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)), recent_result[0]])
                if len(records) > 31:
                    records.pop(0)
                r = open(record_path, 'a', encoding='utf8')
                r.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) + ',' + recent_result[0] + '\n')
                r.close()
                total += 1
            
            console.print(f'最新记录：{records[-3:]}，总数：{total}')

            if len(predicts) > 0:
                record_pred = open(predict_log, 'a', encoding='utf8')
                record_pred.write("预测：" + predicts[0][1] + "/" + predicts[1][1] + '。实际结果为：' + records[-1][1] + '\n')
                record_pred.close()

            '''
            当记录数达到达到31时，使用openAI的davanci模型进行预测
            '''
            if len(records) > 5:
                text = ''
                for each in records:
                    text = text + each[0] + ' ' + each[1] + '；'
                text = '有一段格式为“时间-值”的时间序列值如下：' + text + '那么下一个时间点是多少？对应的值如果按照概率排序最有可能是哪些？'
                response = openai.Completion.create(model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=1024)
                x = json.dumps(response['choices'])
                y = json.loads(x)
                predict_str = y[0]["text"]
                predicts = []
                for each in ITEMS:
                    if each in predict_str:
                        get_position = predict_str.find(each)
                        predicts.append([each, get_position])
                        predicts.sort(key=lambda x: x[1], reverse=1)
                print(f'预测结果：{predicts}')

            # 把出货历史，泛化成数字
            nums = ''
            for each in records:
                if each[1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                    nums += '{' + DICT[each[1]] + '}'
                else:
                    nums += DICT[each[1]]
            if len(nums) - nums.count('{') - nums.count('}') > 20:
                if nums[0] == '{':
                    nums = nums[3:]
                else:
                    nums = nums[1:]
            console.print(f'回合记录： {nums}')            

            if total % 200 == 0:
                pdc.main()

            inlib.wait_next(start_timestamp, 58)
            start_timestamp += 58

    except Exception as e:
        print(e,traceback.format_exc())