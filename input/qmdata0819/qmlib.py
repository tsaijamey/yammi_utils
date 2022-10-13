# -*- coding: utf8 -*-

from cProfile import run
import copy
from distutils.command.config import dump_file
from email.utils import parsedate_to_datetime
from tkinter.tix import TList
from typing import ItemsView
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from pandas import DataFrame, array
import pandas as pd
import re
import os
import datetime
import numpy as np


'''
通过输入的方式，生成csv格式的数据集
数据集的内容形态：
2022-08-22 15:30:46,钢琴
2022-08-22 15:31:44,架子鼓
2022-08-22 15:32:42,钢琴
涉及：
1. 读写已有的文本(all.csv)
2. 输入本次序列的起始时间
3. 输入结果
4. 构建数据行
5. 写入all.csv
'''
def generat_dataset(file_path:str, override=0) -> DataFrame:
    '''
    参数说明：
    1. file_path：包含了所有历史数据的csv文件路径
    2. override：是否覆盖写入 该历史数据文件
        2.1 为0时，表示不覆盖，函数仅返回 Dataframe 结果；\n
        2.2 为1时，表示直接覆盖\n
        2.3 为2时，表示存为新文件，文件位置为当前脚本目录，文件名格式为 new_all_history_{时间}.csv
    '''
    # 接收时间
    r_time = input('输入起始时间，格式为2022-01-01 14:00:00：')
    # 为防止意外输入中文冒号
    r_time = r_time.replace('：',':') 

    # 接收结果
    input_str = ''
    result = ''
    while '0' not in input_str and '9' not in input_str:
        input_str = input('依次输入回合结果，也可以一次粘贴多个结果，以0或9结束输入：')
        result += input_str
        # 去掉result里存入的0和9
        strings = u'[0 9 ：, ，]'
        rules = re.compile(strings)
        result = re.sub(rules, '', result)

        num = ['1', '2', '3', '4', '5', '6', '7', '8']
        item = ['钢琴', '小提琴', '吉他', '贝斯', '架子鼓', '竖琴', '萨克斯', '圆号']
        r_list = []
        for each in result:
            r_list.append(item[num.index(each)])
        
        # 生成时间序列
        idx = pd.date_range(r_time, periods=len(result), freq="58S")
        # 转化成 DataFrame
        ts = pd.DataFrame(idx,columns=['时间'])
        rs = pd.DataFrame(r_list,columns=['记录'])

        gs = pd.concat([ts,rs],axis=1)

        if os.path.exists(file_path):
            f = pd.read_csv(file_path)
            gs = pd.concat([f,gs],axis=0)

        print(gs.tail())
        print(gs.shape[0])
    
    if override == 1:
        gs.to_csv(file_path,index=False)
        return gs
    elif override == 2:
        dir_setting = os.path.split(os.path.abspath(__file__))[0]
        print(f'保存目录：{dir_setting}')
        gs.to_csv(dir_setting+'./new_all_history_by_'+r_time.replace(':', '-')+'.csv',index=False)
    else:
        return gs

'''
各种问题的解决：
pandas dataframe逐行读取
https://blog.csdn.net/qq_41292236/article/details/108049943
numpy的array转list
https://blog.csdn.net/weixin_39655993/article/details/113960737
把str值转化为时间值
https://blog.csdn.net/liujingwei8610/article/details/124358645
计算时间差
https://www.py.cn/jishu/jichu/12878.html
列表求和
https://www.delftstack.com/zh/howto/python/sum-of-list-of-numbers-in-python
List转DataFrame
https://blog.csdn.net/claroja/article/details/64439735
多维列表的排序问题解决方法
https://www.youtube.com/watch?v=EPIUxGOynE0
重置Dataframe的索引
https://www.delftstack.com/zh/api/python-pandas/pandas-dataframe-dataframe.reset_index-function/
Dataframe去除指定行
https://www.delftstack.com/zh-tw/howto/python-pandas/drop-row-pandas
随机森林参数说明
https://blog.csdn.net/m0_37876745/article/details/85271508

'''

