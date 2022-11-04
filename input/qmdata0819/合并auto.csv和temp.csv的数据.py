import os
import datetime
import platform



DIR = os.path.dirname(__file__)

if platform.system().lower() == 'windows':
    auto_csv_path = DIR+'./auto.csv'
    temp_csv_path = DIR+'./temp.csv'
    merge_csv_path = DIR+'./merge_result_.csv'
elif platform.system().lower() == 'linux':
    auto_csv_path = DIR+'/auto.csv'
    temp_csv_path = DIR+'/temp.csv'
    merge_csv_path = DIR+'/merge_result.csv'

read_auto = open(auto_csv_path, 'r', encoding='utf8')
read_temp = open(temp_csv_path, 'r', encoding='utf8')

total_data = []
for line in read_auto:
    line = line.strip()
    if line != '':
        time_, item_ = line.split(',')
        total_data.append([time_, item_, 0])

for line in read_temp:
    line = line.strip()
    if line != '':
        time_, item_ = line.split(',')
        total_data.append([time_, item_, 0])

for each in total_data:
    time_stamp = datetime.datetime.timestamp(datetime.datetime.strptime(each[0], '%Y-%m-%d %H:%M:%S'))
    each[2] = int(time_stamp)

total_data.sort(key=lambda x:x[2])

# print(len(total_data))

unique_check = []
remove_list = []
for each in total_data:
    if each[2] in unique_check:
        remove_list.append(each)
    else:
        unique_check.append(each[2])

for each in remove_list:
    total_data.remove(each)


'''
检查total_data里的隔行片段长度，如果低于40的，舍弃
'''
segment = []
total_data_format = []
for i in range(len(total_data)):
    segment.append(total_data[i])
    if i < len(total_data)-1:
        if total_data[i+1][2] - total_data[i][2] != 58:
            total_data_format.append(segment)
            segment = []

total_data_format.append(segment)

for i in range(len(total_data_format)):
    print(len(total_data_format[i]))


print("*"*40)
# 片段长度小于50的舍弃
for_remove = []
for each in total_data_format:
    if len(each) < 40:
        for_remove.append(each)

for each in for_remove:
    total_data_format.remove(each)

for i in range(len(total_data_format)):
    print(len(total_data_format[i]))


'''
输出成csv
如果时间戳不连续，则中间空一行
'''
out = open(merge_csv_path, 'w', encoding='utf8')
for lists in total_data_format:
    for each in lists:
        out.write(each[0]+','+each[1]+'\n')

out.close()