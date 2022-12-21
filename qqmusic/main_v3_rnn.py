'''新版的主程序
'''
# 引用库
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
console = Console()
import time
import os
import traceback
import platform

# 自定义库
import instead_lib as inlib
import instead_buy as by
import pad_control as pdc

import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.optimizers import Adam
from keras import layers
import keras.metrics as keras_metrics

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
def windowed_df_to_date_X_y(windowed_dataframe):
    df_as_np = windowed_dataframe.to_numpy()

    dates = df_as_np[:, 0]
    middle_matrix = df_as_np[:, 1:-1]
    X = middle_matrix.reshape((len(dates), middle_matrix.shape[1], 1))

    Y = df_as_np[:, -1]

    return dates, X.astype(np.float32), Y.astype(np.float32)



# 预定义变量
header = ['time']
for i in range(20):
    header.append('col_'+str(i+1))
header.append('result')
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
CONFIGS = {
    'bullet':'0',
    'buy':'no',
    'chat':'no',
}


start_timestamp = 0
item_history = []
time_history = []
records = []
total = 0

# 每回合的数据列表，每回合都会变。
count_item          = []                    # 物品的统计
offset_item         = []
item_copd = []
last_copd = []

# 数据历史的列表，累计
posis   = []
diffs   = []
diff2   = []
# history_length = int(60*60/58)
history_length = 21
for i in range(history_length):
    posis.append(0)
    diffs.append(0)
reg_preds         = []
pred_bias_str    = []
invest = 0
chips = 0
income = 0
voted = False
InVest_Agreed = 0
win_records=[]
win_times = 0


# 预设变量
DIR = os.path.dirname(__file__)
# 获得当前日期
current_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
if platform.system().lower() == 'windows':
    shot_path = DIR + './img/shot.png'
    record_path = DIR+'./record-' + current_date + '.csv'
    diffs_log = DIR+'./diff-' + current_date + '.csv'
    rate_log = DIR+'./win_rate-' + current_date + '.log'
    buy_log = DIR+'./buy_log-' + current_date + '.log'
    if_buy = DIR+'./if_buy.txt'
    diff_model_path = DIR+'./model/reg_5_20221220_seed10.m'
elif platform.system().lower() == 'linux':
    shot_path = DIR + '/img/shot.png'
    record_path = DIR+'/auto2-' + current_date + '.csv'
    diffs_log = DIR+'/diff-' + current_date + '.csv'
    rate_log = DIR+'/win_rate-' + current_date + '.log'
    buy_log = DIR+'/buy_log-' + current_date + '.log'
    if_buy = DIR+'/if_buy.txt'    
    diff_model_path = DIR+'/model/reg_5_20221220_seed10.m'

diffs_rec = open(diffs_log, 'a', encoding='utf8')
diffs_rec.write('\n')
diffs_rec.close()

def write_config(dict:dict,path:str):
    r = open(path, 'w', encoding='utf8')
    r.write('bullet='+dict['bullet']+'\n')
    r.write('buy='+dict['buy']+'\n')
    r.write('chat='+dict['chat']+'\n')
    r.close()