def datasets_split(input_csv,input_mode=1) -> list:
    '''
    从csv数据集中读取数据，并根据时间差自动分割数据集，整个数据集是多个子数据集（list）的集合（list）

    :input_csv:     输入的表格，表格的每行内容格式为 datetime,item_name
    :input_mode:    输入模式，1表示读取表格文件

    输出：list，list的格式[[]]
    '''
    if input_mode == 1:
        DF = pd.read_csv(input_csv)
    elif input_mode == 2:   
        DF = input_csv
    
    # 逐行读取
    transformed_list = []
    splited_list = []
    item_dict = {'钢琴':'1', '小提琴':'2', '吉他':'3', '贝斯':'4', '架子鼓':'5', '竖琴':'6', '萨克斯':'7', '圆号':'8'}

    # 逐行读取表格数据
    # 对每行数据进行转换后，分析它与上一行的时间值的差额，如果大于58秒，则认为当前这一行属于新的数据段落
        # 把前面的数据存到 splited_list 里，再把当前这行变为新的 transformed_list
        # 如此循环
    # 最后一个段落的数据要单独存到 transformed_list 里
    for index in DF.index:
        
        
        time_str = DF.loc[index].values.tolist()[0]
        r_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

        # 通过字典，把物品名称转义成对应的编号
        item = DF.loc[index].values.tolist()[-1]        
        number = item_dict[item]
        
        # 
        transformed_list.append([r_time, number])

        # 大于58秒进行切割
        if len(transformed_list) > 1 and (transformed_list[-1][0] - transformed_list[-2][0]).seconds > 58:            
            splited_list.append(transformed_list[:-1])
            transformed_list = transformed_list[-1:]
    
    # 最后一个段落的数据
    splited_list.append(transformed_list)

    return splited_list

def datasets_dealer(input_list:list, rule:int, result=0, only_for_train=1, data_type=0) -> DataFrame:
    '''
    参数：
    :input_list:        一个连续时间上的物品编号历史记录，每行内容格式：  datetime, item_number \n
    :rule:              要么是5，要么是8\n
    :result:            1  输出物品编号（数字           其他，输出物品名称\n
    :only_for_train:    1  输出不包含最后一行的数据     0  输出包含最后一行的数据\n
    :data_type:         0=只含差分值    1=完整的    2=输出旧格式（不含时间，只含物品名）
    \n
    输入：2d列表
    输出：包含多列数据的Dataframe
    '''
    item_list               = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯','圆号']

    item_dict = {
        '1':    '钢琴',
        '2':    '小提琴',
        '3':    '吉他',
        '4':    '贝斯',
        '5':    '架子鼓',
        '6':    '竖琴',
        '7':    '萨克斯',
        '8':    '圆号',
    }

    diff_text_dict        = {'负七':-7, '负六':-6, '负五':-5, '负四':-4, '负三':-3, '负二':-2, '负一':-1, '零':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7}
    diff_num_dict        = {'-7':'负七', '-6':'负六', '-5':'负五', '-4':'负四', '-3':'负三', '-2':'负二', '-1':'负一', '0':'零', '1':'一', '2':'二', '3':'三', '4':'四', '5':'五', '6':'六', '7':'七'}
    item_number_dict        = {'1':'钢琴', '2':'小提琴', '3':'吉他', '4':'贝斯', '5':'架子鼓', '6':'竖琴', '7':'萨克斯', '8':'圆号'}
    counter_header          = ('pc','vc','gc','bc','dc','hc','sc','oc')
    offset_header           = ('po','vo','go','bo','do','ho','so','oo')
    position_header         = ('pp','vp','gp','bp','dp','hp','sp','op')
    diff_header             = ('pd','vd','gd','bd','dd','hd','sd','od')
    item_number_list        = []
    diff_result_list         = []
    counter_list            = [[0,0,0,0,0,0,0,0]]
    offset_list             = [[-20,-20,-20,-20,-9.10,-4.60,-3.70,-2.60]]
    position_list           = [[4,5,6,3,8,1,2,7]]

    # diff_list的初始值，目的是为了构建一个对应第一行结果的 diff_result，使之与
    diff_list         = [[3,4,5,2,7,0,1,6]]

    for each in input_list:

        item_number = each[1]  # 每一行的第二个值对应的是物品编号

        item_number_list.append(each[1])
        if len(item_number_list) > 20:
            item_number_list.remove(item_number_list[0])


        diff_result_list.append(diff_num_dict[str(diff_list[-1][int(item_number)-1])])


        if rule == 5:
            print('5对应的规则，是把所有的大怪，作为一个20%概率的整体来看待。')
            pass
        
        if rule == 8:
            # counter_list存储的是每一回合的统计值，数据形态：[[a1,b1,c1,d1,h1,i1,j1,k1], [a2,b2,c2,d2,h2,i2,j2,k2], ...]
            c = counters_8(item_number_list)
            counter_list.append(c)

            # offset_list存储的是每一回合的统计值，数据形态：[[0.xxx, 0.xxx, -0.xxx, -0.xxx, 0.xxx, 0.xxx, -0.xxx, -0.xxx], [0.xxx, 0.xxx, -0.xxx, -0.xxx, 0.xxx, 0.xxx, -0.xxx, -0.xxx], ...]
            o = offsets_8(c)
            offset_list.append(o)

            ps = position_sort_8_distrib(o)
            p = position_8(ps)
            position_list.append(p)

            if len(position_list) <= 1:
                last_p = 1
            elif len(position_list) > 1:
                last_p = position_list[-2][int(each[1])-1]
            
            d = diff_8_distrib(p, last_p)
            diff_list.append(d)


    pd_time     = pd.DataFrame([t[0] for t in input_list], columns=['时间'])

    if result == 0:
        pd_datalist = pd.DataFrame([item_list[int(t[1])-1] for t in input_list], columns=['item_name'])
    elif result == 1:
        pd_datalist = pd.DataFrame([t[1] for t in input_list], columns=['item_name'])
    else:
        pd_datalist = pd.DataFrame([item_list[int(t[1])-1] for t in input_list], columns=['item_name'])

    pd_diffresult = pd.DataFrame(diff_result_list, columns=['item_num'])

    pd_counters = pd.DataFrame(counter_list, columns=counter_header)
    pd_offset   = pd.DataFrame(offset_list, columns=offset_header)
    pd_position = pd.DataFrame(position_list, columns=position_header)
    pd_diff     = pd.DataFrame(diff_list,columns=diff_header)    

    if only_for_train == 1:
        pd_counters = pd_counters.drop(pd_counters.index[-1])
        pd_offset   = pd_offset.drop(pd_offset.index[-1])
        pd_position = pd_position.drop(pd_position.index[-1])
        pd_diff     = pd_diff.drop(pd_diff.index[-1])

    if data_type == 1:
        export_list = pd.concat([pd_time, pd_counters, pd_offset, pd_position, pd_diff, pd_datalist, pd_diffresult],axis=1)
    elif data_type == 0:
        # print('将输出 差分值')
        export_list = pd.concat([pd_counters, pd_offset, pd_position, pd_diff, pd_diffresult],axis=1)
    elif data_type == 2:
        # print('将输出 物品名')
        export_list = pd.concat([pd_counters, pd_offset, pd_position, pd_diff, pd_datalist],axis=1)
    # export_list = ['结果保留']

    return export_list

