import os
import platform
import datetime
import instead_lib as inlib
from rich.console import Console

DICT = {
    '钢琴': '1',
    '小提琴': '2',
    '吉他': '3',
    '贝斯': '4',
    '架子鼓': '5',
    '竖琴': '6',
    '萨克斯风': '7',
    '圆号': '8',
}
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
}

DICT_NAME = ['钢琴', '小提琴', '吉他', '贝斯', '大']


console = Console()
DIR = os.path.dirname(__file__)
if platform.system().lower() == 'windows':
    all_csv_path = DIR + './all.csv'
    pos_csv_path_20 = DIR + './all___20+1.csv'
    diff_csv_path_20 = DIR + './all_diff_20+1.csv'
elif platform.system().lower() == 'linux':
    all_csv_path = DIR + '/all.csv'
    pos_csv_path_20 = DIR + '/all___20+1.csv'
    diff_csv_path_20 = DIR + '/all_diff_20+1.csv'

read_all_csv = open(all_csv_path, 'r', encoding='utf8')

all_data = []
for line in read_all_csv:
    line = line.strip()
    time_ , item_ = line.split(',')
    if time_ != '时间':
        all_data.append([time_, item_, 0])
    

for each in all_data:
    time_stamp = datetime.datetime.timestamp(datetime.datetime.strptime(each[0], '%Y-%m-%d %H:%M:%S'))
    each[2] = int(time_stamp)


# 分成不同的段落
segment = []
data_segments = []
for i in range(len(all_data)):
    segment.append(all_data[i])
    if i < len(all_data)-1:
        if all_data[i+1][2] - all_data[i][2] != 58:
            data_segments.append(segment)
            segment = []

data_segments.append(segment)

# 用来检查数据分段后的各段长度
# for i in range(len(total_data_format)):
#     print(len(total_data_format[i]))


'''
下面这个流程模拟了 instead_main 的实时过程，只是把每回合数据的输入改成了从list里读取
'''
write_pos_csv = open(pos_csv_path_20, 'a', encoding='utf8')
write_pos_csv.write('time,col_1,col_2,col_3,col_4,col_5,col_6,col_7,col_8,col_9,col_10,col_11,col_12,col_13,col_14,col_15,result,item\n')
# write_diff_csv = open(diff_csv_path_20, 'a', encoding='utf8')
# write_diff_csv.write('time,col_1,col_2,col_3,col_4,col_5,col_6,col_7,col_8,col_9,col_10,col_11,col_12,col_13,col_14,col_15,col_16,col_17,col_18,col_19,col_20,result,item\n')
for segment in data_segments:
    # 在进行新的片段时，初始化这些数据
    record_history = []
    position_history = []
    diff_history            = []
    # 预设20个posi历史记录，方便开局就进行预测
    for i in range(20):
        position_history.append(0)
    # 预设20个diff历史记录，方便开局就进行预测
    for i in range(20):
        diff_history.append(0)

    total = 0
    export = ''
    
    # 片段内数据逐个读入
    for each in segment:
        # 0是时间文本，1是物品
        record_history.append([each[0],each[1]])
        if len(record_history) > 20:
            record_history.pop(0)

        if export != '':
            write_pos_csv.write(record_history[-1][0] + export + ',' + record_history[-1][1] + '\n')
        total += 1
        # 开始计算各项值
        count_item              = inlib.item_sum_V(record_history)
        offset_item             = inlib.item_offset_V(count_item)
        item_copd               = inlib.position_sorted_V(offset_item,count_item)

        if len(item_copd) > 0:
            if record_history[-1][1] in ['钢琴','小提琴','吉他','贝斯']:
                for item in item_copd:
                    if record_history[-1][1] in item:
                        position_history.append(item[3])
            if record_history[-1][1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                for item in item_copd:
                    if '大' in item:
                        position_history.append(item[3])

        # posi值的历史，最多不超过20个。
        if len(position_history) > 21:
            position_history.pop(0)
        
        # 适当时机，显示posi值的历史
        if len(position_history) > 0:
            # 计算当前回合 各个物品的 Diff 值（预期值）
            for item in item_copd:
                item[4] = item[3]-position_history[-1]

        # 适当时机，开始计算 diff值，计算的依据是最近2个posi值的差
        if len(position_history) >= 2:
            diff_history.append(position_history[-1] - position_history[-2])

        # diff值得历史，最多不超过20个。
        if len(diff_history) > 21:
            diff_history.pop(0)

        if total >= 21:
            export = ''
            for num in count_item:
                export = export + ',' + str(num)
            for name in DICT_NAME:
                for item in item_copd:
                    if item[0] == name:
                        export = export + ',' + str(item[3])
            for name in DICT_NAME:
                for item in item_copd:
                    if item[0] == name:
                        export = export + ',' + str(item[4])
            # export = ''
            # for num in diff_history:
            #     export = export + ',' + str(num)
            # write_diff_csv.write(record_history[-1][0] + export + ',' + record_history[-1][1] + '\n')

write_pos_csv.close()
# write_diff_csv.close()