if __name__ == '__main__':
    try:
        # pdc.main()
        while True:
            read_buy = open(if_buy, 'r', encoding='utf8')
            # 读取购买配置
            for line in read_buy:
                line = line.strip()
                key,value = line.split('=')
                CONFIGS[key] = value
                
            # 在获取结果时，容易因为点击意外导致列表为空，然后无法继续，因此增加这一段保障代码

            STOCK, _, RATE, TOP_STOCK   = inlib.init_stock()
            recent_result = []
            try_times = 0

            if total % 100 == 0:
                pdc.main()
                start_timestamp = 0
                item_history = []
                time_history = []
                records = []
                total = 0

                # 每回合的数据列表，每回合都会变。
                count_item          = []                    # 物品的统计
                offset_item         = []
                item_copd = []
                last_copd = []

                # 数据历史的列表，累计
                posis   = []
                diffs   = []
                diff2   = []
                for i in range(history_length):
                    posis.append(0)
                    diffs.append(0)
                reg_preds         = []
                pred_bias_str    = []
                chips = 0
                voted = False
                InVest_Agreed = 0
                win_records=[]
                win_times = 0
                CONFIGS['buy'] = 'no'
                write_config(CONFIGS,if_buy)

            while len(recent_result) == 0 or len(recent_result[0]) == 0:
                inlib.screenshot_via_adb('shot.png')
                try:
                    recent_result = inlib.treasure_result_ocr(shot_path)
                    
                except Exception as e:
                    pdc.main()
                    start_timestamp = 0
                    item_history = []
                    time_history = []
                    records = []
                    total = 0

                    # 每回合的数据列表，每回合都会变。
                    count_item          = []                    # 物品的统计
                    offset_item         = []
                    item_copd = []
                    last_copd = []

                    # 数据历史的列表，累计
                    posis   = []
                    diffs   = []
                    diff2   = []
                    for i in range(history_length):
                        posis.append(0)
                        diffs.append(0)
                    reg_preds         = []
                    pred_bias_str    = []
                    chips = 0
                    voted = False
                    InVest_Agreed = 0
                    win_records=[]
                    win_times = 0
                    CONFIGS['buy'] = 'no'
                    write_config(CONFIGS,if_buy)

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

            
            console.print(f'最新记录：{records[-3:]}，总数：{total}')        

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
            count_item              = inlib.item_sum_V(records)
            offset_item             = inlib.item_offset_V(count_item)
            item_copd               = inlib.position_sorted_V(offset_item,count_item)

            # 还是需要基于固定的值进行记录，而不是动态的值
            if len(last_copd) > 0:
                if records[-1][1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                    alias = '大'
                else:
                    alias = records[-1][1]
                for each in last_copd:
                    if alias in each:
                        posis.append(each[3])
            else:
                if records[-1][1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                    alias = '大'
                else:
                    alias = records[-1][1]
                for each in item_copd:                    
                    if alias in each:
                        posis.append(each[3])
            
            # 下一回合各乐器的diff值
            if len(posis) > 0:
                for each in item_copd:
                    each[4] = each[3]-posis[-1]

            # 计算 diff值
            if len(posis) >= 2:
                diffs.append(posis[-1] - posis[-2])

            # 不超过指定个数。
            if len(diffs) > history_length:
                posis.pop(0)
                diffs.pop(0)
                temp_ = [time_history[-1]] + diffs
                diff2.append(temp_)                

            console.print(f'DIFF：{diffs[-20:]} | 历史值：{sum(diffs[-5:])}->{sum(diffs[-4:])}')

            # diff2条数超过40时，才开始预测（前20条资源要丢弃）
            if len(diff2) > 40:
                df2 = pd.DataFrame(diff2[20:], columns=header)
                dates, X, y = windowed_df_to_date_X_y(df2)
                q_80 = int(len(dates) * .8)
                q_90 = int(len(dates) * .9)

                dates_train, X_train, y_train = dates[:q_80], X[:q_80], y[:q_80]

                dates_val, X_val, y_val = dates[q_80:q_90], X[q_80:q_90], y[q_80:q_90]
                dates_test, X_test, y_test = dates[q_90:], X[q_90:], y[q_90:]
                model = Sequential([layers.Input((20, 1)),
                    layers.LSTM(64),
                    layers.Dense(32, activation='relu'),
                    layers.Dense(32, activation='relu'),
                    layers.Dense(1)])

                model.compile(loss='mse', 
                            optimizer=Adam(learning_rate=0.0005),
                            metrics=['mean_absolute_error'])

                model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100)
                test_predictions = model.predict(X_test).flatten()

                next_ = inlib.calc_next_datetime(start_timestamp, 58)
                line_for_pred = [next_] + diffs[-1] + [0]
                lpred = pd.DataFrame(line_for_pred, columns=header)
                _, x_lpred, _ = windowed_df_to_date_X_y(lpred)
                print(f'下回合标签：{x_lpred}')
                prediction = model.predict(x_lpred).flatten()
                print(f'下回合预测值：{prediction}')

                mae_ = float(keras_metrics.mean_absolute_error(y_test, test_predictions))
                print(f'误差范围：{mae_}')
                y_ = y_test.tolist()
                test_predictions_ = test_predictions.tolist()
                for i in range(len(y_)):
                    if abs(y_[i] - (test_predictions_[i]+mae_)) <= 1:
                        print(f'胜 | 实际值：{y_[i]} | 预测值（含误差范围）：{test_predictions_[i]+mae_}')
                    else:
                        print(f'负 | 实际值：{y_[i]} | 预测值（含误差范围）：{test_predictions_[i]+mae_}')
                
                

            # # 计算上回合的收益
            # mgs = ''
            # if InVest_Agreed == 1:
            #     if records[-1][1] in buy_option[0:2]:
            #         income += chips_config[0] * 5
            #         msg = '买入结果：【命中】。'
            #         msg = msg + records[-1][0] + ' ' + records[-1][1] + '。'
            #         msg = msg + '本次回收：' + str(chips_config[0] * 5) + '。'
            #         msg = msg + '总投入：' + str(invest) + '。'
            #         msg = msg + '总回收：' + str(income) + '。'
            #         msg = msg + '总收益：' + str(int(income*0.635 - invest*0.92)) + '。'
            #         log_ = open(buy_log, 'a', encoding='utf8')
            #         log_.write(msg + '\n')
            #         log_.close()
            #         win_records.append('胜')
            #         win_times += 1
            #         chips = 0
            #     elif len(buy_option) == 4 and records[-1][1] in buy_option[2:4]:
            #         win = 0
            #         if chips_config[2] == 0:
            #             msg = '买入结果：【命中但未押】。'
            #             msg = msg + records[-1][0] + ' ' + records[-1][1] + '。'
            #             msg = msg + '本次回收：0。'
            #             msg = msg + '总投入：' + str(invest) + '。'
            #             msg = msg + '总回收：' + str(income) + '。'
            #             msg = msg + '总收益：' + str(int(income*0.635 - invest*0.92)) + '。'
            #             log_ = open(buy_log, 'a', encoding='utf8')
            #             log_.write(msg + '\n')
            #             log_.close()
            #             win_records.append('负')
            #         if chips_config[2] != 0:
            #             if records[-1][1] == '架子鼓':
            #                 win = int(chips_config[0]/4 * 10)
            #             elif  records[-1][1] == '竖琴':
            #                 win = int(chips_config[0]/4 * 20)
            #             elif  records[-1][1] == '萨克斯风':
            #                 win = int(chips_config[0]/4 * 25)
            #             elif  records[-1][1] == '圆号':
            #                 win = int(chips_config[0]/4 * 35)
            #             income += win
            #             msg = '买入结果：【命中】。'
            #             msg = msg + records[-1][0] + ' ' + records[-1][1] + '。'
            #             msg = msg + '本次回收：' + str(win) + '。'
            #             msg = msg + '总投入：' + str(invest) + '。'
            #             msg = msg + '总回收：' + str(income) + '。'
            #             msg = msg + '总收益：' + str(int(income*0.635 - invest*0.92)) + '。'
            #             log_ = open(buy_log, 'a', encoding='utf8')
            #             log_.write(msg + '\n')
            #             log_.close()
            #             chips = 0
            #             win_records.append('胜')
            #     elif records[-1][1] not in buy_option:
            #         msg = '买入结果：【未命中】。'
            #         msg = msg + records[-1][0] + ' ' + records[-1][1] + '。'
            #         msg = msg + '本次回收：0。'
            #         msg = msg + '总投入：' + str(invest) + '。'
            #         msg = msg + '总回收：' + str(income) + '。'
            #         msg = msg + '总收益：' + str(int(income*0.635 - invest*0.92)) + '。'
            #         log_ = open(buy_log, 'a', encoding='utf8')
            #         log_.write(msg + '\n')
            #         log_.close()
            #         win_records.append('负')
                    
            #     if len(win_records) > 5:
            #         win_records.pop(0)
            #     console.print(msg)


            # voted = False
            # InVest_Agreed = 0
            # buy_option = []
            
            # # if wins[-4:] == ['胜', '负', '负', '胜'] or wins[-4:] == ['负', '负', '负', '负'] or wins[-4:] == ['负', '负', '负', '胜']:
            # if win_records[-3:] == ['负', '负', '胜'] or win_records[-4:] == ['负', '负', '负', '胜']:
            # # if win_counter == 2:
            #     CONFIGS['buy'] = 'no'
            #     write_config(CONFIGS,if_buy)
            # # elif wins[-2:] == ['胜', '胜']:
            # elif win_records[-5:].count('胜') >= 3:
            #     CONFIGS['buy'] = 'yes'
            #     win_times = 0
            #     write_config(CONFIGS,if_buy)

      
            # # 时段条件
            # if (start_timestamp+8*60*60) % (24*60*60) < (0*60*60):
            #     # console.print(f'本时段不进行模拟')
            #     pass
            # else:
            #     # 购买条件
            #     if total >= 10:
            #         buy_option = []
            #         # 如果最近一次的预测误差小于等于1，则
            #         if abs(pred_bias_int[-1]) <= 1:
            #             # 计算本次每个物品的diff值与预测值之间的绝对差，
            #             for i in range(5):
            #                 # 如果小于等于1，就记录为一个候选项
            #                 if abs(item_copd[i][4] - reg_preds[-1]) <= 1:
            #                     buy_option.append(item_copd[i][0])
                    
            #         # 如果最近一次的预测误差大于1，则
            #         if abs(pred_bias_int[-1]) > 1:
            #             # 计算本次每个物品的diff值与预测值之间的绝对差，
            #             for i in range(5):
            #                 # 如果大于1，就记录为一个候选项
            #                 if abs(item_copd[i][4] - reg_preds[-1]) > 1:
            #                     buy_option.append(item_copd[i][0])
                    
            #         # 如果候选项的个数为2，并且候选项里没有‘大’，则认为可以“买入”
            #         # 如果不符合条件的话，候选项清空
            #         if len(buy_option) == 2 and '大' not in buy_option:
            #             InVest_Agreed = 1
            #         else:
            #             buy_option = []
                    
            #     # 如果认为可以“买入”
            #     if InVest_Agreed == 1:
            #         comment = '同意买入。'
            #         # 配置项中，购买开启
            #         if CONFIGS['buy'] == 'yes':
            #             comment = comment + '买入操作配置【开启】。'
            #             if chips == 0 or chips == TOP_STOCK:
            #                 chips = STOCK
            #             else:
            #                 chips = int(chips/RATE)
            #             comment = comment + '买入计量为' + str(chips) + '。'
            #         # 配置项中，购买未开启
            #         elif CONFIGS['buy'] == 'no':
            #             comment = comment + '买入操作配置【未开启】。'
            #             chips = 0
            #             comment = comment + '买入计量为' + str(chips) + '。'
            #         invest += chips
                    
            #         console.print(comment)

            #         chips_config = [int(chips/2), int(chips/2), 0, 0]
            #         console.print(f'模拟买入：{buy_option} | {chips_config}音符')
            #         msg = ''
            #         msg = msg + comment
            #         if len(buy_option) == 4:
            #             msg = msg + '模拟买入：' + buy_option[0] + ',' + str(chips_config[0]) + ' | ' + buy_option[1] + ',' + str(chips_config[1]) + ' | ' + buy_option[2] + ',' + str(chips_config[2]) + ' | ' + buy_option[3] + ',' + str(chips_config[3]) + ' | '
            #         elif len(buy_option) == 2:
            #             msg = msg + '模拟买入：' + buy_option[0] + ',' + str(chips_config[0]) + ' | ' + buy_option[1] + ',' + str(chips_config[1]) + ' | '
            #         log_ = open(buy_log, 'a', encoding='utf8')
            #         log_.write(msg)
            #         log_.close()

            #         if CONFIGS['buy'] == 'yes' and int(CONFIGS['bullet']) > 0:
                        
            #             '''
            #             这里要解决的问题是
            #             1. 当处于购买状态时，如果剩余子弹大于0
            #                 剩余子弹数量大于要押注的数量，且上一回合没赢
            #             '''
            #             if win_records[-1] != '胜':
            #                 if int(CONFIGS['bullet']) <= chips:
            #                     CONFIGS['buy'] = 'no'
            #                     write_config(CONFIGS,if_buy)
            #                 elif int(CONFIGS['bullet']) > chips and int(CONFIGS['bullet']) >= int(STOCK + STOCK/RATE + STOCK/RATE/RATE + TOP_STOCK):
            #                     pass
            #                 elif int(CONFIGS['bullet']) > chips and int(CONFIGS['bullet']) < int(STOCK + STOCK/RATE + STOCK/RATE/RATE + TOP_STOCK):
            #                     CONFIGS['buy'] = 'no'
            #                     write_config(CONFIGS,if_buy)
            #                 else:
            #                     pass
            #             if win_records[-1] == '负':
            #                 if chips == TOP_STOCK and int(CONFIGS['bullet']) <= TOP_STOCK:
            #                     CONFIGS['buy'] = 'no'
            #                     write_config(CONFIGS,if_buy)
            #                 elif chips == int(STOCK/RATE) and int(CONFIGS['bullet']) <= int(STOCK/RATE + STOCK/RATE/RATE + TOP_STOCK):
            #                     CONFIGS['buy'] = 'no'
            #                     write_config(CONFIGS,if_buy)
            #                 elif chips == int(STOCK/RATE/RATE) and int(CONFIGS['bullet']) <= int(STOCK/RATE/RATE + TOP_STOCK):
            #                     CONFIGS['buy'] = 'no'
            #                     write_config(CONFIGS,if_buy)

            #         # 购买执行后，修改配置项里的余量
            #         if CONFIGS['buy'] == 'yes' and CONFIGS['bullet'] != '0':
            #             time.sleep(5)
            #             CONFIGS['bullet'] = str(int(int(CONFIGS['bullet']) - chips))
            #             write_config(CONFIGS,if_buy)
            #             by.buy_4(buy_option,chips_config)
            #             voted = True
            #         elif CONFIGS['buy'] == 'no':
            #             voted = False

            

            console.print(f'拟总计投入：{invest} 音符 | 总计回收：{income} 音符 | 收益：{int(income*0.63) - invest}')
            console.print(f'起注：{STOCK} | 封顶：{TOP_STOCK}')

            # 格式化展示，方便查看数值
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("物品", style="dim", width=12)
            table.add_column("4 - 差分", justify="right", width=12)
            table.add_column("1 - 数量", justify="right", width=12)
            table.add_column("2 - 偏移", justify="right", width=12)
            table.add_column("3 - 位序", justify="right", width=12)
            for i in range(5):
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
            for i in range(history_length):
                if i != history_length-1:
                    diffs_rec.write(str(diffs[i])+',')
                else:
                    diffs_rec.write(str(diffs[i])+'\n')
            diffs_rec.close()

            # if CONFIGS['chat'] == 'yes' and len(buy_option) > 0:
            #     # pad按返回键
            #     os.popen('adb shell input keyevent 4')
            #     time.sleep(2)
            #     # 点击聊天输入框
            #     pdc.open_chat()
            #     time.sleep(1)
            #     if buy_option[0] == '钢琴':
            #         content = 'buy%spiano%s&%s'
            #     elif buy_option[0] == '小提琴':
            #         content = 'buy%svoilin%s&%s'
            #     elif buy_option[0] == '吉他':
            #         content = 'buy%sguitar%s&%s'
            #     elif buy_option[0] == '贝斯':
            #         content = 'buy%sbeth%s&%s'
            #     os.popen('adb shell input text '+ content).read()
            #     if buy_option[1] == '钢琴':
            #         content = 'piano'
            #     elif buy_option[1] == '小提琴':
            #         content = 'voilin'
            #     elif buy_option[1] == '吉他':
            #         content = 'guitar'
            #     elif buy_option[1] == '贝斯':
            #         content = 'beth'
            #     os.popen('adb shell input text '+ content).read()
            #     if len(buy_option) == 4:
            #         if buy_option[2] == '架子鼓':
            #             content = '%s&%sdrum%s&%s'
            #         elif buy_option[2] == '竖琴':
            #             content = '%s&%sharp%s&%s'
            #         elif buy_option[2] == '萨克斯风':
            #             content = '%s&%ssax%s&%s'
            #         elif buy_option[2] == '圆号':
            #             content = '%s&%shorn%s&%s'
            #         os.popen('adb shell input text '+ content).read()
            #         if buy_option[3] == '架子鼓':
            #             content = 'drum'
            #         elif buy_option[3] == '竖琴':
            #             content = 'harp'
            #         elif buy_option[3] == '萨克斯风':
            #             content = 'sax'
            #         elif buy_option[3] == '圆号':
            #             content = 'horn'
            #         os.popen('adb shell input text '+ content).read()
            #     # 发送消息
            #     time.sleep(1)
            #     pdc.send_chat()
            #     time.sleep(2)
            #     pdc.open_kd()

            inlib.wait_next(start_timestamp, 58)
            start_timestamp += 58
            if voted == True:
                time.sleep(10)
                by.close_popup()

    except Exception as e:
        print(e,traceback.format_exc())

        # unsupported operand type(s) for -: 'int' and 'list'