def counters_8(s:list)  -> list:
    '''
    输入：字符数据列表，形如： ['1','2','3','4','5','6','7','8']，左右对应顺序 = 钢琴->圆号\n
    输出：列表，形如：[20, 20, 19, 19, 4, 2, 1, 0]，左右对应顺序 = 钢琴->圆号
    '''
    counter = [0,0,0,0,0,0,0,0]
    for i in range(8):
        counter[i] = s.count(str(i+1))

    # print(f'本次统计值：{counter}')
    return counter

def offsets_8(c:list) -> list:
    '''
    输入：乐器数量统计列表，形如：[20, 20, 19, 19, 4, 2, 1, 0]，左右对应顺序 = 钢琴->圆号
    输出：乐器已知概率与目标概率的偏移量，形如：[0.xxx, 0.xxx, -0.xxx, -0.xxx, 0.xxx, 0.xxx, -0.xxx, -0.xxx]，左右对应顺序 = 钢琴->圆号
    '''

    rates = [0.200, 0.200, 0.200, 0.200, 0.091, 0.046, 0.037, 0.026]
    all = sum(c)
    offset = [0,0,0,0,0,0,0,0]

    for i in range(8):
        offset[i] = round(100*(c[i]/all - rates[i]), 2)

    # print(f'本次偏移值：{offset}')
    return offset

def position_sort_8_distrib(offsets:list) -> list:
    '''
    输入：乐器已知概率与目标概率的偏移量，形如：[0.xxx, 0.xxx, -0.xxx, -0.xxx, 0.xxx, 0.xxx, -0.xxx, -0.xxx]，左右对应顺序 = 钢琴->圆号\n
    输出：[乐器编号, 偏移值] 的2d数组，形如：[[大, y], [大, y], [小, y], [小, y], [小, y], [小, y], [大, y], [大, y]]
    '''
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯','圆号']
    items_position_sort = []

    # 
    # 把8种乐器分为两组，分别进行排序，排序后把结果合并到一个数组里：
    items_offset_left = [list(t) for t in zip(items[0:4],offsets[0:4])]
    items_offset_right = [list(t) for t in zip(items[4:8],offsets[4:8])]
    items_offset_left.sort(key=lambda x: x[1], reverse=1)
    items_offset_right.sort(key=lambda x: x[1], reverse=1)
    items_position_sort.append(items_offset_right[2])
    items_position_sort.append(items_offset_right[1])
    items_position_sort.append(items_offset_left[3])
    items_position_sort.append(items_offset_left[0])
    items_position_sort.append(items_offset_left[1])
    items_position_sort.append(items_offset_left[2])
    items_position_sort.append(items_offset_right[0])
    items_position_sort.append(items_offset_right[3])

    return items_position_sort

