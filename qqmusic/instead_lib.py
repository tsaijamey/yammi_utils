from datetime import datetime
import os
import time
from rich.console import Console
from rich.theme import Theme
console = Console(theme=Theme({
    "pre": "bold purple blink",  # predict
    "re": "cyan bold blink",   # result
    "st": "#e3e3e3",  # statement
    "wa": "red bold",   # warning
    }))

from cnocr import CnOcr
import re


from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from pandas import DataFrame, array
from numpy import *
import joblib


def screenshot_via_adb(file_name):
    '''通过adb让设备截屏并传输回脚本相对路径下的img目录
    '''
    DIR = os.path.dirname(__file__)
    os.popen("adb shell input tap 1067 627").read()
    time.sleep(3)
    os.popen("adb shell screencap -p /storage/emulated/0/Download/"+file_name).read()
    console.print(os.popen("adb pull /storage/emulated/0/Download/"+ file_name + ' ' + DIR + './img/' + file_name).read())
    os.popen("adb shell input tap 147 415").read()

def treasure_result_ocr(file_path:str) -> list:
    '''寻宝记录进行ocr识别
    输入：文件路径
    输出：list
    '''
    ocr = CnOcr()
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']
    ocr_list = ocr.ocr(file_path)
    name_list = []
    time_list = []
    treasure_result = []
    for i in range(len(ocr_list)):
        ocr_list[i]['text'] = ocr_list[i]['text'].replace('O','0')
        
        for item in items:            
            name_ = re.findall(item, ocr_list[i]['text'])
            if len(name_) == 1:
                # print(ocr_list[i])
                name_list.append(name_[0])

        t = re.findall(r'\d{1,4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}', ocr_list[i]['text'])
        if len(t) == 1:
            # print(ocr_list[i])
            time_ = time.strptime(t[0], "%Y-%m-%d %H:%M:%S")
            time_stamp = int(time.mktime(time_))
            time_list.append([t[0], time_stamp])
            
    treasure_result.append(name_list)
    treasure_result.append(time_list)
    
    return_result = [treasure_result[0][0],treasure_result[1][0]]
    # console.print(return_result)

    return return_result

def interface_ocr(file_path:str) -> list:
    ocr = CnOcr()
    ocr_list = ocr.ocr(file_path)
    text_list = []
    position_list = []
    for i in range(len(ocr_list)):
        print(ocr_list[i])
        text_list.append(ocr_list[i]['text'])

def wait_next(start_time:datetime,time_gap:int):
    '''对比输入的时间，等待58秒后的下一回合
    '''
    last_record_timearray = time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    last_record_timeStamp = int(time.mktime(last_record_timearray))
    latest_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(last_record_timeStamp + 58))
    console.print(f'[st]下回合时间：[/st][pre]{latest_time}[/pre]')
    while int(time.time()) <= last_record_timeStamp + time_gap:
        if last_record_timeStamp + time_gap - int(time.time()) < 3:
            console.print(f"倒计时：[re]{last_record_timeStamp + time_gap - int(time.time())}[/re]秒")
        time.sleep(1)

def item_sum(item_record:list) -> list[int]:
    '''统计输入的物品列表中，各物品总数
    '''
    dict = ['钢琴', '小提琴', '吉他', '贝斯', '架子鼓', '竖琴', '萨克斯风', '圆号']
    item_merge = []
    counter = []

    # 输入的列表是 [时间,物品] 把物品抽离出来，合并到单独的列表
    for each in item_record:
        item_merge.append(each[1])
    # 按照
    for each in dict:
        counter.append(item_merge.count(each))
    return counter

def item_offset(item_counter:list) -> list[float]:
    '''
    输入：乐器数量统计列表，形如：[20, 20, 19, 19, 4, 2, 1, 0]，左右对应顺序 = 钢琴->圆号
    输出：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->圆号
    '''
    rates = [0.200, 0.200, 0.200, 0.200, 0.091, 0.046, 0.037, 0.026]
    all = sum(item_counter)
    offset = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    for i in range(8):
        offset[i] = round(100*(item_counter[i]/all - rates[i]), 2)

    return offset

def position_sorted(offset:list,counter:list) -> list[str,int]:
    '''
    输入：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->圆号
    输出：[乐器编号, 偏移值] 的2d数组，形如：[[大, y], [大, y], [小, y], [小, y], [小, y], [小, y], [大, y], [大, y]]
    输出的排序：[7,6,4,1,2,3,5,8]，左右侧之和都是18
    '''
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']
    input_sort_small = [list(t) for t in zip(items[0:4],counter[0:4],offset[0:4],[0,0,0,0],[0,0,0,0])]
    input_sort_big = [list(t) for t in zip(items[4:8],counter[4:8],offset[4:8],[0,0,0,0],[0,0,0,0])]
    input_sort_small.sort(key=lambda x: x[2], reverse=1)
    input_sort_big.sort(key=lambda x: x[2], reverse=1)
    
    small   = [3,4,5,6]
    big     = [1,2,7,8]

    for i in range(4):
        input_sort_small[i][3] = small[i]
        input_sort_big[i][3] = big[i]

    input_sort = input_sort_small + input_sort_big
    input_sort.sort(key=lambda x: x[3], reverse=1)

    return input_sort

def random_forest_clf_train(train_set:DataFrame,dir_name:str,column_name:str):
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    model = RandomForestClassifier(n_estimators=300, max_leaf_nodes=20, n_jobs=-1)
    model.fit(X.values, y.values)

    joblib.dump(model, dir_name+"./model/rf_clf.m")

def load_rf_clf_model(model_path:str, predict_data):
    clf = joblib.load(model_path)
    rnd_clf_prediction_proba = clf.predict_proba([predict_data]).tolist()[0]

    # 提取随机森林投票的标签  clf.classes_
    labels_list = []
    for each in clf.classes_:
        labels_list.append(each)
    
    proba_list = []
    for each in rnd_clf_prediction_proba:
        proba_list.append(round(each,2))
   
    output_list = list(t for t in zip(labels_list, proba_list))
    output_list.sort(key=lambda x: x[1],reverse=1)

    # 返回值的形式：
    # return [rnd_clf_prediction.tolist()[0], rnd_clf_prediction_proba.tolist()[0]]
    return output_list


def random_forest_reg_train(train_set:DataFrame,dir_name:str,column_name:str):
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    model = RandomForestRegressor(n_estimators=300, criterion='mse', max_leaf_nodes=20, n_jobs=1)
    model.fit(X.values, y.values)

    joblib.dump(model, dir_name+"./model/rf_reg.m")


def load_rf_reg_model(model_path:str, predict_data):
    reg = joblib.load(model_path)
    prediction = reg.predict([predict_data])
    
    return prediction