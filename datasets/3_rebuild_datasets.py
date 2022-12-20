'''
把2_generate_train_set.py生成的数据集再进行加工，去掉那些pc~oc之和小于20的行
'''

getinput = input('重建的数据集路径：\n')

f = open(getinput, 'r', encoding='utf8')
li_str = ''
r = []
for line in f:
    l = line.strip()
    if 'po' not in l:
        data_list = l.split(',')
        if sum([int(data_list[0]), int(data_list[1]), int(data_list[2]), int(data_list[3]), int(data_list[4]), int(data_list[5]), int(data_list[6]), int(data_list[7])]) < 20:
            pass
        else:
            for each in data_list:
                li_str += each + ','
            
            r.append(li_str[:-1])
            li_str = ''
    else:
        r.append(l)

f.close()

w = open(getinput[:-4]+'_rebuilt.csv', 'w', encoding='utf8')

for each in r:
    w.write(each+'\n')
w.close()