def position_8(items_postion_sort:list) -> list:
    '''
    输入：列表。数据形态为 [[str, float], [str, float], ...]
    输出：列表。数据形态为 [int, int, int, int, int, int, int, int] 
    '''
    # 先用deepcopy复制一下入参。
    # 因为入参是 2d列表， cppy函数是无法传递 2d 数据的。
    # 涉及到修改列表值的问题，所以要复制，不要直接在入参上修改，否则原始列表值也会被替换。
    temp = copy.deepcopy(items_postion_sort)
    for i in range(8):
        # 把偏移值根据 index 转换成 int数值，从 8 到 1
        temp[i][1] = i + 1
    
    output = []
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯','圆号']
    for each in items:
        for x in temp:
            if each in x:
                output.append(x[1])
    
    return output

def diff_8_distrib(position:list,last_pos:int):
    '''
    输入：
    1. 列表是同期的位序值 [int, int, int, int, int, int, int, int]
    2. 上一轮结果对应的位序值，需要根据item，从 position_8函数输出结果中的倒数第二项去找
    '''
    diff = [0,0,0,0,0,0,0,0]
    
    for i in range(8):
        diff[i] = position[i] - last_pos

    #items_diff.sort(key=lambda x: x[1], reverse=1)
        
    return diff    

def rfc_proba(trainset:DataFrame, testset:DataFrame, x_name:list, y_name:str, run_mode=0):
    '''_summary_

    参数:
        trainset (DataFrame): 训练集文件路径
        testset (DataFrame): 测试集文件路径
        x_name (list): X要抛弃的列头
        y_name (str): y的列头
        run_mode (int, optional): 运行模式，0适用于测试，1适用于实战. 默认0.
    '''

    diff_text_to_num = {'负七':-7, '负六':-6, '负五':-5, '负四':-4, '负三':-3, '负二':-2, '负一':-1, '零':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7}
    Xtrain = trainset.drop(columns=x_name)
    ytrain = trainset[y_name]

    Xtest = testset.drop(columns=x_name)
    ytest = testset[y_name]

    # 建立随机森林
    rfc = RandomForestClassifier(n_estimators=35, max_depth=50, min_samples_split=20, min_samples_leaf=20, min_weight_fraction_leaf=0.2, max_leaf_nodes=40, n_jobs=-1)
    rfc.fit(Xtrain.values, ytrain.values)
    loc_list = []
    for i in range(11,len(Xtest.values)):
        rfc_proba = rfc.predict_proba([Xtest.values[i]]).tolist()[0]

        # 提取随机森林投票的标签  clf.classes_
        labels_list = []
        for each in rfc.classes_:
            labels_list.append(each)
        
        proba_list = []
        for each in rfc_proba:
            proba_list.append(round(each,2))

        # print(labels_list)
        # print(proba_list)
        
        output_list = list(t for t in zip(labels_list, proba_list))
        output_list.sort(key=lambda x: x[1],reverse=1)

        for each in output_list:
            if ytest.values[i] in each:
                loc = output_list.index(each) + 1
        
        loc_list.append(loc)

        if run_mode == 0:
            print(f'第{i+1}行数据预测概率：{output_list}')
            print(f'第{i+1}行数据实际结果：{ytest.values[i]}，预测值位置：{loc}')
            print('\n')
    
    if run_mode == 1:
        print(f'对照：{Xtest.values[i]}')
        print(f'最后1行数据预测概率：{output_list}')


    loc_var = np.var(loc_list)
    loc_std = np.std(loc_list, ddof=1)
    loc_avg = np.mean(loc_list)

    print(f'预测方差为：{loc_var}')
    print(f'预测标准差为：{loc_std}')
    print(f'均值为：{loc_avg}')

def rn_clf_proba(train_set:DataFrame, predict_data:list, column_name:str, ) -> array:
    '''
    随机森林决策树分类 -> 返回的是置信度排序
    输入：训练集 | 待预测的列表数据
    输出：[预测值, 预测概率]
    '''
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    rnd_clf = RandomForestClassifier(n_estimators=100, max_depth=50, min_samples_split=20, min_samples_leaf=20, min_weight_fraction_leaf=0.2, max_leaf_nodes=40, n_jobs=-1)
    rnd_clf.fit(X.values, y.values)

    rnd_clf_prediction_proba = rnd_clf.predict_proba([predict_data]).tolist()[0]

    # 提取随机森林投票的标签  clf.classes_
    labels_list = []
    for each in rnd_clf.classes_:
        labels_list.append(each)
    
    proba_list = []
    for each in rnd_clf_prediction_proba:
        proba_list.append(round(each,2))

    # print(labels_list)
    # print(proba_list)
    
    output_list = [[t] for t in zip(labels_list, proba_list)]
    output_list.sort(key=lambda x: x[1],reverse=1)

    # 返回值的形式：
    # return [rnd_clf_prediction.tolist()[0], rnd_clf_prediction_proba.tolist()[0]]
    return output_list