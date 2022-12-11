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
import platform
import requests
# Python源码资料电子书领取群 279199867

def send_wechat(msg_title,msg):
    token = 'f848a62a0c7541fd8519247fd3f139f9' #前边复制到那个token
    title = msg_title
    content = msg
    template = 'html'
    topic = '1022111101'
    url = f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}&topic={topic}"
    r = requests.get(url=url)

def send_wechat_self(msg):
    token = 'f848a62a0c7541fd8519247fd3f139f9'#前边复制到那个token
    title = 'Music Kingdom'
    content = msg
    template = 'html'
    url = f"https://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}"
    r = requests.get(url=url)

# def init_stock():
#     stock   = 1
#     times   = 1
#     rate    = 0.20
#     top     = stock
#     for i in range(times):
#         top = int(top/rate)

#     return stock, times, rate, top

def init_stock():
    stock   = 2
    times   = 3
    rate    = 0.20
    top     = stock
    for i in range(times):
        top = int(top/rate)

    return stock, times, rate, top



def screenshot_via_adb(file_name):
    '''通过adb让设备截屏并传输回脚本相对路径下的img目录
    '''
    DIR = os.path.dirname(__file__)
    os.popen("adb shell input tap 1067 627").read()
    time.sleep(3)
    os.popen("adb shell screencap -p /storage/emulated/0/Download/"+file_name).read()
    if platform.system().lower() == 'windows':
        download_path = DIR + './img/'
    elif platform.system().lower() == 'linux':
        download_path = DIR + '/img/'
    console.print(os.popen("adb pull /storage/emulated/0/Download/"+ file_name + ' ' + download_path + file_name).read())
    os.popen("adb shell input tap 147 415").read()

def getshot_via_adb(file_name_1,file_name_2):
    '''通过adb让设备截屏并传输回脚本相对路径下的img目录
    '''
    DIR = os.path.dirname(__file__)
    # os.popen("adb shell input tap 1067 627").read()
    # time.sleep(3)
    # os.popen("adb shell screencap -p /storage/emulated/0/Download/"+file_name).read()
    console.print(os.popen("adb pull /storage/emulated/0/Download/"+ file_name_1 + ' ' + DIR + './img/' + file_name_2).read())
    # os.popen("adb shell input tap 147 415").read()

def check_screen_via_adb():
    if platform.system().lower() == 'windows':
        return os.popen("adb shell dumpsys window windows | findstr mCurrentFocus").read()
    elif platform.system().lower() == 'linux':
        return os.popen("adb shell dumpsys window windows | grep mCurrentFocus").read()

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

def wait_next(start_time,time_gap:int):
    '''对比输入的时间，等待58秒后的下一回合
    '''

    latest_time = start_time + time_gap
    console.print(f'[st]下回合时间：[/st][pre]{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(latest_time))}[/pre]')
    while int(time.time()) <= latest_time:
        if latest_time - int(time.time()) < 3:
            console.print(f"倒计时：[re]{latest_time - int(time.time())}[/re]秒")
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

def if_item_sum_balance(counter:list):
    container = []
    for each in counter[:4]:
        if each not in container:
            container.append(each)
    if len(container) == 4:
        return False
    else:
        return True

def if_item_sum_middle_balance(counter:list):
    container = []
    for each in counter:
        container.append(each)
    container = container[:4]
    container.sort(reverse=0)
    if container[1] == container[2]:
        return True
    else:
        return False

