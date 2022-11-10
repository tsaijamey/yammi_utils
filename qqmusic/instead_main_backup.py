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

STOCK = 2                                   # 预设的起始下注
BET_TIME = 3                               # 追投的次数
TOP_CHIPS = STOCK                           # 初始化的封顶下注量
for i in range(BET_TIME):
    TOP_CHIPS = int(TOP_CHIPS/0.2)          # 按照追投次数计算后的封顶下注量

# 每回合的数据列表，每回合都会变。
count_item          = []                    # 物品的统计
offset_item         = []
item_copd = []
last_copd = []

# 数据历史的列表，累计
position_history        = []
diff_history            = []
# @2022-10-29   废弃
# @2022-10-30   启用
real_position_history      = []
real_diff_history          = []
for i in range(20):
    position_history.append(0)
    diff_history.append(0)
    real_position_history.append(0)
    real_diff_history.append(0)


sum_history             = []
reg_predict_history         = []
reg_predict_infact_error    = []


analytics = []

clf_predict_history = []

start_timestamp = 0
item_history = []
time_history = []
record_history = []


high_low = []
item_high_low = []


'''测算胜率
'''
guess_counter = 0
not_pred_options = []
as_pred_options = []
not_pred_win_counter = 0
as_pred_win_counter = 0
as_pred_win_rate = 0
not_pred_win_rate = 0
upper = 0
lower = 0
pred_history = []
vote_count = 0
vote_ = 0
vote_win_count = 0
voted = False
BUY = False


# 预设变量
DIR = os.path.dirname(__file__)
if platform.system().lower() == 'windows':
    shot_path = DIR + './img/shot.png'
    record_path = DIR+'./auto2.csv'
    diff_model_path = DIR+'./model/reg_diff_21_20221028_seed10.m'
    pos_model_path = DIR+'./model/clf_all_15___20221028_seed10.m'
    rate_log = DIR+'./win_rate.log'
    buy_log = DIR+'./buy_log.log'
    high_low_log = DIR+'./high_low.log'
elif platform.system().lower() == 'linux':
    record_path = DIR+'/auto2.csv'
    diff_model_path = DIR+'/model/reg_diff_21_20221028_seed10.m'
    pos_model_path = DIR+'/model/clf_all_15___20221028_seed10.m'
    shot_path = DIR + '/img/shot.png'
    rate_log = DIR+'/win_rate.log'
    buy_log = DIR+'/buy_log.log'
    high_low_log = DIR+'/high_low.log'

