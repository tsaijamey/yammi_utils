import os
import datetime

read_auto = open(r'C:\Users\yammi\OneDrive\0_caijia\1_code\python\yammi_utils\yammi_utils\qqmusic\auto.csv', 'r', encoding='utf8')
read_temp = open(r'C:\Users\yammi\OneDrive\0_caijia\1_code\python\yammi_utils\yammi_utils\input\qmdata0819\temp.csv', 'r', encoding='utf8')

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

print(len(total_data))

unique_check = []
remove_list = []
for each in total_data:
    if each[2] in unique_check:
        remove_list.append(each)
    else:
        unique_check.append(each[2])

for each in remove_list:
    total_data.remove(each)

out = open(r'C:\Users\yammi\OneDrive\0_caijia\1_code\python\yammi_utils\yammi_utils\input\qmdata0819\merge_result.csv', 'w', encoding='utf8')

for i in range(len(total_data)):
    if i > 0:
        if total_data[i][2] - total_data[i-1][2] > 58:
            out.write('\n')
    out.write(total_data[i][0]+','+total_data[i][1]+'\n')

out.close()