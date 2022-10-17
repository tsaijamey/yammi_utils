'''
本脚本的目的，是仅对 all_num_datasets_rebuild的最后一列进行修改

原列存储的是中文字的数值，把它们变成阿拉伯数字
'''

import os

DIR = os.path.dirname(__file__)
read_csv = open(DIR+'./all_num_datasets_rebuilt.csv', 'r', encoding='utf8')

# 对照字典
diff_text_dict = {'负七':-7, '负六':-6, '负五':-5, '负四':-4, '负三':-3, '负二':-2, '负一':-1, '零':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7}

for line in read_csv:
    line = line.strip()
    