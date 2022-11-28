'''新版的主程序
'''


# 引用库
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
console = Console(theme=Theme({
    "pre": "bold purple blink",  # predict
    "re": "cyan bold blink",   # result
    "st": "#e3e3e3",  # statement
    "wa": "red bold",   # warning
    "bg": "#a8a8a8",
    }))
import time
import datetime
import os
import traceback
import pandas as pd
import numpy as np

import platform
import instead_buy as by


# 自定义库
import instead_lib as inlib

# 预定义变量
DIR = os.path.dirname(__file__)             # 当前文件所在的目录
DICT = {
    '钢琴': '1',
    '小提琴': '2',
    '吉他': '3',
    '贝斯': '4',
    '架子鼓': '5',
    '竖琴': '6',
    '萨克斯风': '7',
    '圆号': '8',
}                                           # 各个乐器对应的编号
DIFF_DICT = {
    '负七': -7,
    '负六': -6,
    '负五': -5,
    '负四': -4,
    '负三': -3,
    '负二': -2,
    '负一': -1,
    '零':   0,
    '一':   1,
    '二':   2,
    '三':   3,
    '四':   4,
    '五':   5,
    '六':   6,
    '七':   7,
}                                           # 各个Diff值的中文与数字表达对应关系


start_timestamp = 0
item_history = []
time_history = []
records = []

# 每回合的数据列表，每回合都会变。
count_item          = []                    # 物品的统计
offset_item         = []
item_copd = []
last_copd = []

# 数据历史的列表，累计
posis   = []
diffs   = []
level   = []
history_length = int(60*60/58)
for i in range(history_length):
    posis.append(0)
    diffs.append(0)
    level.append(2)



reg_predict_history         = []
reg_predict_infact_error    = []

pred_seeds_list = []
seed = 90



'''测算胜率
'''
guess = 0
not_pred = []
as_pred = []
not_win_num = 0
as_win_num = 0
as_win_rate = 0
not_win_rate = 0
upper = 0
lower = 0
preds = []
vote_count = 0
vote_ = 0
vote_win_count = 0
voted = False
try_buy = False
BUY = False

switch = 1
buy_switch = 0
round_gap = 0
logical = 'a'
preds_head = ''


# 预设变量
DIR = os.path.dirname(__file__)
if platform.system().lower() == 'windows':
    shot_path = DIR + './img/shot.png'
    record_path = DIR+'./auto2.csv'
    diffs_log = DIR+'./diff.csv'
    diff_model_path = DIR+'./model/reg_diff_21_20221028_seed10.m'
    pos_model_path = DIR+'./model/clf_all_15___20221028_seed10.m'
    rate_log = DIR+'./win_rate.log'
    buy_log = DIR+'./buy_log.log'
    level_log = DIR+'./high_low.log'
    record_msg = DIR+'./record_msg.log'
    if_buy = DIR+'./if_buy.txt'
elif platform.system().lower() == 'linux':
    record_path = DIR+'/auto2.csv'
    diff_model_path = DIR+'/model/reg_diff_21_20221028_seed10.m'
    pos_model_path = DIR+'/model/clf_all_15___20221028_seed10.m'
    shot_path = DIR + '/img/shot.png'
    rate_log = DIR+'/win_rate.log'
    buy_log = DIR+'/buy_log.log'
    level_log = DIR+'/high_low.log'
    record_msg = DIR+'/record_msg.log'
    if_buy = DIR+'/if_buy.txt'
    diffs_log = DIR+'/diff.csv'

diffs_rec = open(diffs_log, 'a', encoding='utf8')
diffs_rec.write('\n')
diffs_rec.close()

