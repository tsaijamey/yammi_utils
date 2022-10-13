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

# 步骤一：进入QQ音乐直播房间
import go_into_qqmusic_room             # 这部分代码找时间要封装一下

# 步骤二：找到“寻宝记录”的元素位置，然后点开
dirname_ = os.path.dirname(__file__)
hwnd = csl.get_hwd('qqmusic')
record_button_pos = csl.find_element(hwnd, dirname_+'./img/find_treasure_button.png', 0.80)
if record_button_pos != [0,0]:
    (x, y) = record_button_pos
    csl.pyautogui_click(hwnd,x,y)
    time.sleep(2)
    
    # 为识别结果进行的截图，存为同目录下的screenshot.bmp
    background_screenshot(hwnd)

    try:
        records = result_recognition(dirname_+'./img/screenshot.bmp')
        history = str(NAME.index(records[0][0]) + 1)
        s_time = records[0][1]
        latest_time = records[0][1]
    except Exception as e:
        console.print(e)
        console.print('未检测到数据')
        exit(-1)

    # 返回无记录的界面
    kingdom_title_pos = csl.find_element(hwnd, dirname_+'./img/kingdom_title.png', 0.80)
    if kingdom_title_pos != [0,0]:
        (x, y) = kingdom_title_pos
        csl.pyautogui_click(hwnd,x,y)
        time.sleep(.5)        
    else:
        console.print('界面异常')
        exit(-1)

# old代码
selected_rate_diff = []
selected_rate_item = []

selected_rate_diff_text = []
selected_rate_diff_text_change_pair = []
selected_rate_item_text = []

diff_proba_trans_list = []
proba_item_list = []

buy_stragety = []
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
        h_list[h_list.index(each)] = NAME[int(each)-1]

    rs = pd.DataFrame(h_list,columns=['历史记录'])
    js = pd.concat([ts,rs],axis=1)
    console.print('*' * 10)
    console.print(js.tail())
    console.print('*' * 10)

    # 先转换为时间数组
    last_record_timearray = time.strptime(latest_time, "%Y-%m-%d %H:%M:%S")
    # 转换为时间戳
    last_record_timeStamp = int(time.mktime(last_record_timearray))

    latest_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(last_record_timeStamp + 58))

    console.print(f'上次出货的时间：{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(last_record_timeStamp))}, 下次时间：{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(last_record_timeStamp + 58))}\n')
    present_time = last_record_timeStamp
    while present_time <= last_record_timeStamp + 58:
        present_time = int(time.time())
        if last_record_timeStamp + 58 - present_time < 6:
            console.print(f"倒计时：{last_record_timeStamp + 58 - present_time}秒")
        time.sleep(1)

    

    (in_put, _) = get_latest_result()
    if in_put not in ['1','2','3','4','5','6','7','8']:
        break
    else:
        history = history + in_put
    
    f = open(DIR+'./auto.csv', 'a', encoding='utf8')
    f.write(latest_time+','+NAME[int(in_put)-1]+'\n')
    f.close()


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

    for x in range(len(history)):
        
        # 将当前回合之前的历史结果，存入 current_history        
        current_history = history[:x+1]
        
        # 当 history的长度超过20时，始终只取其右侧的20位数据
        format_history = DataAnalytics(current_history,20).formatted()
        
        result.append(NAME[int(format_history[-1]) - 1])

        for each in position_list[-1]:
            if result[-1] in each:
                p = each[-1]        
    
        
        for each in diff_list[-1]:
            if result[-1] in each:
                d_num = each[-1]
                d = DIFF_TEXT[DIFF_NUM.index(d_num)]
        
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
        
        front_counter = selected_rate_diff_text[-20:].count('前')
        back_counter = selected_rate_diff_text[-20:].count('后')
    
        console.print(f'实际结果对应的预测位置(历史值)：\n{selected_rate_diff[-20:]}\n{selected_rate_diff_text[-20:]}\n均值：{mean(selected_rate_diff[-20:])}\n前排总数：{front_counter}\t后排总数：{back_counter}')
        console.print(f'排位变化：{selected_rate_diff_text_change_pair[-5:]}')
        logging.info("位置值历史：%s\n位置：%s\n均值：%s\n前排总数：%s\n后排总数：%s",selected_rate_diff[-20:], selected_rate_diff_text[-20:], mean(selected_rate_diff[-20:]), front_counter, back_counter)

        r = open(OUT_PATH+'openlog.log', 'a', encoding='utf8')
        r.write(str(latest_time)+'\n位置值历史：'+str(selected_rate_diff[-20:])+'\n位置：'+str(selected_rate_diff_text[-20:])+'\n均值：'+str(mean(selected_rate_diff[-20:]))+'\n前排总数：'+str(front_counter)+'\n后排总数：'+str(back_counter)+'\n')
        r.close()
    

    console.print(f'\n输入的结果：[red]{result[-1]}[/red]\n差分历史值：{result2[-20:]}')

    # 对Diff的选项值进行预分类
    diff_sort = copy.deepcopy(diff_list[-1])
    diff_sort.sort(key=lambda x: x[1], reverse=1)
    diff_sort_left = diff_sort[0:4]
    diff_sort_right = diff_sort[4:8]
    console.print(f'差分\n左侧选项：{diff_sort_left}\n右侧选项：{diff_sort_right}')
    if len(result2) >= 20:
        reg_n_r_proba_diff = load_rf_reg_model(DIR+'\\model\\rf_reg.m',result2[-20:])
        console.print(f'随机森林回归：差分的预测概率\n{reg_n_r_proba_diff}')

    # 在循环外，合并最后一回合的数据，构建成测试数据
    predict_data = []
    predict_data = counter_list[-1] + offset_list[-1]
    for each in position_list[-1]:
        predict_data.append(each[1])
    for each in diff_list[-1]:
        predict_data.append(each[1])        

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

    

    console.print(f'随机森林分类：物品的预测概率\n前排：{diff_proba_trans_list[0]}|{diff_proba_trans_list[1]}|{diff_proba_trans_list[4]}|{diff_proba_trans_list[5]}\n后排：{diff_proba_trans_list[2]}|{diff_proba_trans_list[3]}|{diff_proba_trans_list[6]}|{diff_proba_trans_list[7]}')  
    console.print('\n')
    console.print(f"[bold red]警告：大怪总数[/bold red]：{format_history.count('5') + format_history.count('6') + format_history.count('7') + format_history.count('8')} [red]应该至少有4个，否则押小容易出大[/red]")