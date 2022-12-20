from qmlib import datasets_split
from qmlib import datasets_dealer
import pandas as pd

if __name__ == '__main__':

    PATH = ''
    while PATH == '':
        PATH = input('输入指定的历史数据csv文件路径：\n')

    name_result_dataset = PATH[:-4]+'_name_datasets.csv'
    number_result_dataset = PATH[:-4]+'_numer_datasets.csv'
    print(f'数据集将保存至：{PATH}')
    confirm = ''
    while confirm not in ['Y', 'y']:
        confirm = input('是否确认数据集路径？\n 是[y] 或者 否[N]')
        if confirm in ['N', 'n']:
            print('程序终止')
            exit(-1)
        else:
            continue


    # origin_datasets 是个分割成若干段落的数据记录的list
    origin_datasets = datasets_split(PATH)   # type = list

    # pprint.pprint(origin_datasets[-1][-5:])
    name_result_df = pd.DataFrame()
    number_result_df = pd.DataFrame()

    # each 对应的是一个段落的数据
    for each in origin_datasets:

        name_result_df = pd.concat([name_result_df, datasets_dealer(each, 8, result=3, only_for_train=1, data_type=2)],axis=0)
        number_result_df  = pd.concat([number_result_df, datasets_dealer(each, 8, result=3, only_for_train=1, data_type=0)],axis=0)

    print(name_result_df)
    name_result_df.to_csv(name_result_dataset, index=False)
    number_result_df.to_csv(number_result_dataset, index=False)