if __name__ == '__main__':
    
    try:
        while True:
            read_buy = open(if_buy, 'r', encoding='utf8')
            for line in read_buy:
                line = line.strip()
                if 'yes' in line:
                    BUY = True
                else:
                    BUY = False
            # 在获取结果时，容易因为点击意外导致列表为空，然后无法继续，因此增加这一段保障代码

            STOCK, _, RATE, TOP_STOCK   = inlib.init_stock()
            recent_result = []
            try_times = 0


            while len(recent_result) == 0 or len(recent_result[0]) == 0:
                inlib.screenshot_via_adb('shot.png')
                try:
                    recent_result = inlib.treasure_result_ocr(shot_path)
                except Exception as e:
                    print(e)

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
                if len(records) > 20:
                    records.pop(0)
                r = open(record_path, 'a', encoding='utf8')
                r.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) + ',' + recent_result[0] + '\n')
                r.close()
                total += 1

            
            console.print('[st]最新记录：[/st]')
            console.print(records[-3:])
            console.print(f'总数：{total}')            

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

            # 保存上一次的记录
            if len(item_copd) > 0:
                last_copd = item_copd

            # 开始计算各项值
            count_item              = inlib.item_sum(records)
            offset_item             = inlib.item_offset(count_item)
            item_copd               = inlib.position_sorted(offset_item,count_item)

            # 还是需要基于固定的值进行记录，而不是动态的值
            if len(last_copd) > 0:
                for each in last_copd:
                    if records[-1][1] in each:
                        posis.append(each[3])
            else:
                for each in item_copd:
                    if records[-1][1] in each:
                        posis.append(each[3])
            
            # 下一回合各乐器的diff值
            if len(posis) > 0:
                for each in item_copd:
                    each[4] = each[3]-posis[-1]

            # 计算 diff值
            if len(posis) >= 2:
                diffs.append(posis[-1] - posis[-2])
                if abs(diffs[-1]) <= 1:
                    level.append(0)
                else:
                    level.append(1)

            # 不超过指定个数。
            if len(diffs) > history_length:
                posis.pop(0)
                diffs.pop(0)
                level.pop(0)

            console.print(f'DIFF：{diffs[-20:]} | 历史值：{sum(diffs[-5:])}->{sum(diffs[-4:])}')
            console.print(f'LEVEL：{level[-20:]}')


            '''@2022-10-29  新思路
            用近期20回合的diff值，拟合一条曲线，预测下一个时间位置的值。
            每个diff值需要按顺序跟时间值组成(x,y)值
            设定 x = 时间戳， y = diff值
            '''
            time_diff = []
            for i in range(len(diffs)):
                time_diff.append([i+1, diffs[i]])
            if total > 3:
                '''
                通过新一轮的diff值，找到100个seed中与之差距最小的seed，用于本次预测。
                '''
                df_header = ['time', 'result']
                try:
                    time_diff_pd = pd.DataFrame(time_diff, columns=df_header)
                    prediction_sd10 = inlib.random_forest_reg_live(time_diff_pd,'result', int(len(diffs)+1))
                    console.print(f'[pre]RDN_SD10：[/][cyan]{round(prediction_sd10[0],5)}[/]')
                except Exception as e:
                    print('error')

            
            

            '''猜测区
            猜的策略：
            把每个回合的diff值，分成4个区，2大2小。
            只猜当 本回合diff值落在2小区域内的情况。
            猜的逻辑：当diff落在某2小区域时，猜下一回合出隔壁区域
            '''
            # 总结上局预测的情况
            if len(as_pred) != 0:
                if records[-1][1] in as_pred:
                    as_win_num += 1
                if records[-1][1] in not_pred:
                    not_win_num += 1

            # 计算上回合的收益
            mgs = ''
            if buy_switch == 1:
                if records[-1][1] in buy_option[0:2]:
                    vote_win_count += votes[0] * 5
                    msg = '下注结果：【命中】。' + records[-1][0] + ' ' + records[-1][1] + '。本次回收：' + str(votes[0] * 5) + '。总投入：' + str(vote_count) + '，总回收：' + str(vote_win_count) + '，实际收益：' + str(int(vote_win_count*0.635 - vote_count*0.92)) + '，开关=' + str(switch)
                    inlib.send_wechat('下注结果', msg)
                    log_ = open(buy_log, 'a', encoding='utf8')
                    log_.write(msg + '\n')
                    log_.write('*'*40 + '\n')
                    log_.close()
                    vote_ = 0
                elif records[-1][1] in buy_option[2:4]:
                    win = 0
                    if votes[2] == 0:
                        msg = '下注结果：【命中但未押】。' + records[-1][0] + ' ' + records[-1][1] + '。本次回收：0。' + '，总投入：' + str(vote_count) + '，总回收：' + str(vote_win_count) + '，实际收益：' + str(int(vote_win_count*0.635 - vote_count*0.92)) + '，开关=' + str(switch)
                        inlib.send_wechat('下注结果', msg)
                        log_ = open(buy_log, 'a', encoding='utf8')
                        log_.write(msg + '\n')
                        log_.write('*'*40 + '\n')
                        log_.close()
                    if votes[2] != 0:
                        if records[-1][1] == '架子鼓':
                            win = int(votes[0]/4 * 10)
                        elif  records[-1][1] == '竖琴':
                            win = int(votes[0]/4 * 20)
                        elif  records[-1][1] == '萨克斯风':
                            win = int(votes[0]/4 * 25)
                        elif  records[-1][1] == '圆号':
                            win = int(votes[0]/4 * 35)
                        vote_win_count += win
                        msg = '下注结果：【命中】。' + records[-1][0] + ' ' + records[-1][1] + '。本次回收：' + str(win) + '。总投入：' + str(vote_count) + '，总回收：' + str(vote_win_count) + '，实际收益：' + str(int(vote_win_count*0.635 - vote_count*0.92)) + '，开关=' + str(switch)
                        inlib.send_wechat('下注结果', msg)
                        log_ = open(buy_log, 'a', encoding='utf8')
                        log_.write(msg + '\n')
                        log_.write('*'*40 + '\n')
                        log_.close()
                        vote_ = 0
                elif records[-1][1] not in buy_option:
                    if switch == 1:
                        switch = 2
                    elif switch == 2:
                        switch = 1
                    round_gap = 3
                    msg = '下注结果：【未命中】。' + records[-1][0] + ' ' + records[-1][1] + '。本次回收：0。' + '，总投入：' + str(vote_count) + '，总回收：' + str(vote_win_count) + '，实际收益：' + str(int(vote_win_count*0.635 - vote_count*0.92)) + '，开关=' + str(switch)
                    inlib.send_wechat('下注结果', msg)
                    log_ = open(buy_log, 'a', encoding='utf8')
                    log_.write(msg + '\n')
                    log_.write('*'*40 + '\n')
                    log_.close()
                    

                console.print(msg)

            elif logical == 'a':
                pass

            voted = False
            try_buy = False
            buy_switch = 0
            buy_option = []
            
            

            # 计算胜率
            if guess > 0:
                as_win_rate = round(as_win_num/guess,2)
                not_win_rate = round(not_win_num/guess,2)
                console.print(f"【预测】胜率: {as_win_num}/{guess}，[green]{as_win_rate}[/]【补充】胜率: {not_win_num}/{guess}，[green]{not_win_rate}[/]")


            if records[-1][1] in as_pred:
                preds.append('预测')
            elif records[-1][1] in not_pred:
                preds.append('补充')
            else:
                preds.append('忽略')
            
            if len(preds) > 20:
                preds_head = preds[0]
                preds.pop(0)
            if len(preds) >= 1:
                console.print(f'前：{preds[:5]}...后：{preds[-5:]}。预测={preds.count("预测")}，补充={preds.count("补充")}')

            # record the rate per hour.
            if (start_timestamp % (60 * 60) <= 30 or start_timestamp % (60 * 60) >= (60*60-30)) and guess > 0:
                record_rate = open(rate_log, 'a', encoding='utf8')
                record_rate.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) + '按预测 胜率: ' + str(as_win_num) + '|' + str(guess) + ', ' + str(as_win_rate) + '\n')
                record_rate.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) + '按补充 胜率: ' + str(not_win_num) + '|' + str(guess) + ', ' + str(not_win_rate) + '\n')
                record_rate.write(f'此时已下注：{vote_count}音符\n')
                record_rate.write(f'此时已回收：{vote_win_count}音符\n')
                record_rate.write('*' * 20 + '\n')
                record_rate.close()
                # 重置下注相关的数据
                console.print(f'[red]整点重置数据[/]')
                guess = 0
                not_pred = []
                as_pred = []
                not_win_num = 0
                as_win_num = 0
                as_win_rate = 0
                not_win_rate = 0


            # 启动后3回合内不进行预测
            if total > 3:
                # 近20回合的大怪总数超过6不进行预测
                # if inlib.item_sum_V(record_history)[4] <= 5:
                bigger = []
                smaller = []
                bigger_2 = []
                smaller_2 = []
                not_pred = []
                as_pred = []
                if prediction_sd10[0] >= (item_copd[3][4] + item_copd[4][4])/2:
                    upper = 1
                else:
                    upper = 0
                if prediction_sd10[0] < (item_copd[3][4] + item_copd[4][4])/2:
                    lower = 1
                else:
                    lower = 0
                
                if upper == 1:
                    as_pred = [item_copd[2][0], item_copd[3][0], item_copd[0][0], item_copd[1][0]]
                    not_pred = [item_copd[4][0], item_copd[5][0], item_copd[6][0], item_copd[7][0]]
                    console.print(f'{prediction_sd10[0]}在上区，按预测选：[red]{as_pred}[/]')
                    console.print(f'{prediction_sd10[0]}在上区，按补充选：[red]{not_pred}[/]')
                    guess += 1
                elif lower == 1:                        
                    as_pred = [item_copd[4][0], item_copd[5][0], item_copd[6][0], item_copd[7][0]]
                    not_pred = [item_copd[2][0], item_copd[3][0], item_copd[0][0], item_copd[1][0]]
                    console.print(f'{prediction_sd10[0]}在下区，按预测选：[red]{as_pred}[/]')
                    console.print(f'{prediction_sd10[0]}在下区，按补充选：[red]{not_pred}[/]')
                    guess += 1
                else:
                    console.print('[blue]本局忽略[/]')
                    

            # 只在胜率大于50，且上一次结果不为大，且四个小乐器的数量不存在相同 时 实施
            # 增加时间限制，去掉凌晨和下午的时间。
            console.print(f'今日秒数：{(start_timestamp+8*60*60) % (24*60*60)}')
            # if (start_timestamp+8*60*60) % (24*60*60) <= (6*60*60) or ((start_timestamp+8*60*60) % (24*60*60) >= (10*60*60) and (start_timestamp+8*60*60) % (24*60*60) <= (18*60*60)):
            
            # 时段条件
            if (start_timestamp+8*60*60) % (24*60*60) < (0*60*60):
                console.print(f'本时段不进行模拟')
            else:
                # 购买条件
                comment = ''
                if logical == 'b':
                    if round_gap != 0:
                        round_gap -= 1
                        console.print(f'Round Gap = {round_gap}')
                    else:
                        if as_win_rate > 0.6 or not_win_rate > 0.6:
                            if records[-1][1] not in ['架子鼓','竖琴','萨克斯风','圆号'] and inlib.if_item_sum_middle_balance(count_item[:4]) == False and guess >= 4:
                                # 购买许可
                                buy_switch = 1
                                if as_win_rate > 0.6 and switch == 1:
                                    buy_option = as_pred
                                    comment = '条件：大于0.6阈值。开关：正向。'
                                if not_win_rate > 0.6 and switch == 1:
                                    buy_option = not_pred
                                    comment = '条件：大于0.6阈值。开关：正向。'
                                if as_win_rate > 0.6 and switch == 2:
                                    buy_option = not_pred
                                    comment = '条件：大于0.6阈值。开关：反向。'
                                if not_win_rate > 0.6 and switch == 2:
                                    buy_option = as_pred
                                    comment = '条件：大于0.6阈值。开关：反向。'
                        elif abs(diffs[-4]) > 1 and abs(diffs[-3]) <= 1 and abs(diffs[-2]) > 1 and abs(diffs[-1]) <= 1:
                            for i in range(2,6):
                                if switch == 1:
                                    if abs(item_copd[i][4]) <= 1:
                                        buy_option.append(item_copd[i][0])
                                        comment = '条件：大小大小。开关：正向。'
                                if switch == 2:
                                    if abs(item_copd[i][4]) > 1:
                                        buy_option.append(item_copd[i][0])
                                        comment = '条件：大小大小。开关：反向。'
                            if len(buy_option) == 2:
                                # 购买许可
                                buy_switch = 1
                                buy_option = []
                                if switch == 1:
                                    if abs(item_copd[3][4]) <= 1:                                
                                        buy_option = [item_copd[2][0],item_copd[3][0],item_copd[0][0],item_copd[1][0]]
                                    if abs(item_copd[4][4]) <= 1:
                                        buy_option = [item_copd[4][0],item_copd[5][0],item_copd[6][0],item_copd[7][0]]
                                if switch == 2:
                                    if abs(item_copd[3][4]) > 1:
                                        buy_option = [item_copd[2][0],item_copd[3][0],item_copd[0][0],item_copd[1][0]]
                                    if abs(item_copd[4][4]) > 1:
                                        buy_option = [item_copd[4][0],item_copd[5][0],item_copd[6][0],item_copd[7][0]]
                        elif (not_win_rate <= 0.6 and as_win_rate <= 0.6) and inlib.if_item_sum_middle_balance(count_item[:4]) == False and guess >= 4:
                            if preds[-4:] == ['预测','预测','预测','补充']:
                                # 购买许可
                                buy_switch = 1
                                if switch == 1:
                                    buy_option = not_pred
                                    comment = '条件：小于0.6阈值。开关：正向。'
                                if switch == 2:
                                    buy_option = as_pred
                                    comment = '条件：小于0.6阈值。开关：反向。'
                            if preds[-4:] == ['补充','补充','补充','预测']:
                                # 购买许可
                                buy_switch = 1
                                if switch == 1:
                                    buy_option = as_pred
                                    comment = '条件：小于0.6阈值。开关：正向。'
                                if switch == 2:
                                    buy_option = not_pred
                                    comment = '条件：小于0.6阈值。开关：反向。'
                        elif guess < 4:
                            console.print(f'判断基数不足。')
                        else:
                            reason = ''
                            if as_win_rate < 0.6 and not_win_rate < 0.6:
                                reason = reason + '胜率不达标。'
                            if records[-1][1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                                reason = reason + '前一回合出大。'
                            if inlib.if_item_sum_middle_balance(count_item[:4]) == True:
                                reason = reason + '存在相同数量的物品。'
                            console.print(f'[wa]不符合下注条件：{reason}[/wa]')
                elif logical == 'a':
                    pass
                    if preds.count("预测") == preds.count("补充") and preds.count("预测") == 10:
                        buy_switch = 1
                        if preds[0] == '预测':
                            buy_option = as_pred
                            comment = '条件：预测补充相等，头为预测。'
                        elif preds[0] == '补充':
                            buy_option = not_pred
                            comment = '条件：预测补充相等，头为补充。'
                    elif preds.count("预测") > preds.count("补充"):
                        count_last_preds = preds[:-1]
                        count_last_preds.append(preds_head)
                        console.print(f'上回合：预测={count_last_preds.count("预测")} 补充={count_last_preds.count("补充")}')
                        if count_last_preds.count("预测") < preds.count("预测"):
                            print('预测还在继续增长')
                            if preds[0] == '预测':
                                buy_switch = 1
                                buy_option = as_pred
                                comment = '条件：预测大于补充，预测增长，头为预测。'
                            else:
                                pass
                        elif count_last_preds.count("预测") > preds.count("预测"):
                            print('预测在衰退')
                        elif count_last_preds.count("预测") == preds.count("预测"):
                            print('与上回合持平')
                    elif preds.count("预测") < preds.count("补充"):
                        count_last_preds = preds[:-1]
                        count_last_preds.append(preds_head)
                        console.print(f'上回合：预测={count_last_preds.count("预测")} 补充={count_last_preds.count("补充")}')
                        if count_last_preds.count("补充") < preds.count("补充"):
                            print('补充还在继续增长')
                            if preds[0] == '补充':
                                buy_switch = 1
                                buy_option = not_pred
                                comment = '条件：预测小于补充，补充增长，头为补充。'
                            else:
                                pass
                        elif count_last_preds.count("补充") > preds.count("补充"):
                            print('补充在衰退')
                        elif count_last_preds.count("补充") == preds.count("补充"):
                            print("与上回合持平")
                    else:
                        console.print('预测量不足。')

                if buy_switch == 1:
                    if vote_ == 0 or vote_ == TOP_STOCK:
                        vote_ = STOCK
                    else:
                        vote_ = int(vote_/RATE)
                    vote_count += vote_
                    console.print(comment)
                    pieces = []
                    if DICT[buy_option[2]] == 5:
                        pieces.append(10)
                    if DICT[buy_option[2]] == 6:
                        pieces.append(20)
                    if DICT[buy_option[2]] == 7:
                        pieces.append(25)
                    if DICT[buy_option[2]] == 8:
                        pieces.append(35)
                    if DICT[buy_option[3]] == 5:
                        pieces.append(10)
                    if DICT[buy_option[3]] == 6:
                        pieces.append(20)
                    if DICT[buy_option[3]] == 7:
                        pieces.append(25)
                    if DICT[buy_option[3]] == 8:
                        pieces.append(35)

                    if vote_ == 2:
                        votes = [1,1,0,0]
                    else:
                        votes = [int(vote_/10*4),int(vote_/10*4),int(vote_/10),int(vote_/10)]
                    console.print(f'模拟下注：{buy_option} | {votes}音符')
                    msg = ''
                    msg = msg + comment
                    msg = msg + '模拟下注：' + buy_option[0] + ',' + str(votes[0]) + ' | ' + buy_option[1] + ',' + str(votes[1]) + ' | ' + buy_option[2] + ',' + str(votes[2]) + ' | ' + buy_option[3] + ',' + str(votes[3]) + ' | '
                    log_ = open(buy_log, 'a', encoding='utf8')
                    log_.write(msg)
                    log_.close()
                    
                    inlib.send_wechat('模拟下注', msg)
                    try_buy = True

                    if BUY == True:
                        time.sleep(5)
                        by.buy_4(buy_option,votes)
                        voted = True
                    else:
                        voted = False

            
            # 根据Diff值的预测：
            reg_predict = inlib.load_rf_reg_model(DIR+'\\model\\reg_8_20221028_seed10.m',diffs[-20:]).tolist()[0]
            if reg_predict == 0:
                reg_predict_to_int = 0
            else:
                reg_predict_to_int = int(reg_predict)

            reg_predict_history.append(reg_predict_to_int)

            # 预测的历史，只保留最近的21个。
            if len(reg_predict_history) > 21:
                reg_predict_history.pop(0)

            # 计算 预测diff 和 实际diff 的误差，存入 reg_predict_infact_error
            # 用于计算的 预测diff 来自 reg_predict_history[-2]
            if len(reg_predict_history) >= 2:
                if records[-1][1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                    reg_predict_infact_error.append(str(diffs[-1] - reg_predict_history[-2]))
                else:
                    reg_predict_infact_error.append(diffs[-1] - reg_predict_history[-2])

                if len(reg_predict_infact_error) > 20:
                    reg_predict_infact_error.pop(0)
                console.print(f'[st]预测与实际结果的误差量（最后一个值，是上一次“预测”vs“实际”的结果）[/st]')
                
                reg_predict_infact_error_int = []
                for each in reg_predict_infact_error:
                    reg_predict_infact_error_int.append(int(each))
                    
                console.print(f'{reg_predict_infact_error} | [wa]{sum(reg_predict_infact_error_int)}[/wa]')
                console.print(f'[st]历史预测值[/st]')
                console.print(f'[re]{reg_predict_history[:-1]}[/re]')
                console.print(f'[st]本次预测值[/st]：[pre]{reg_predict_history[-1]}[/pre]')
                right = 0
                left  = 0
                for each in reg_predict_infact_error_int[-5:]:
                    if each > 0:
                        right += 1
                    elif each < 0:
                        left  += 1
                if right > left and right >= 3:
                    console.print(f'[pre]下回合 [u]出现的DIFF值[/u] 可能比 {reg_predict_history[-1]} 小[/pre]')
                elif left > right and left >= 3:
                    console.print(f'[pre]下回合 [u]出现的DIFF值[/u] 可能比 {reg_predict_history[-1]} 大[/pre]')
                elif right <= 2 and left <= 2:
                    console.print(f'[pre]暂无法判断，观望[/pre]')

            console.print(f'模拟总计投入：{vote_count} 音符')
            console.print(f'模拟总计回收：{vote_win_count} 音符')
            console.print(f'起注：{STOCK} | 封顶：{TOP_STOCK}')

            # 格式化展示，方便查看数值
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("物品(隐藏大)", style="dim", width=12)
            table.add_column("4 - 差分", justify="right", width=12)
            table.add_column("1 - 数量", justify="right", width=12)
            table.add_column("2 - 偏移", justify="right", width=12)
            table.add_column("3 - 位序", justify="right", width=12)
            for i in range(8):
                if i in [2,3,4,5]:
                    table.add_row(
                        item_copd[i][0],
                        '[cyan]'+str(item_copd[i][4]),
                        '[cyan]'+str(item_copd[i][1]),
                        '[cyan]'+str(item_copd[i][2]),
                        '[cyan]'+str(item_copd[i][3]),
                    )
                if i in [0,1,6,7]:
                    table.add_row(
                        item_copd[i][0],
                        str(item_copd[i][4]),
                        str(item_copd[i][1]),
                        str(item_copd[i][2]),
                        str(item_copd[i][3]),
                    )

            console.print(table)
            
            # 存一份diff数据用来训练
            diffs_rec = open(diffs_log, 'a', encoding='utf8')
            level_rec = open(level_log, 'a', encoding='utf8')
            for i in range(history_length):
                if i != history_length-1:
                    diffs_rec.write(str(diffs[i])+',')
                    level_rec.write(str(level[i])+',')
                else:
                    diffs_rec.write(str(diffs[i])+'\n')
                    level_rec.write(str(level[i])+'\n')
            diffs_rec.close()
            level_rec.close()

            inlib.wait_next(start_timestamp, 58)
            start_timestamp += 58
            if voted == True:
                time.sleep(10)
                by.close_popup()

    except Exception as e:
        print(e,traceback.format_exc())

        # unsupported operand type(s) for -: 'int' and 'list'