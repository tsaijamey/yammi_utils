def item_sum_V(item_record:list) -> list[int]:
    '''统计输入的物品列表中，各物品总数
    其中，架子鼓、竖琴、萨克斯风、圆号视为一个物品
    最终输出为：[a,b,c,d,e]
    '''
    dict = ['钢琴', '小提琴', '吉他', '贝斯', '架子鼓', '竖琴', '萨克斯风', '圆号']
    item_merge = []
    counter = []

    # 输入的列表是 [时间,物品] 把物品抽离出来，合并到单独的列表
    for each in item_record:
        item_merge.append(each[1])
    # 按照
    for each in dict:
        counter.append(item_merge.count(each))
    
    big = sum(counter[4:])
    counter = counter[:4]
    counter.append(big)
    return counter

def item_offset_V(item_counter:list) -> list[float]:
    '''
    输入：乐器数量统计列表，形如：[20, 20, 19, 19, 19]，左右对应顺序 = 钢琴->大
    输出：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->大
    '''
    rates = [0.200, 0.200, 0.200, 0.200, 0.200]
    all = sum(item_counter)
    offset = [0.0, 0.0, 0.0, 0.0, 0.0]

    for i in range(5):
        offset[i] = round(100*(item_counter[i]/all - rates[i]), 2)

    return offset

def position_sorted_V(offset:list,counter:list) -> list[str,int]:
    '''
    输入：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->大
    输出：[乐器编号, 偏移值] 的2d数组，形如：[[大, y], [大, y], [小, y], [小, y], [小, y]]
    输出的排序：[7,6,4,1,2,3,5,8]，左右侧之和都是18
    '''
    items = ['钢琴','小提琴','吉他','贝斯','大']
    input_sort = [list(t) for t in zip(items,counter,offset,[0,0,0,0,0],[0,0,0,0,0])]
    input_sort.sort(key=lambda x: x[2], reverse=1)

    sort_id = [1,2,3,4,5]
    for i in range(5):
        input_sort[i][3] = sort_id[i]

    input_sort.sort(key=lambda x: x[3], reverse=1)

    return input_sort

from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from pandas import DataFrame
import joblib

def random_forest_reg_train(train_set:DataFrame,dir_name:str,column_name:str, model_name):
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    model = RandomForestRegressor(n_estimators=300, criterion='squared_error', max_leaf_nodes=20, n_jobs=1,random_state=42)
    # model = RandomForestRegressor(random_state=75)
    model.fit(X.values, y.values)

    joblib.dump(model, dir_name+"\\"+model_name)