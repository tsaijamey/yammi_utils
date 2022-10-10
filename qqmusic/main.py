import pandas as pd
from pandas import DataFrame, array
from numpy import *
import time
import logging
import os
from kingdoms import DataAnalytics, counters_8, calcOffset_8, calcPositionSort_8_divi, calcPosition, calDiffSort_8_divi, rf_clf_proba
import copy
import control_scrcpy_lib as csl
import pyautogui
import time
import win32gui,win32ui,win32con
from ocr import result_recognition
from recognition import background_screenshot,get_latest_result

# 常量
data_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '\\input\\qmdata0819\\'
out_path = os.path.abspath(os.path.dirname(__file__))+'\\kaggle\\working\\'
logging.basicConfig(filename=out_path+'qqmusic.log', encoding='utf-8', level=logging.DEBUG)

# DataFrame 表头，注意用tuple类型
name_header = ('pc', 'vc', 'gc', 'bc', 'dc', 'hc', 'sc', 'oc','po','vo','go','bo','do','ho','so','oo','pp','vp','gp','bp','dp','hp','sp','op','pd','vd','gd','bd','dd','hd','sd','od','item_name')
num_header = ('pc', 'vc', 'gc', 'bc', 'dc', 'hc', 'sc', 'oc','po','vo','go','bo','do','ho','so','oo','pp','vp','gp','bp','dp','hp','sp','op','pd','vd','gd','bd','dd','hd','sd','od','item_num')
name = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯','圆号']

d_num_list = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]
d_text_list = ['负七', '负六', '负五', '负四', '负三', '负二', '负一', '零', '一', '二', '三', '四', '五', '六', '七']

CLF_df = pd.read_csv(data_path+'all_name_datasets_rebuilt.csv')
REG_df = pd.read_csv(data_path+'all_num_datasets_rebuilt.csv')

history = ''

buyoption = ''

# 进入qq音乐房间
import go_into_qqmusic_room

# 外来代码
dirname_ = os.path.dirname(__file__)
hwnd = csl.get_hwd('qqmusic')
record_button_pos = csl.find_element(hwnd, dirname_+'./find_treasure_button.png', 0.80)
if record_button_pos != [0,0]:
    (x, y) = record_button_pos
    pyautogui.moveTo(x, y)
    time.sleep(1)
    pyautogui.click()
    time.sleep(3)
    
    # 为识别结果进行的截图，存为同目录下的screenshot.bmp
    background_screenshot(hwnd)

    records = result_recognition(dirname_+'./screenshot.bmp')

    # 返回无记录的界面
    kingdom_title_pos = csl.find_element(hwnd, dirname_+'./kingdom_title.png', 0.80)
    if kingdom_title_pos != [0,0]:
        (x, y) = kingdom_title_pos
        pyautogui.moveTo(x, y)
        time.sleep(1)
        pyautogui.click()
        time.sleep(3)
    print(records)

    history = str(name.index(records[0][0]) + 1)
    s_time = records[0][1]
    latest_time = records[0][1]

# old代码
selected_rate_diff = []
selected_rate_item = []

selected_rate_diff_text = []
selected_rate_diff_text_change_pair = []
selected_rate_item_text = []

diff_proba_trans_list = []
proba_item_list = []

buy_stragety = []