if __name__ == '__main__':
    
    try:
        while True:
            read_buy = open(DIR+'./if_buy.txt', 'r', encoding='utf8')
            for line in read_buy:
                line = line.strip()
                if 'yes' in line:
                    BUY = True
                else:
                    BUY = False
            # 在获取结果时，容易因为点击意外导致列表为空，然后无法继续，因此增加这一段保障代码
            recent_result = []
            try_times = 0
            # while len(recent_result) == 0 or len(recent_result[0]) == 0:
            #     # inlib.getshot_via_adb('shot.png','shot2.png')
            #     # 返回值是 [[名称] , [[时间, 时间戳]]]
            #     try:
            #         recent_result = inlib.treasure_result_ocr(DIR + './img/shot.png')
            #     except Exception as e:
            #         print(e)


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
                record_history.append([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)), recent_result[0]])
                # 循环写入第一次识别的4个结果
                r = open(record_path, 'a', encoding='utf8')
                r.write(time_history[-1]+','+item_history[-1]+'\n')
                r.close()
                total = 1
            else:
                record_history.append([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)), recent_result[0]])
                if len(record_history) > 20:
                    record_history.pop(0)
                r = open(record_path, 'a', encoding='utf8')
                r.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) + ',' + recent_result[0] + '\n')
                r.close()
                total += 1

            
            console.print('[st]最新记录：[/st]')
            console.print(record_history[-3:])
            console.print(f'总数：{total}')            

            # 把出货历史，泛化成数字
            item_num_history = ''
            for each in record_history:
                if each[1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                    item_num_history += '{' + DICT[each[1]] + '}'
                else:
                    item_num_history += DICT[each[1]]
            if len(item_num_history) - item_num_history.count('{') - item_num_history.count('}') > 20:
                if item_num_history[0] == '{':
                    item_num_history = item_num_history[3:]
                else:
                    item_num_history = item_num_history[1:]
            console.print(f'近20回合记录： {item_num_history}')

            # 保存上一次的记录
            if len(item_copd) > 0:
                last_copd = item_copd

            # 开始计算各项值
            count_item              = inlib.item_sum(record_history)
            offset_item             = inlib.item_offset(count_item)
            item_copd               = inlib.position_sorted(offset_item,count_item)

            for each in item_copd:
                if record_history[-1][1] in each:
                    position_history.append(each[3])
            # posi值的历史，最多不超过20个。
            if len(position_history) > 20:
                position_history.pop(0)
            if len(position_history) > 0:
                for each in item_copd:
                    each[4] = each[3]-position_history[-1]

            # 适当时机，开始计算 diff值，计算的依据是最近2个posi值的差
            if len(position_history) >= 2:
                diff_history.append(position_history[-1] - position_history[-2])
            # diff值得历史，最多不超过20个。
            if len(diff_history) > 20:
                diff_history.pop(0)
            # 适当时机，显示 diff 值的历史
            if len(diff_history) > 0:
                console.print(f'DIFF历史值：{diff_history} | 历史值：{sum(diff_history)}')


            '''@2022-10-29  新思路
            用近期20回合的diff值，拟合一条曲线，预测下一个时间位置的值。
            每个diff值需要按顺序跟时间值组成(x,y)值
            设定 x = 时间戳， y = diff值
            '''
            time_diff_20 = []
            diff_20 = diff_history[-20:]
            for i in range(len(diff_20)):
                time_diff_20.append([i+1, diff_20[i]])
            if total > 3:
                df_header = ['time', 'result']                
                try:
                    time_diff_pd = pd.DataFrame(time_diff_20, columns=df_header)
                    prediction_20 = inlib.random_forest_reg_live(time_diff_pd,'result', [[21]])
                    console.print(f'RDM_REG预测(20)：[cyan]{prediction_20[0]}[/]')
                except Exception as e:
                    print('error')

            '''猜测区
            猜的策略：
            把每个回合的diff值，分成4个区，2大2小。
            只猜当 本回合diff值落在2小区域内的情况。
            猜的逻辑：当diff落在某2小区域时，猜下一回合出隔壁区域
            '''
            # 总结上局预测的情况
            if len(as_pred_options) != 0:
                if record_history[-1][1] in as_pred_options:
                    as_pred_win_counter += 1
                if record_history[-1][1] in not_pred_options:
                    not_pred_win_counter += 1

            # count last round earnings
            if as_pred_win_rate >= 0.6 and (upper == 1 or lower == 1):
                if record_history[-1][1] in as_pred_options:
                    vote_win_count += vote_/2*5
                    log_ = open(buy_log, 'a', encoding='utf8')
                    log_.write(record_history[-1][0] + ',' + record_history[-1][1] + ',' + str(int(vote_/2*5)) + ',' + str(vote_win_count) + '\n')
                    log_.close()
                    vote_ = 0
                else:
                    log_ = open(buy_log, 'a', encoding='utf8')
                    log_.write(record_history[-1][0] + ',' + record_history[-1][1] + ',' + str(vote_win_count) + '\n')
                    log_.close()
            if not_pred_win_rate >= 0.6 and (upper == 1 or lower == 1):
                if record_history[-1][1] in not_pred_options:
                    vote_win_count += vote_/2*5
                    log_ = open(buy_log, 'a', encoding='utf8')
                    log_.write(record_history[-1][0] + ',' + record_history[-1][1] + ',' + str(int(vote_/2*5)) + ',' + str(vote_win_count) + '\n')
                    log_.close()
                    vote_ = 0
                else:
                    log_ = open(buy_log, 'a', encoding='utf8')
                    log_.write(record_history[-1][0] + ',' + record_history[-1][1] + ',' + str(vote_win_count) + '\n')
                    log_.close()

            voted = False


            

            # 计算胜率
            if guess_counter > 0:
                as_pred_win_rate = round(as_pred_win_counter/guess_counter,2)
                not_pred_win_rate = round(not_pred_win_counter/guess_counter,2)
                console.print(f"按预测 胜率: {as_pred_win_counter} | {guess_counter}，[cyan]{str(as_pred_win_rate)}[/]")
                console.print(f"按补充 胜率: {not_pred_win_counter} | {guess_counter}，[cyan]{str(not_pred_win_rate)}[/]")

            if record_history[-1][1] in as_pred_options:
                pred_history.append('预测')
            elif record_history[-1][1] in not_pred_options:
                pred_history.append('补充')
            else:
                pred_history.append('忽略')
            
            
            if len(pred_history) > 20:
                pred_history.pop(0)
            if len(pred_history) >= 1:
                print(pred_history)

            # record the rate per hour.
            if (start_timestamp % (60 * 60) <= 60 or start_timestamp % (60 * 60) >= (60*60-59)) and guess_counter > 0:
                record_rate = open(rate_log, 'a', encoding='utf8')
                record_rate.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) + '按预测 胜率: ' + str(as_pred_win_counter) + '|' + str(guess_counter) + ', ' + str(as_pred_win_rate) + '\n')
                record_rate.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) + '按补充 胜率: ' + str(not_pred_win_counter) + '|' + str(guess_counter) + ', ' + str(not_pred_win_rate) + '\n')
                record_rate.write(f'此时已下注：{vote_count}音符\n')
                record_rate.write(f'此时已回收：{vote_win_count}音符\n')
                record_rate.write('*' * 20 + '\n')
                record_rate.close()
                # 重置下注相关的数据
                console.print(f'[red]整点重置数据[/]')
                guess_counter = 0
                not_pred_options = []
                as_pred_options = []
                not_pred_win_counter = 0
                as_pred_win_counter = 0
                as_pred_win_rate = 0
                not_pred_win_rate = 0


            # 启动后3回合内不进行预测
            if total > 3:
                # 近20回合的大怪总数超过6不进行预测
                # if inlib.item_sum_V(record_history)[4] <= 5:
                bigger = []
                smaller = []
                bigger_2 = []
                smaller_2 = []
                if prediction_20[0] >= item_copd[3][4]:
                    upper = 1
                else:
                    upper = 0
                if prediction_20[0] <= item_copd[4][4]:
                    lower = 1
                else:
                    lower = 0
                
                if upper == 1:
                    as_pred_options = [item_copd[2][0], item_copd[3][0]]
                    not_pred_options = [item_copd[4][0], item_copd[5][0]]
                    console.print(f'{prediction_20[0]}在上区，按预测选：[red]{as_pred_options}[/]')
                    console.print(f'{prediction_20[0]}在上区，按补充选：[red]{not_pred_options}[/]')
                    guess_counter += 1
                elif lower == 1:                        
                    as_pred_options = [item_copd[4][0], item_copd[5][0]]
                    not_pred_options = [item_copd[2][0], item_copd[3][0]]
                    console.print(f'{prediction_20[0]}在下区，按预测选：[red]{as_pred_options}[/]')
                    console.print(f'{prediction_20[0]}在下区，按补充选：[red]{not_pred_options}[/]')
                    guess_counter += 1
                else:
                    console.print('[blue]本局忽略[/]')
                    not_pred_options = []
                    as_pred_options = []

            # 只在胜率大于50，且上一次结果不为大时 实施
            if as_pred_win_rate >= 0.6 and (upper == 1 or lower == 1) and record_history[-1][1] not in ['架子鼓','竖琴','萨克斯风','圆号'] and inlib.if_item_sum_balance(count_item[:4]) == False:
            # if as_pred_win_rate - not_pred_win_rate > 0.2 and (upper == 1 or lower == 1):
                if vote_ == 0 or vote_ == TOP_CHIPS:
                    vote_ = STOCK
                else:
                    vote_ = int(vote_/0.2)
                vote_count += vote_
                console.print(f'模拟下注：{as_pred_options} + {str(vote_)}音符(各{str(vote_/2)})')
                log_ = open(buy_log, 'a', encoding='utf8')
                log_.write(as_pred_options[0] + '|' + as_pred_options[1] + ',' + str(vote_) + ',')
                log_.close()
                if BUY == True:
                    by.buy(as_pred_options[0], as_pred_options[1], int(vote_/2))
                    voted = True
                else:
                    voted = False
            elif not_pred_win_rate >= 0.6 and (upper == 1 or lower == 1) and record_history[-1][1] not in ['架子鼓','竖琴','萨克斯风','圆号'] and inlib.if_item_sum_balance(count_item[:4]) == False:
            # elif not_pred_win_rate - as_pred_win_rate > 0.2 and (upper == 1 or lower == 1):
                if vote_ == 0 or vote_ == TOP_CHIPS:
                    vote_ = STOCK
                else:
                    vvote_ = int(vote_/0.2)
                vote_count += vote_
                console.print(f'模拟下注：{not_pred_options} + {str(vote_)}音符(各{str(vote_/2)})')
                log_ = open(buy_log, 'a', encoding='utf8')
                log_.write(not_pred_options[0] + '|' + not_pred_options[1] + ',' + str(vote_) + ',')
                log_.close()
                if BUY == True:
                    by.buy(not_pred_options[0], not_pred_options[1], int(vote_/2))                        
                    voted = True
                else:
                    voted = False
            else:
                pass
            
            if as_pred_win_rate<0.6 and not_pred_win_rate<0.6:
                if abs(as_pred_win_rate - not_pred_win_rate) < 0.19:
                    count_a = pred_history.count('预测')
                    count_b = pred_history.count('补充')
                    if count_a == count_b:
                        pass
                    elif count_a > count_b:
                        pass
                    elif count_b > count_a:
                        pass

            
            # 根据Diff值的预测：
            reg_predict = inlib.load_rf_reg_model(DIR+'\\model\\reg_8_20221028_seed10.m',diff_history).tolist()[0]
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
                if record_history[-1][1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                    reg_predict_infact_error.append(str(diff_history[-1] - reg_predict_history[-2]))
                else:
                    reg_predict_infact_error.append(diff_history[-1] - reg_predict_history[-2])

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
            console.print(f'起注：{STOCK} | 封顶：{TOP_CHIPS}')

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


            inlib.wait_next(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) , 58)
            start_timestamp += 58
            if voted == True:
                time.sleep(10)
                by.close_popup()

    except Exception as e:
        print(e,traceback.format_exc())

        # unsupported operand type(s) for -: 'int' and 'list'