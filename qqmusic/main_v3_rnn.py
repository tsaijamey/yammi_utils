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
from keras.models import load_model
from keras.optimizers import Adam
from keras import layers
import keras.metrics as keras_metrics

# RNN和LSTM输入数据集的处理方法
def windowed_df_to_date_X_y(windowed_dataframe):
    df_as_np = windowed_dataframe.to_numpy()

    dates = df_as_np[:, 0]
    middle_matrix = df_as_np[:, 1:-1]
    X = middle_matrix.reshape((len(dates), middle_matrix.shape[1], 1))

    Y = df_as_np[:, -1]

    return dates, X.astype(np.float32), Y.astype(np.float32)

def write_config(dict:dict,path:str):
    r = open(path, 'w', encoding='utf8')
    r.write('bullet='+str(dict['bullet'])+'\n')
    r.write('buy='+dict['buy']+'\n')
    r.write('chat='+dict['chat']+'\n')
    r.write('chip='+str(dict['chip'])+'\n')
    r.write('times='+str(dict['times'])+'\n')
    r.write('rate='+str(dict['rate'])+'\n')
    r.close()

def read_config(dict:dict, path:str):
    r = open(path, 'r', encoding='utf8')
    for line in r:
        line = line.strip()
        key,value = line.split('=')
        if key in ['buy', 'chat']:
            dict[key] = value
        elif key in ['bullet','chip','times']:
            dict[key] = int(value)
        elif key == 'rate':
            dict[key] = float(value)
    r.close()

def R_to_Str(r:list, dict:dict, nums:str):
    for each in r:
        if each[1] in ['架子鼓','竖琴','萨克斯风','圆号']:
            nums += '{' + dict[each[1]] + '}'
        else:
            nums += dict[each[1]]
    if len(nums) - nums.count('{') - nums.count('}') > 20:
        if nums[0] == '{':
            nums = nums[3:]
        else:
            nums = nums[1:]

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
CONFIGS = {
    'bullet': 0,
    'buy':'no',
    'chat':'no',
    'chip':2,
    'times':2,
    'rate':0.1,
}


timestamp = 0
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
ACTION = False
InVest_Agreed = 0
win_records=[]
win_times = 0
validation = []
RNN_win = []
pred_option = []


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
    mae_log = DIR+'./mae_log-' + current_date + '.log'
    RNN_model = DIR+'./model/RNN-current.h5'
elif platform.system().lower() == 'linux':
    shot_path = DIR + '/img/shot.png'
    record_path = DIR+'/auto2-' + current_date + '.csv'
    diffs_log = DIR+'/diff-' + current_date + '.csv'
    rate_log = DIR+'/win_rate-' + current_date + '.log'
    buy_log = DIR+'/buy_log-' + current_date + '.log'
    if_buy = DIR+'/if_buy.txt'    
    diff_model_path = DIR+'/model/reg_5_20221220_seed10.m'
    mae_log = DIR+'/mae_log-' + current_date + '.log'
    RNN_model = DIR+'/model/RNN-current.h5'

log_recorder = open(diffs_log, 'a', encoding='utf8')
log_recorder.write('\n')
log_recorder.close()



