import numpy
import pandas as pd
from numpy import *
import logging
import os
import copy
import time
from rich.console import Console

# 自定义库
from kingdoms import DataAnalytics, counters_8, calcOffset_8, calcPositionSort_8_divi, calcPosition, calDiffSort_8_divi, load_rf_clf_model, load_rf_reg_model
import control_scrcpy_lib as csl
from ocr import result_recognition,background_screenshot,get_latest_result

from rich.theme import Theme
console = Console(theme=Theme({
    "pre": "bold purple blink",  # predict
    "re": "cyan bold blink",   # result
    "st": "#e3e3e3",  # statement
    "wa": "red bold",   # warning
    }))

# 自定义库
import instead_lib as inlib


console = Console()


# 常量
DIR = os.path.dirname(__file__)
DATA_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '\\input\\qmdata0819\\'
OUT_PATH = os.path.dirname(__file__)+'\\kaggle\\working\\'
print(OUT_PATH)
logging.basicConfig(
    filename=OUT_PATH+'qqmusic.log',
    encoding='utf-8',
    level=logging.DEBUG)

# DataFrame 表头，注意用tuple类型
NAME_HEADER = ('pc', 'vc', 'gc', 'bc', 'dc', 'hc', 'sc', 'oc','po','vo','go','bo','do','ho','so','oo','pp','vp','gp','bp','dp','hp','sp','op','pd','vd','gd','bd','dd','hd','sd','od','item_name')
NUM_HEADER = ('pc', 'vc', 'gc', 'bc', 'dc', 'hc', 'sc', 'oc','po','vo','go','bo','do','ho','so','oo','pp','vp','gp','bp','dp','hp','sp','op','pd','vd','gd','bd','dd','hd','sd','od','item_num')
NAME = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']

DIFF_NUM = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]
DIFF_TEXT = ['负七', '负六', '负五', '负四', '负三', '负二', '负一', '零', '一', '二', '三', '四', '五', '六', '七']

history = ''

inlib.screenshot_via_adb()
# 返回值是 [[名称] , [[时间, 时间戳]]]
recent_result = inlib.treasure_result_ocr(DIR + './img/shot.png')
start_time = recent_result[1][0][1]

total = 4
item_history = []
time_history = []
record_history = []
for each in recent_result[0]:
    item_history.insert(0, each)

for each in recent_result[1]:
    time_history.insert(0,each[0])

r = open(DIR+'./auto.csv', 'a', encoding='utf8')
for i in range(4):
    record_history.append([time_history[i],item_history[i]])
    r.write(time_history[i]+','+item_history[i]+'\n')
r.close()
for each in record_history:
    history += str(NAME.index(each[1])+1)
console.print('[st]最新记录：[/st]')
console.print(record_history[-5:])
total = 4

# old代码
selected_rate_diff = []
selected_rate_item = []

selected_rate_diff_text = []
selected_rate_diff_text_change_pair = []
selected_rate_item_text = []

diff_proba_trans_list = []
proba_item_list = []

reg_result_list = []
for i in range(21):
    reg_result_list.append(0)