buy_stragety_list = []
buy_list = []
buy_decision = 2
# 开始循环
while True:

    # 以变量 s_time 为起点时间，构建一个间隔为58s的时间序列
    idx = pd.date_range(s_time, periods=len(history), freq="58S")
    # 转化成 DataFrame
    ts = pd.DataFrame(idx,columns=['回合时间'])

    # 基于 history 的值，初始化一个 历史记录 的list
    h_list = DataAnalytics(history,0).formatted()
    for each in h_list:
        h_list[h_list.index(each)] = name[int(each)-1]

    rs = pd.DataFrame(h_list,columns=['历史记录'])
    js = pd.concat([ts,rs],axis=1)
    print('*' * 10)
    print(js.tail())
    print('*' * 10)
    logging.info('\n近5回合历史：\n%s', js.tail())

    print('\n')

    # 先转换为时间数组
    last_record_timearray = time.strptime(latest_time, "%Y-%m-%d %H:%M:%S") 
    # 转换为时间戳
    last_record_timeStamp = int(time.mktime(last_record_timearray))

    print(f'最后出货的时间戳为：{last_record_timeStamp}, 目标时间戳：{last_record_timeStamp + 60}\n')
    present_time = last_record_timeStamp
    while present_time <= last_record_timeStamp + 60:
        present_time = int(time.time())
        # print(f"当前时间为：{present_time}, {time.strftime('%Y-%m-%d T%H:%M:%S',time.localtime(present_time))}")
        time.sleep(5)


    (in_put, latest_time) = get_latest_result()
    if in_put not in ['1','2','3','4','5','6','7','8']:
        break
    else:
        history = history + in_put
    
    print('\n')

    #初始化的项值，是第一个结果出来前的counter统计状态
    # counter_list 是一个8维列表，用于记录每个回合的已出乐器统计量
    counter_list = [[0,0,0,0,0,0,0,0]]

    # offset_list 也是一个1D列表，用于记录每个回合的目标概率差值
    offset_list = [[-0.200, -0.200, -0.200, -0.200, -0.091, -0.046, -0.037, -0.026]]

    # position_sort_list 是一个16维的列表，用于记录每个回合的 目标概率差值。并且格式化成一个正态分布的结果，以使得其index值变成有意义的量化值，用于后面的特征计算。
    position_sort_list = []
    position_sort_list.append(calcPositionSort_8_divi(offset_list[-1]))

    # position_list 是一个2D列表，用于记录每个回合的目标概率差值排序后的 顺序值
    position_list = []
    position_list.append(calcPosition(position_sort_list[-1]))

    # 将分解后的值，代入到处理diff的函数，计算出
    diff_list = []
    diff_list.append(calDiffSort_8_divi(position_list[-1],1))

    # 定义 result 列表用于存放当前回合的乐器在上一回合对应的 position 值
    # 这个position值要在最新的position_list中取
    result = []   # 用于存放以 乐器名 为结果的数据
    result2 = []  # 用于存放以 diff值 为结果的数据


    single_line = []
    single_line2 = []

    # 构建一个空的DataFrame，用来格式化训练数据
    trainset = pd.DataFrame()
    trainset2 = pd.DataFrame()

    for x in range(len(history)):
        
        # 将当前回合之前的历史结果，存入 current_history        
        current_history = history[:x+1]
        
        # 当 history的长度超过31时，始终只取其右侧的31位数据
        format_history = DataAnalytics(current_history,20).formatted()
        
        result.append(name[int(format_history[-1]) - 1])

        for each in position_list[-1]:
            if result[-1] in each:
                p = each[-1]        
    
        
        for each in diff_list[-1]:
            if result[-1] in each:
                d_num = each[-1]
                d = d_text_list[d_num_list.index(d_num)]
        
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
        
        # 单行数据构建成DataFrame
        line = pd.DataFrame([single_line], columns=name_header)
        line2 = pd.DataFrame([single_line2], columns=num_header)
        
        trainset    = pd.concat([trainset,line])        
        trainset2   = pd.concat([trainset2,line2])
        
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

    if buy_stragety != [] and result[-1] in buy_stragety and buy_decision == 1:
        buy_list.append([buy_stragety, result[-1], '胜'])
    elif buy_stragety != [] and result[-1] not in buy_stragety and buy_decision == 1:
        buy_list.append([buy_stragety, result[-1], '负'])

    if buy_stragety != [] and result[-1] in buy_stragety:
        buy_stragety_list.append([buy_stragety, result[-1], '对'])
        buy_decision = 1
    elif buy_stragety != [] and result[-1] not in buy_stragety:
        buy_stragety_list.append([buy_stragety, result[-1], '错'])
        buy_decision = 0

    if len(buy_stragety_list) > 0:
        # print(f'近20次选注组合：{buy_stragety_list}')
        # logging.info('近20次选注组合：%s', buy_stragety_list)
        pass

    if len(buy_list) > 0:
        win_num = 0
        for each in buy_list[-20:]:
            if '胜' in each:
                win_num += 1
        sum_buy_counter_win_rate = round(win_num / len(buy_list[-20:]), 2)
    
        # print(f'近20次实际下注：{buy_list}\n胜率：{sum_buy_counter_win_rate}\n')
        # logging.info('近20次实际下注：%s\n胜率：%s\n', buy_list, sum_buy_counter_win_rate)
        print(f'胜率：{sum_buy_counter_win_rate}\n')
        logging.info('胜率：%s\n',sum_buy_counter_win_rate)

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
        
        front_counter = selected_rate_diff_text[-20:].count('前')
        back_counter = selected_rate_diff_text[-20:].count('后')

        if front_counter > back_counter and front_counter+back_counter > 5:
            # print(f'策略逻辑：\n1）主买前排。出"后"时不买。遇到"后"变"前"，则下一回合买"前"，一个周期只买这一次。\n2）选注组合对的时候连买，策略错的是等对了再买。')
            # logging.info('策略逻辑：\n1）主买前排。出"后"时不买。遇到"后"变"前"，则下一回合买"前"，一个周期只买这一次。\n2）选注组合对的时候连买，策略错的是等对了再买。')
            print(f'策略逻辑：主买前排。')
            logging.info('策略逻辑：主买前排。')
            if selected_rate_diff_text[-1] == '前' and selected_rate_diff_text[-2] == '后':
                # 买"前"
                buyoption = '买前排选项'
            else:
                # 不买
                buyoption = ''
        elif back_counter > front_counter and front_counter+back_counter > 5:
            # print(f'策略逻辑：\n1）主买后排。出"前"时不买。遇到"前"变"后"，则下一回合买"后"，一个周期只买这一次。\n2）选注组合对的时候连买，策略错的是等对了再买。')
            # logging.info('策略逻辑：\n1）主买后排。出"前"时不买。遇到"前"变"后"，则下一回合买"后"，一个周期只买这一次。\n2）选注组合对的时候连买，策略错的是等对了再买。')
            print(f'策略逻辑：主买后排。')
            logging.info('策略逻辑：主买后排。')
            if selected_rate_diff_text[-1] == '后' and selected_rate_diff_text[-2] == '前':
                # 买"前"
                buyoption = '买后排选项'
            else:
                # 不买
                buyoption = ''
        else:
            buyoption = ''
                   

    # if len(proba_item_list) > 0:
    #     for each in proba_item_list:
    #         if result[-1] in each:
    #             selected_rate_item.append(proba_item_list.index(each)+1)
    #             if proba_item_list.index(each)+1 in [1,2,5,6]:
    #                 selected_rate_item_text.append('前')
    #             else:
    #                 selected_rate_item_text.append('后')
    
        # print(f'分析：实际结果\n位于selected_rate_diff的历史值：{selected_rate_diff[-20:]}\n{selected_rate_diff_text[-20:]}\n位于selected_rate_item的历史值：{selected_rate_item[-20:]}\n{selected_rate_item_text[-20:]}')
        # logging.info('分析：实际结果\n位于selected_rate_diff的历史值：%s\n%s\n位于selected_rate_item的历史值：%s\n%s', selected_rate_diff[-20:], selected_rate_diff_text[-20:], selected_rate_item[-20:], selected_rate_item_text[-20:])
        print(f'分析：实际结果\n位于selected_rate_diff的历史值：\n{selected_rate_diff[-20:]}\n{selected_rate_diff_text[-20:]}\n均值：{mean(selected_rate_diff[-20:])}\n\n前排总数：{front_counter}\t后排总数：{back_counter}')
        print(f'selected_rate_diff的变化：{selected_rate_diff_text_change_pair[-5:]}')
        logging.info('分析：实际结果\n位于selected_rate_diff的历史值：%s\n%s\n\n前排总数：%s\t后排总数：%s', selected_rate_diff[-20:], selected_rate_diff_text[-20:], front_counter,back_counter)

    

    trainset    = pd.concat([CLF_df,trainset])
    trainset2   = pd.concat([REG_df,trainset2])

    # print(f'CLF训练集的行数：{trainset.shape[0]} \t REG训练集的行数：{trainset2.shape[0]}')
    # logging.info('CLF训练集的行数：%s，REG训练集的行数：%s', trainset.shape[0], trainset2.shape[0])

    print(f'输入的结果：{result[-1]} \t Diff历史：{result2[-20:]}\n')
    logging.info('输入的结果：%s \t Diff历史：%s' , result[-1], result2[-20:])

    print('\n')

    # 对Diff的选项值进行预分类
    diff_sort = copy.deepcopy(diff_list[-1])
    diff_sort.sort(key=lambda x: x[1], reverse=1)
    diff_sort_left = diff_sort[0:4]
    diff_sort_right = diff_sort[4:8]
    print(f'A选项：{diff_sort_left} \t B选项：{diff_sort_right}')
    logging.info('A选项：%s \t B选项：%s', diff_sort_left, diff_sort_right)
    print('\n')

    # 在循环外，合并最后一回合的数据，构建成测试数据
    predict_data = []
    predict_data = counter_list[-1] + offset_list[-1]
    for each in position_list[-1]:
        predict_data.append(each[1])
    for each in diff_list[-1]:
        predict_data.append(each[1])        

    # 根据diff值的中文化标签，进行随机森林分类器的预测
    clf_n_r_proba_diff = rf_clf_proba(trainset2,predict_data,'item_num')
    diff_proba_trans_list = []
    # proba_trans_list 变量用来对 clf_n_r_proba_diff 的输出结果进行翻译，转译成 以物品名方式显示的结果
    for each in clf_n_r_proba_diff:



        # each 的结构是 [Diff中文, 预测概率]，要把Diff中文替换为相关的乐器
        each_diff_name = ''
        each_diff_num = d_num_list[d_text_list.index(each[0])]
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
    

        
    # print(f'Diff标签森林分类：{clf_n_r_proba_diff}')
    print(f'Diff标签森林分类\n前排：{diff_proba_trans_list[0]}\t{diff_proba_trans_list[1]}\t{diff_proba_trans_list[4]}\t{diff_proba_trans_list[5]}\n后排：{diff_proba_trans_list[2]}\t{diff_proba_trans_list[3]}\t{diff_proba_trans_list[6]}\t{diff_proba_trans_list[7]}')
    logging.info('Diff标签森林分类\n前排：%s\t%s\t%s\t%s\n后排：%s\t%s\t%s\t%s', diff_proba_trans_list[0], diff_proba_trans_list[1], diff_proba_trans_list[4], diff_proba_trans_list[5], diff_proba_trans_list[2], diff_proba_trans_list[3], diff_proba_trans_list[6], diff_proba_trans_list[7])

    if '前' in buyoption:
        buy_stragety = [diff_proba_trans_list[0][0], diff_proba_trans_list[1][0], diff_proba_trans_list[4][0], diff_proba_trans_list[5][0]]
    elif '后' in buyoption:
        buy_stragety = [diff_proba_trans_list[2][0], diff_proba_trans_list[3][0], diff_proba_trans_list[6][0], diff_proba_trans_list[7][0]]
    else:
        buy_stragety = []
    
    if  buy_stragety != []:
        print(f'\n选注组合为：{buy_stragety}')
        logging.info('\n选注组合为：%s', buy_stragety)

    if buy_decision == 1:
        print(f'\n可购买')
        logging.info('\n可购买。')
    elif buy_decision == 0:
        print(f'\n不可购买。')
        logging.info('\n不可购买。')
    else:
        print(f'\n下注跳过。')
        logging.info('\n下注跳过。')

    print('\n')
    print(f"大怪总数：{format_history.count('5') + format_history.count('6') + format_history.count('7') + format_history.count('8')}")
    logging.info('大怪总数：%s', format_history.count('5') + format_history.count('6') + format_history.count('7') + format_history.count('8'))

# Kaggle Notebook不能直接写入数据
trainset.to_csv(out_path + 'name_datasets.csv',index=False)
trainset2.to_csv(out_path + 'num_datasets.csv',index=False)


history_list = []
for x in range(len(history)):
    # 将当前回合之前的历史结果，存入 current_history    
    history_list.append(name[int(history[x])-1])
idx2 = pd.date_range(s_time, periods=len(history), freq="58S")
td = pd.DataFrame(idx2, columns=['时间'])
hd = pd.DataFrame(history_list, columns=['记录'])

thd = pd.concat([td,hd],axis=1)
old_record = pd.read_csv(data_path+'all.csv')
thd = pd.concat([old_record,thd],axis=0)
filename = out_path + '/QMK-history-' + s_time.replace(":","-") + '.csv'
thd.to_csv(filename,index=False)
# else:
#     thd.to_csv(this_dir+'./Datasets/all.csv',index=False)