if __name__ == '__main__':
    try:
        # pdc.main()
        while True:

            # 重置近期结果
            _result = []

            # 获取App中的结果
            while len(_result) == 0 or len(_result[0]) == 0:
                
                # 读取购买配置
                read_config(CONFIGS, if_buy)
                
                
                # 计算 max_chips
                STOCK       = CONFIGS['chip']
                TIMES       = CONFIGS['times']
                RATE        = CONFIGS['rate']
                TOP_STOCK   = int(STOCK/round((RATE**TIMES),4))
                _chips = STOCK
                max_chips = _chips
                # TIMES = 3的话，就是循环0、1、2
                for x in range(TIMES):
                    # 2/0.1（20）、2/0.1/0.1（200）
                    _chips = int(_chips/RATE)
                    max_chips += _chips
                inlib.screenshot_via_adb('shot.png')
                try:
                    # [物品名, [时间文本,时间戳]]
                    _result = inlib.treasure_result_ocr(shot_path)
                    
                except Exception as e:
                    print(f'解析失败，ERROR：{e}')
                    # 重启App
                    pdc.main()
                    timestamp = 0
                    records = []
                    total = 0
                    count_item      = []
                    offset_item     = []
                    item_copd       = []
                    last_copd       = []
                    posis   = []
                    diffs   = []
                    diff2   = []
                    for i in range(history_length):
                        posis.append(0)
                        diffs.append(0)
                    reg_preds         = []
                    pred_bias_str    = []
                    chips = 0
                    ACTION = False
                    InVest_Agreed = 0
                    win_records=[]
                    win_times = 0
                    validation = []
                    pred_option = []
                    CONFIGS['buy'] = 'no'
                    write_config(CONFIGS,if_buy)

            # 区分第一次和后面的其他回合
            if total == 0:
                # 第一次需要更新 timestamp 值
                timestamp = _result[1][1]

            records.append([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)), _result[0]])
            if len(records) > 20:
                records.pop(0)

            r = open(record_path, 'a', encoding='utf8')
            r.write(records[-1][0] + ',' + records[-1][1] + '\n')
            r.close() 
            total += 1        

            # 把出货历史，泛化成数字
            nums = ''
            R_to_Str(records, DICT, nums)
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
                diff2.append([records[-1][0]]+diffs)

            console.print(f'DIFF：{diffs[-20:]} | 历史值：{sum(diffs[-5:])}->{sum(diffs[-4:])}')

            if len(validation) > 0:
                # validation的格式是：[预测值, 实际值]
                validation[-1].append(diffs[-1])
                if abs(validation[-1][1] - validation[-1][0]) <= 1:
                    mae_record = open(mae_log, 'a', encoding='utf8')
                    mae_record.write(f',time={time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))},obs={diffs[-1]},item={records[-1][1]},正')
                    mae_record.close()
                    RNN_win.append('正')
                else:
                    mae_record = open(mae_log, 'a', encoding='utf8')
                    mae_record.write(f',time={time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))},obs={diffs[-1]},item={records[-1][1]},反')
                    mae_record.close()
                    RNN_win.append('反')
                
                if len(pred_option) > 0:
                    validation[-1].append(pred_option)

                if len(RNN_win) > 20:
                    RNN_win.pop(0)
                print(f'RNN预测记录：{RNN_win}')

            # 计算上回合的收益
            mgs = ''
            if InVest_Agreed == 1:
                if records[-1][1] in buy_option[0:2]:
                    income += chips_config[0] * 5
                    if chips_config[0] > 0:
                        win_times += 1
                    msg = '买入结果：【命中】。'
                    msg = msg + records[-1][0] + ' ' + records[-1][1] + '。'
                    msg = msg + '本次回收：' + str(chips_config[0] * 5) + '。'
                    msg = msg + '总投入：' + str(invest) + '。'
                    msg = msg + '总回收：' + str(income) + '。'
                    msg = msg + '总收益：' + str(int(income*0.635 - invest*0.92)) + '。'
                    log_ = open(buy_log, 'a', encoding='utf8')
                    log_.write(msg + '\n')
                    log_.close()
                    win_records.append('胜')                    
                    chips = 0
                elif len(buy_option) == 4 and records[-1][1] in buy_option[2:4]:
                    win = 0
                    if chips_config[2] == 0:
                        msg = '买入结果：【命中但未押】。'
                        msg = msg + records[-1][0] + ' ' + records[-1][1] + '。'
                        msg = msg + '本次回收：0。'
                        msg = msg + '总投入：' + str(invest) + '。'
                        msg = msg + '总回收：' + str(income) + '。'
                        msg = msg + '总收益：' + str(int(income*0.635 - invest*0.92)) + '。'
                        log_ = open(buy_log, 'a', encoding='utf8')
                        log_.write(msg + '\n')
                        log_.close()
                        win_records.append('负')
                    if chips_config[2] != 0:
                        if records[-1][1] == '架子鼓':
                            win = int(chips_config[0]/4 * 10)
                        elif  records[-1][1] == '竖琴':
                            win = int(chips_config[0]/4 * 20)
                        elif  records[-1][1] == '萨克斯风':
                            win = int(chips_config[0]/4 * 25)
                        elif  records[-1][1] == '圆号':
                            win = int(chips_config[0]/4 * 35)
                        income += win
                        msg = '买入结果：【命中】。'
                        msg = msg + records[-1][0] + ' ' + records[-1][1] + '。'
                        msg = msg + '本次回收：' + str(win) + '。'
                        msg = msg + '总投入：' + str(invest) + '。'
                        msg = msg + '总回收：' + str(income) + '。'
                        msg = msg + '总收益：' + str(int(income*0.635 - invest*0.92)) + '。'
                        log_ = open(buy_log, 'a', encoding='utf8')
                        log_.write(msg + '\n')
                        log_.close()
                        chips = 0
                        win_records.append('胜')
                elif records[-1][1] not in buy_option:
                    msg = '买入结果：【未命中】。'
                    msg = msg + records[-1][0] + ' ' + records[-1][1] + '。'
                    msg = msg + '本次回收：0。'
                    msg = msg + '总投入：' + str(invest) + '。'
                    msg = msg + '总回收：' + str(income) + '。'
                    msg = msg + '总收益：' + str(int(income*0.635 - invest*0.92)) + '。'
                    log_ = open(buy_log, 'a', encoding='utf8')
                    log_.write(msg + '\n')
                    log_.close()
                    win_records.append('负')
                    
                if len(win_records) > 5:
                    win_records.pop(0)
                console.print(msg)


            ACTION = False
            InVest_Agreed = 0
            buy_option = []

            if total > 100 and chips == 0:
                console.print('超过100回合且不在购买状态。')
                pdc.main()
                timestamp = 0
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
                ACTION = False
                InVest_Agreed = 0
                win_records=[]
                win_times = 0
                validation = []
                pred_option = []
                CONFIGS['buy'] = 'no'
                write_config(CONFIGS,if_buy)
            else:
                try:
                    # diff2条数超过40时，才开始预测（前20条资源要丢弃）
                    if len(diff2) > 20:
                        diff2.pop(0)
                        df2 = pd.DataFrame(diff2[-20:], columns=header)
                        dates, X, y = windowed_df_to_date_X_y(df2)
                        q_90 = int(len(dates) * .9)

                        X_train, y_train = X[:q_90], y[:q_90]

                        X_val, y_val = X[q_90:-2], y[q_90:-2]
                        X_test, y_test = X[-2:], y[-2:]

                        # model = Sequential([layers.Input((20, 1)),
                        #     layers.LSTM(64),
                        #     layers.Dense(32, activation='relu'),
                        #     layers.Dense(32, activation='relu'),
                        #     layers.Dense(1)])

                        # model.compile(loss='mse', 
                        #             optimizer=Adam(learning_rate=0.0005),
                        #             metrics=['mean_absolute_error'])

                        # model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, verbose=0)
                        # model.save(DIR+"\\model\\"+'RNN-Realtime-'+current_date+'.h5')
                        model = load_model(RNN_model)

                        # 用测试集验证
                        test_predictions = model.predict(X_test).flatten()
                        mae_ = float(keras_metrics.mean_absolute_error(y_test, test_predictions))
                        print(f'误差范围：{mae_}')
                        y_ = y_test.tolist()
                        test_predictions_ = test_predictions.tolist()
                        print('以下仅供参考')
                        print('*'*30)
                        if len(y_) > 5:
                            for i in range(-5,0):
                                if abs(y_[i] - (test_predictions_[i]+mae_)) <= 1:
                                    print(f'胜 | 实际值：{y_[i]} | 预测值：{test_predictions_[i]} | 误差：{y_[i]-test_predictions_[i]}')
                                else:
                                    print(f'负 | 实际值：{y_[i]} | 预测值：{test_predictions_[i]} | 误差：{y_[i]-test_predictions_[i]}')
                        else:
                            for i in range(len(y_)):
                                if abs(y_[i] - (test_predictions_[i]+mae_)) <= 1:
                                    print(f'胜 | 实际值：{y_[i]} | 预测值：{test_predictions_[i]} | 误差：{y_[i]-test_predictions_[i]}')
                                else:
                                    print(f'负 | 实际值：{y_[i]} | 预测值：{test_predictions_[i]} | 误差：{y_[i]-test_predictions_[i]}')
                        print('*'*30)

                        # 预测下回合数据
                        next_ = inlib.calc_next_datetime(timestamp, 58)
                        line_for_pred = [[next_] + diffs[1:] + [0]]
                        lpred = pd.DataFrame(line_for_pred, columns=header)
                        _, x_lpred, _ = windowed_df_to_date_X_y(lpred)
                        prediction_ = model.predict(x_lpred).flatten()
                        prediction = prediction_.tolist()[0]
                        print(f'\n下回合预测值：{round(prediction,3)} | 下回合预测值（含误差）：{round(prediction+mae_,3)}\n')
                        validation.append([round(prediction+mae_,3)])

                        if len(RNN_win) >= 2:
                            pred_option_a = []  # a对应的是正手历史的购买选项
                            pred_option_b = []  # b对应的是反手历史的购买选项
                            pred_option = []
                            for each in item_copd:
                                if abs(each[4] - round(prediction+mae_,3)) > 1:
                                    pred_option_b.append(each[0])
                                elif abs(each[4] - round(prediction+mae_,3)) < 1:
                                    pred_option_a.append(each[0])

                            # 根据预测值分析购买选项
                            if RNN_win[-1] == RNN_win[-2] and RNN_win[-1] == '正':
                                pred_option = pred_option_a
                                # if len(pred_option_a) == 2 and '大' not in pred_option_a:                        
                                direction = '正'
                                print(f'正手预测：{pred_option}')
                            elif RNN_win[-1] == RNN_win[-2] and RNN_win[-1] == '反':
                                pred_option = pred_option_b
                                # if len(pred_option_b) == 2 and '大' not in pred_option_b:
                                direction = '反'
                                print(f'反手预测：{pred_option}')
                            else:
                                pred_option_a = []  # a对应的是正手历史的购买选项
                                pred_option_b = []  # b对应的是反手历史的购买选项
                                pred_option = []
                                direction = ''

                            try:
                                mae_record = open(mae_log, 'a', encoding='utf8')
                                mae_record.write(f'\ndirection={direction},mae={round(mae_,3)},pred={round(prediction,3)},opt={pred_option}')
                                mae_record.close()
                            except Exception as e:
                                print(e)
                            if len(validation) > 5:
                                validation.pop(0)
                            print(f'预测历史：{validation}')
                except Exception as e:
                    print(e)



                # 根据Diff值的预测：
                reg_predict = inlib.load_rf_reg_model(diff_model_path, diffs[-20:]).tolist()[0]
                if reg_predict == 0:
                    pred_to_int = 0
                else:
                    pred_to_int = int(reg_predict)

                reg_preds.append(pred_to_int)

                # 预测的历史，只保留最近的21个。
                if len(reg_preds) > 21:
                    reg_preds.pop(0)

                # 计算 预测diff 和 实际diff 的误差，存入 reg_predict_infact_error
                # 用于计算的 预测diff 来自 reg_predict_history[-2]
                if len(reg_preds) >= 2:
                    if records[-1][1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                        pred_bias_str.append(str(diffs[-1] - reg_preds[-2]))
                    else:
                        pred_bias_str.append(diffs[-1] - reg_preds[-2])

                    if len(pred_bias_str) > 20:
                        pred_bias_str.pop(0)
                    
                    pred_bias_int = []
                    for each in pred_bias_str:
                        pred_bias_int.append(int(each))
                        
                    console.print(f'误差bias历史：{pred_bias_str}')
                    console.print(f'预测pred历史：{reg_preds[:-1]} | 当前值：{reg_preds[-1]}')  

                
                
                # if wins[-4:] == ['胜', '负', '负', '胜'] or wins[-4:] == ['负', '负', '负', '负'] or wins[-4:] == ['负', '负', '负', '胜']:
                # if win_times == 1 or win_records[-3:] == ['负', '负', '胜'] or win_records[-4:] == ['负', '负', '负', '胜']:
                if win_times >= 1:
                    CONFIGS['buy'] = 'no'
                    write_config(CONFIGS,if_buy)
                # elif wins[-2:] == ['胜', '胜']:
                elif win_records[-5:].count('胜') >= 3:
                    CONFIGS['buy'] = 'yes'
                    win_times = 0
                    write_config(CONFIGS,if_buy)

        
                # 时段条件
                if (timestamp+8*60*60) % (24*60*60) < (8*60*60):
                    # console.print(f'本时段不进行模拟')
                    pass
                else:
                    # 购买条件
                    if total >= 10:
                        buy_option = []
                        # 最近一次的预测误差的绝对值与1进行比较，则
                        # 计算本次每个物品的diff值与预测值之间的绝对差，
                        if abs(pred_bias_int[-1]) <= 1:                            
                            for i in range(5):
                                if abs(item_copd[i][4] - reg_preds[-1]) <= 1:
                                    buy_option.append(item_copd[i][0])
                        else:
                            for i in range(5):
                                if abs(item_copd[i][4] - reg_preds[-1]) > 1:
                                    buy_option.append(item_copd[i][0])
                        
                        # 如果候选项的个数为2，并且候选项里没有‘大’，则认为可以“买入”
                        # 如果不符合条件的话，候选项清空
                        if len(buy_option) == 2 and '大' not in buy_option:
                            InVest_Agreed = 1
                            # 配置项中，购买开启
                            if CONFIGS['buy'] == 'yes' and CONFIGS['bullet'] > max_chips:
                                ACTION = True
                                if chips == 0 or chips >= TOP_STOCK:
                                    chips = STOCK
                                else:
                                    chips = int(chips/RATE)
                            
                            # 配置项中，购买未开启
                            else:
                                ACTION = False                         
                                chips = 0                                

                            invest += chips
                            chips_config = [int(chips/2), int(chips/2), 0, 0]
                            if ACTION == True:
                                time.sleep(3)
                                by.buy_4(buy_option,chips_config)                                
                                CONFIGS['bullet'] -= chips
                                write_config(CONFIGS,if_buy)
                            console.print(f'模拟买入：{buy_option} | {chips_config}音符')

                            log_ = open(buy_log, 'a', encoding='utf8')
                            log_.write(msg)
                            log_.close()


                                
                        else:
                            buy_option = []
                

                console.print(f'拟总计投入：{invest} 音符 | 总计回收：{income} 音符 | 收益：{int(income*0.635) - int(invest*0.92)}')
                console.print(f'起注：{STOCK} | 封顶：{TOP_STOCK} | 循环最大量：{max_chips}')

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
                
                # 记录diff数据
                log_recorder = open(diffs_log, 'a', encoding='utf8')
                # diffs_rec.write(records[-1][0]+',')
                # [0, 21)
                for i in range(history_length):
                    if i != history_length-1:
                        log_recorder.write(str(diffs[i])+',')
                    else:
                        log_recorder.write(str(diffs[i])+'\n')
                log_recorder.close()

                inlib.wait_next(timestamp, 58)
                timestamp += 58
                if ACTION == True:
                    time.sleep(10)
                    by.close_popup()

    except Exception as e:
        print(e,traceback.format_exc())

        # unsupported operand type(s) for -: 'int' and 'list'