buy_stragety = []
buy_decision = 2
# 开始循环
while True:

    inlib.compare_time(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)) , 58)
    start_time += 58
    inlib.screenshot_via_adb()

    # 返回值是 [[名称] , [[时间, 时间戳]]]
    recent_result = inlib.treasure_result_ocr(DIR + './img/shot.png')
    if len(record_history) > 20:
        record_history.pop(0)
    record_history.append([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)),recent_result[0][0]])
    r = open(DIR+'./auto.csv', 'a', encoding='utf8')
    r.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)) + ',' + recent_result[0][0] + '\n')
    r.close()
    console.print('[st]最新记录：[/st]')
    console.print(record_history[-5:])
    total += 1
    console.print(f'总数：{total}')

    in_put = str(NAME.index(record_history[-1][1])+1)

    if in_put not in ['1','2','3','4','5','6','7','8']:
        break
    else:
        history = history + in_put
        if len(history) > 20:
            history = history[-20:]
        console.print(f'当前History：{history}')


    #初始化的项值，是第一个结果出来前的counter统计状态
    # counter_list 是一个8维列表，用于记录每个回合的已出乐器统计量
    # offset_list 也是一个1D列表，用于记录每个回合的目标概率差值
    # position_sort_list 是一个16维的列表，用于记录每个回合的 目标概率差值。并且格式化成一个正态分布的结果，以使得其index值变成有意义的量化值，用于后面的特征计算。
    # position_list 是一个2D列表，用于记录每个回合的目标概率差值排序后的 顺序值
    # 将分解后的值，代入到处理diff的函数，计算出
    counter_list = [[0,0,0,0,0,0,0,0]]    
    offset_list = [[-0.200, -0.200, -0.200, -0.200, -0.091, -0.046, -0.037, -0.026]]    
    position_sort_list = []
    position_sort_list.append(calcPositionSort_8_divi(offset_list[-1]))    
    position_list = []
    position_list.append(calcPosition(position_sort_list[-1]))    
    diff_list = []
    diff_list.append(calDiffSort_8_divi(position_list[-1],1))

    # 定义 result 列表用于存放当前回合的乐器在上一回合对应的 position 值
    # 这个position值要在最新的position_list中取
    result = []   # 用于存放以 乐器名 为结果的数据
    result2 = []  # 用于存放以 diff值 为结果的数据
    for i in range(20):
        result2.append(0)


    single_line = []
    single_line2 = []

    for x in range(len(history)):
        
        # 当 history的长度超过20时，始终只取其右侧的20位数据
        format_history = DataAnalytics(history,20).formatted()
        
        result.append(NAME[int(format_history[-1]) - 1])

        for each in position_list[-1]:
            if result[-1] in each:
                p = each[-1]        
    
        
        for each in diff_list[-1]:
            if result[-1] in each:
                d_num = each[-1]
                d = DIFF_TEXT[DIFF_NUM.index(d_num)]
        
        result2.pop(0)
        result2.append(d_num)

        # 构建单行数据
        single_line = counter_list[-1] + offset_list[-1]
        for each in position_list[-1]:
            single_line.append(each[1])
        for each in diff_list[-1]:
            single_line.append(each[1])
        
        single_line2 = single_line.copy()
        
        single_line.append(result[-1])
        single_line2.append(d)
        
        # 对当前格式化的 历史数据 进行分类统计
        counter_list.append(counters_8(format_history))
        

        # 基于统计结果，进行 目标概率 的偏差值计算
        offset_list.append(calcOffset_8(counter_list[-1]))
        
        # 偏差值的排序
        position_sort_list.append(calcPositionSort_8_divi(offset_list[-1]))
        
        # 计算位序特征值
        position_list.append(calcPosition(position_sort_list[-1]))
        
        
        # 计算新的Diff特征值
        diff_list.append(calDiffSort_8_divi(position_list[-1],p))

    if len(diff_proba_trans_list) > 0:
        for each in diff_proba_trans_list:
            if result[-1] in each:
                selected_rate_diff.append(diff_proba_trans_list.index(each)+1)
                if diff_proba_trans_list.index(each)+1 in [1,2,5,6]:
                    selected_rate_diff_text.append('前')
                else:
                    selected_rate_diff_text.append('后')

                # 如果已经记录了 "即将消失的diff text"
                try:
                    diff_text_header
                except NameError:
                    pass
                else:
                    if diff_text_header != '':
                        selected_rate_diff_text_change_pair.append(diff_text_header + ' -> ' + selected_rate_diff_text[-1])

                # 当记录的 [前,后] 列表长度超过20时，取其倒数第20个值，存为 "即将消失的diff text"
                if len(selected_rate_diff_text) >= 20:
                    diff_text_header = selected_rate_diff_text[-20]
                else:
                    diff_text_header = ''

    # 对Diff的选项值进行预分类
    diff_sort = copy.deepcopy(diff_list[-1])
    diff_sort.sort(key=lambda x: x[1], reverse=1)
    diff_sort_left = diff_sort[0:4]
    diff_sort_right = diff_sort[4:8]
    console.print(f'差分\n左侧选项：{diff_sort_left}\n右侧选项：{diff_sort_right}')
    if len(result2) >= 20:
        reg_n_r_prediction_diff = load_rf_reg_model(DIR+'\\model\\rf_reg.m',result2[-20:]).tolist()[0]
        if reg_n_r_prediction_diff == 0:
            reg_predict_to_int = 0
        else:
            reg_predict_to_int = int(reg_n_r_prediction_diff)
        reg_result_list.pop(0)
        reg_result_list.append(reg_predict_to_int)
        # console.print(f'随机森林回归：Diff值预测\n{reg_predict_to_int}')
        merge_history_predict = []
        for i in range(20):
            merge_history_predict.append(str(reg_result_list[i])+ '|' +str(result2[i]))
        console.print(f'预测历史 | 实际结果\n[cyan]{merge_history_predict}[/cyan]\n当前：{reg_predict_to_int}')
        logging.info("预测历史 | 实际结果\n%s\n当前预测：%s", merge_history_predict,reg_predict_to_int)
        # console.print(f'预测历史参考：\t[grey]{reg_result_list}[/grey]')
        # console.print(f'实际历史参考：\t[grey]{result2[-20:]}[/grey] | [red]待验证[/red]')
    

    # 在循环外，合并最后一回合的数据，构建成测试数据
    predict_data = []
    predict_data = counter_list[-1] + offset_list[-1]
    for each in position_list[-1]:
        predict_data.append(each[1])
    for each in diff_list[-1]:
        predict_data.append(each[1])        

    front_counter = selected_rate_diff_text[-20:].count('前')
    back_counter = selected_rate_diff_text[-20:].count('后')

    console.print(f'实际结果对应的预测位置(历史值)：\n{selected_rate_diff[-20:]}\n{selected_rate_diff_text[-20:]}\n均值：{mean(selected_rate_diff[-20:])}\n前排总数：{front_counter}\t后排总数：{back_counter}')
    console.print(f'排位变化：{selected_rate_diff_text_change_pair[-5:]}')
    logging.info("位置值历史：%s\n位置：%s\n均值：%s\n前排总数：%s\n后排总数：%s",selected_rate_diff[-20:], selected_rate_diff_text[-20:], mean(selected_rate_diff[-20:]), front_counter, back_counter)

    r = open(OUT_PATH+'openlog.log', 'a', encoding='utf8')
    r.write(str(start_time)+'\n位置值历史：'+str(selected_rate_diff[-20:])+'\n位置：'+str(selected_rate_diff_text[-20:])+'\n均值：'+str(mean(selected_rate_diff[-20:]))+'\n前排总数：'+str(front_counter)+'\n后排总数：'+str(back_counter)+'\n')
    r.close()
    # 根据diff值的中文化标签，进行随机森林分类器的预测
    clf_n_r_proba_diff = load_rf_clf_model(DIR+'\\model\\rf_clf.m',predict_data)
    diff_proba_trans_list = []
    # proba_trans_list 变量用来对 clf_n_r_proba_diff 的输出结果进行翻译，转译成 以物品名方式显示的结果
    for each in clf_n_r_proba_diff:
        # each 的结构是 [Diff中文, 预测概率]，要把Diff中文替换为相关的乐器
        each_diff_name = ''
        each_diff_num = DIFF_NUM[DIFF_TEXT.index(each[0])]
        for item in diff_sort_left:
            if each_diff_num in item:
                each_diff_name = item[0]
        for item in diff_sort_right:
            if each_diff_num in item:
                each_diff_name = item[0]
        if each_diff_name != '':
            proba_temp = [each_diff_name,each[1]]
            diff_proba_trans_list.append(proba_temp)
        else:
            continue
        
    # 条件1： 前排数大于后排数
    # 条件2： 前排后排之和等于20
    # 条件3： 变化 情况前后相同的，大于等于3
    console.print(f'随机森林分类：物品的预测概率\n前排：{diff_proba_trans_list[0]}|{diff_proba_trans_list[1]}|{diff_proba_trans_list[4]}|{diff_proba_trans_list[5]}\n后排：{diff_proba_trans_list[2]}|{diff_proba_trans_list[3]}|{diff_proba_trans_list[6]}|{diff_proba_trans_list[7]}')
    console.print(f"[bold red]警告：大怪总数[/bold red]：{format_history.count('5') + format_history.count('6') + format_history.count('7') + format_history.count('8')} [red]应该至少有4个，否则押小容易出大[/red]")