'''基于all.csv的时间轴，和all_num_datasets.csv的差分顺序，生成适用于随机森林回归的训练集

这个脚本的运行，是根据 all.csv的时间轴，和all_num_datasets.csv的diff result，
按照时间轴分割的段落（差值超过58秒认为是不同的段落），
把 每20个 diff result 变成一行 x_data， 把第21个 diff result 变成 y_data，以此生成训练集

'''


import os
import datetime
from rich.console import Console
import pandas as pd

console = Console()

diff_text_dict = {
    '负七':     -7,
    '负六':     -6,
    '负五':     -5,
    '负四':     -4,
    '负三':     -3,
    '负二':     -2,
    '负一':     -1,
    '零':       0,
    '一':       1,
    '二':       2,
    '三':       3,
    '四':       4,
    '五':       5,
    '六':       6,
    '七':       7,
    }

DIR = os.path.dirname(__file__)
read_record = open(DIR+'./all.csv', 'r', encoding='utf8')
read_diff_result = open(DIR+'./all_num_datasets.csv', 'r', encoding='utf8')

time_index_list = []
i = 0
for line in read_record:
    if i == 0:
        i += 1
        pass
    else:
        line = line.strip()
        time_str, _ = line.split(',')
        time_index_list.append(time_str)
            

diff_index_list = []
i = 0
for line in read_diff_result:
    if i == 0:
        i += 1
        pass
    else:
        line = line.strip()
        *args, diff_text = line.split(',')      # 文字          
        diff_num = diff_text_dict[diff_text]    # 数值
        diff_index_list.append(diff_num)

####################

merge_list_para = []
merge_list_final = []
for i in range(len(time_index_list)):
    if i > 0 and (datetime.datetime.strptime(time_index_list[i], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(time_index_list[i-1], '%Y-%m-%d %H:%M:%S')).seconds == 58:
        merge_list_para.append([time_index_list[i], diff_index_list[i]])
    elif i == 0:
        merge_list_para.append([time_index_list[i], diff_index_list[i]])
    else:
        merge_list_final.append(merge_list_para)
        merge_list_para = []
        merge_list_para.append([time_index_list[i], diff_index_list[i]])

merge_list_final.append(merge_list_para)

####################

each_final_diff_list = []
column_name_list = []
for i in range(1,21):
    col_name = 'col_' + str(i)
    column_name_list.append(col_name)

column_name_list.append('result')

for each in merge_list_final:
    print(len(each))
    # 把 每个段落的前20条数据去掉，因为前20条数据不完整，故diff值没有参考价值
    deal_list = each[20:]
    

    for i in range(20,len(deal_list)):
        each_diff_line = []
        for j in range(21):
            each_diff_line.append(deal_list[i - 20 + j][-1])
        each_final_diff_list.append(each_diff_line)

    print(len(each_final_diff_list))

console.print(each_final_diff_list[:2])

df = pd.DataFrame([t for t in each_final_diff_list], columns=column_name_list,)

print(df.tail())

df.to_csv(DIR+'./test.csv',index=False)