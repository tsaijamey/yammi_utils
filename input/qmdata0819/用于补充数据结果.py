import os
import datetime

dict = {
    "1":"钢琴",
    "2":"小提琴",
    "3":"吉他",
    "4":"贝斯",
    "5":"架子鼓",
    "6":"竖琴",
    "7":"萨克斯风",
    "8":"圆号",
}

DIR = os.path.dirname(__file__)
f = open(DIR+'./temp.csv','a', encoding='utf8')
f.write('\n')
start_time = '2022-10-16 21:47:49'
time_ = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
print(time_)
time_ = int(datetime.datetime.timestamp(time_))

while True:
    input_ = input('Item编号：\n')
    if input_ != '0':
        name_ = dict[input_]
        print(str(datetime.datetime.fromtimestamp(time_)))
        print(name_)
        f.write(str(datetime.datetime.fromtimestamp(time_))+','+name_+'\n')
        time_ = time_ + 58

    else:
        break

f.close()