def item_sum_V(item_record:list) -> list[int]:
    '''统计输入的物品列表中，各物品总数
    其中，架子鼓、竖琴、萨克斯风、圆号视为一个物品
    最终输出为：[a,b,c,d,e]
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
    
    big = sum(counter[4:])
    counter = counter[:4]
    counter.append(big)
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

def item_offset_V(item_counter:list) -> list[float]:
    '''
    输入：乐器数量统计列表，形如：[20, 20, 19, 19, 19]，左右对应顺序 = 钢琴->大
    输出：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->大
    '''
    rates = [0.200, 0.200, 0.200, 0.200, 0.200]
    all = sum(item_counter)
    offset = [0.0, 0.0, 0.0, 0.0, 0.0]

    for i in range(5):
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

def position_sorted_V(offset:list,counter:list) -> list[str,int]:
    '''
    输入：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->大
    输出：[乐器编号, 偏移值] 的2d数组，形如：[[大, y], [大, y], [小, y], [小, y], [小, y]]
    输出的排序：[7,6,4,1,2,3,5,8]，左右侧之和都是18
    '''
    items = ['钢琴','小提琴','吉他','贝斯','大']
    input_sort = [list(t) for t in zip(items,counter,offset,[0,0,0,0,0],[0,0,0,0,0])]
    input_sort.sort(key=lambda x: x[2], reverse=1)

    sort_id = [1,2,3,4,5]
    for i in range(5):
        input_sort[i][3] = sort_id[i]

    input_sort.sort(key=lambda x: x[3], reverse=1)

    return input_sort

def random_forest_clf_train(train_set:DataFrame,dir_name:str,column_name:str, model_name):
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    model = RandomForestClassifier(n_estimators=300, max_leaf_nodes=20, n_jobs=-1,random_state=10)
    model.fit(X.values, y.values)

    joblib.dump(model, dir_name+"/model/"+model_name)


def load_rf_clf_model(model_path:str, predict_data):
    clf = joblib.load(model_path)
    # rnd_clf_prediction_proba = clf.predict_proba([predict_data]).tolist()[0]
    rnd_clf_prediction_proba = clf.predict_proba([predict_data]).tolist()[0]

    # 提取随机森林投票的标签  clf.classes_
    labels_list = []
    for each in clf.classes_:
        labels_list.append(each)
    
    proba_list = []
    for each in rnd_clf_prediction_proba:
        proba_list.append(each)
   
    output_list = list(t for t in zip(labels_list, proba_list))
    output_list.sort(key=lambda x: x[1],reverse=1)

    t = float(0)
    for i in range(4, 8):
        t += output_list[i][1]

    output_list = output_list[:4]
    output_list.append(['大', t])
    output_list.sort(key=lambda x: x[1],reverse=1)

    # 返回值的形式：
    # return [rnd_clf_prediction.tolist()[0], rnd_clf_prediction_proba.tolist()[0]]
    return output_list


def random_forest_reg_train(train_set:DataFrame,dir_name:str,column_name:str, model_name):
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    model = RandomForestRegressor(n_estimators=300, criterion='squared_error', max_leaf_nodes=20, n_jobs=1,random_state=10)
    # model = RandomForestRegressor(random_state=75)
    model.fit(X.values, y.values)

    joblib.dump(model, dir_name+"/model/"+model_name)

from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
import numpy as np

def random_forest_reg_live(train_set:DataFrame,column_name:str, predict_data):
    X = train_set.drop(columns=column_name ,axis=1)
    y = train_set[column_name]
    train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.2, shuffle=False)
    n_estimators = [int(x) for x in np.linspace(start = 10, stop = 80, num = 10)]
    max_depth = [2, 4]
    min_samples_split = [2, 5]
    min_samples_leaf = [1, 2]
    bootstrap = [True, False]

    param_grid = {
        'n_estimators':         n_estimators,
        'max_depth':            max_depth,
        'min_samples_split':     min_samples_split,
        'min_samples_leaf':      min_samples_leaf,
        'bootstrap':            bootstrap,
    }
    model = RandomForestRegressor()
    rf_RandomGrid = RandomizedSearchCV(estimator = model, param_distributions = param_grid, cv=10, verbose=0, n_jobs=4, )
    rf_RandomGrid.fit(train_x, train_y)
    print(f'Train Accuracy: {rf_RandomGrid.score(train_x, train_y):.3f}')
    print(f'Test Accuracy: {rf_RandomGrid.score(test_x, test_y):.3f}')

    # params = rf_RandomGrid.best_params_

    header = ['time']
    pd_data = DataFrame([predict_data], columns=header)

    prediction = rf_RandomGrid.predict(pd_data)

    return prediction


# 废弃了
def RND_REG_LIVE(train_set:DataFrame,column_name:str, predict_data):
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]

    pred_list = []
    for i in range(1,101):
        model = RandomForestRegressor(random_state=i)
        # model = RandomForestRegressor(random_state=75)
        model.fit(X.values, y.values)
        prediction = model.predict(predict_data).tolist()[0]
        pred_list.append(prediction)

    return pred_list


def load_rf_reg_model(model_path:str, predict_data):
    reg = joblib.load(model_path)
    prediction = reg.predict([predict_data])
    
    return prediction

