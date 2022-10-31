from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from pandas import DataFrame, array
from numpy import *
import copy
import joblib


class DataAnalytics:
    '''
    输入：一串字符 和 一个数字
    方法：格式化 字符串，生成列表
    输出：列表，形如： ['1','2','3','4','5','6','7','8']
    s：代表顺序时间下依次出现的乐器。
    counter：限定数据片段的长度。
    '''    
    def __init__(self,s:str,c:int):
        self.s = s
        self.counter = c
        if len(s) >= c:
            self.s = s[-c:]   # 当 s的长度 超过 counter量 时，截取 倒数counter个 字符
    
    def formatted(self)  -> list:
        return list(self.s)

def counters_8(s:list)  -> list:
    '''
    输入：字符数据列表，形如： ['1','2','3','4','5','6','7','8']，左右对应顺序 = 钢琴->圆号
    输出：列表，形如：[20, 20, 19, 19, 4, 2, 1, 0]，左右对应顺序 = 钢琴->圆号
    '''
    counter = [0,0,0,0,0,0,0,0]
    for i in range(8):
        counter[i] = s.count(str(i+1))
    return counter

def counters_5(s:list):
    '''
    用途：以5维数据方式，统计“钢琴”、“小提琴”、“吉他”、“贝斯”、“大怪”的数量
    输入s为物品列表
    输出counters为上述5种物品的统计值
    '''
    counters = [0,0,0,0,0]
    for i in range(4):
        counters[i] = s.count(str(i+1))
    counters[4] = s.count('5') + s.count('6') + s.count('7') + s.count('8')
    return counters

def calcOffset_8(counter:list) -> list:
    '''
    输入：乐器数量统计列表，形如：[20, 20, 19, 19, 4, 2, 1, 0]，左右对应顺序 = 钢琴->圆号
    输出：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->圆号
    '''
    rates = [0.200, 0.200, 0.200, 0.200, 0.091, 0.046, 0.037, 0.026]
    all = sum(counter)
    offset = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    for i in range(8):
        offset[i] = round(100*(counter[i]/all - rates[i]), 2)

    # print(f'本次偏移值：{offset}')
    return offset

def calcPositionSort_8_nodivi(offsets:list) -> list:
    '''
    输入：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->圆号
    输出：[乐器编号, 位序值] 的2d数组，形如：[[x, y], [x, y], [x, y], [x, y], [x, y], [x, y], [x, y], [x, y]]，左右对应顺序 = 钢琴->圆号
    '''
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']

    # 多维列表的排序问题解决方法：https://www.youtube.com/watch?v=EPIUxGOynE0
    items_offsets = [list(t) for t in zip(items,offsets)]    
    items_offsets.sort(key=lambda x: x[1], reverse=1)

    return items_offsets    # 【注意】输出的是个二维数组，需要调用 a[i][0] 来获取乐器编号，调用 a[i][1] 来获取位序值


def calcPositionSort_8_divi(offsets:list) -> list:
    '''
    输入：乐器已知概率与目标概率的偏移量，形如：[xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x, xx.x]，左右对应顺序 = 钢琴->圆号
    输出：[乐器编号, 偏移值] 的2d数组，形如：[[大, y], [大, y], [小, y], [小, y], [小, y], [小, y], [大, y], [大, y]]
    '''
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']

    # 多维列表的排序问题解决方法：https://www.youtube.com/watch?v=EPIUxGOynE0
    # 把8种乐器分为两组，分别进行排序，排序后把结果合并到一个数组里：
    items_offset_left = [list(t) for t in zip(items[0:4],offsets[0:4])]
    items_offset_left.sort(key=lambda x: x[1], reverse=1)

    items_offset_right = [list(t) for t in zip(items[4:8],offsets[4:8])]
    items_offset_right.sort(key=lambda x: x[1], reverse=1)

    items_position_sort = []
    items_position_sort.append(items_offset_right[2])
    items_position_sort.append(items_offset_right[1])
    items_position_sort.append(items_offset_left[3])
    items_position_sort.append(items_offset_left[0])
    items_position_sort.append(items_offset_left[1])
    items_position_sort.append(items_offset_left[2])
    items_position_sort.append(items_offset_right[0])
    items_position_sort.append(items_offset_right[3])

    return items_position_sort

# 输入：[乐器名称, 偏移值] 的2d列表
# 输出：[乐器名称，位序值] 的2d列表，，左右对应顺序 = 钢琴 -> 圆号
def calcPosition(items_postion_sort:list) -> list:
    # 先用deepcopy复制一下入参。
    # 因为入参是 2d列表， cppy函数是无法传递 2d 数据的。
    # 涉及到修改列表值的问题，所以要复制，不要直接在入参上修改，否则原始列表值也会被替换。
    temp = copy.deepcopy(items_postion_sort)
    for i in range(8):
        # 把偏移值根据 index 转换成 int数值，从 8 到 1
        temp[i][1] = i + 1
    
    output = []
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']
    for each in items:
        for x in temp:
            if each in x:
                output.append(x)
    
    return output

# 输入：([[钢琴, y], [小提琴, y] ... [圆号, y]],上一次乐器对应的位序值)
def calDiffSort_8_divi(items_position:list,last_pos:int):
    items = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']
    diff_init = [0,0,0,0,0,0,0,0]
    items_diff = [list(x) for x in zip(items,diff_init)]
    # 合成的结果是 [['钢琴',0],['小提琴',0],['吉他',0],['贝斯',0],['架子鼓',0],['竖琴',0],['萨克斯风',0],['圆号',0]]
    
    for each in items_position:
        if each[0] == '钢琴':
            items_diff[0][1] = each[1] - last_pos
        elif each[0] == '小提琴':
            items_diff[1][1] = each[1] - last_pos
        elif each[0] == '吉他':
            items_diff[2][1] = each[1] - last_pos
        elif each[0] == '贝斯':
            items_diff[3][1] = each[1] - last_pos
        elif each[0] == '架子鼓':
            items_diff[4][1] = each[1] - last_pos
        elif each[0] == '竖琴':
            items_diff[5][1] = each[1] - last_pos
        elif each[0] == '萨克斯风':
            items_diff[6][1] = each[1] - last_pos
        elif each[0] == '圆号':
            items_diff[7][1] = each[1] - last_pos

    #items_diff.sort(key=lambda x: x[1], reverse=1)
        
    return items_diff


# 把4种低概率乐器视为一个乐器，计算当前的偏移量
def calcOffset_5(counter:list):
    calc_all = 0
    for x in counter:
        calc_all += x

    offset = [0,0,0,0,0]
    offset[0] = round(100*(counter[0]/calc_all - 0.200),2)
    offset[1] = round(100*(counter[1]/calc_all - 0.200),2)
    offset[2] = round(100*(counter[2]/calc_all - 0.200),2)
    offset[3] = round(100*(counter[3]/calc_all - 0.200),2)
    offset[4] = round(100*(counter[4]/calc_all - 0.200),2)

    return offset

# 把4种乐器视为一种新乐器，计算偏移量的排序
# *注意，输出的是个二维数组，需要调用 a[i][0] 来获取乐器编号，调用 a[i][1] 来获取位序值
def calcPositionSort_5(offsets:list):
    items = ['钢琴','小提琴','吉他','贝斯','稀有']

    # 多维列表的排序问题解决方法：https://www.youtube.com/watch?v=EPIUxGOynE0
    items_offset = [list(t) for t in zip(items,offsets)]
    # lambda的意思，见这篇博客：https://blog.csdn.net/qq_40169189/article/details/108070945
    # x:x[1]，是指定了排序的列表项，即列表中每一项的第二个项值。
    # reverse=1表示倒叙，从大到小
    items_offset.sort(key=lambda x: x[1], reverse=1)
    return items_offset

def clf(trainset:DataFrame, predict_data:list, column_name:str) -> array:
    '''
    用途：决策分类
    输入trainset：DataFrame格式的数据表，为训练数据集
    输入predict_data：列表格式的待预测数据
    输出：置信度最高的决策结果
    '''
    X = trainset.drop(columns=column_name)  # 分割训练集的X部分
    y = trainset[column_name]   # 分割训练集的y部分

    tree_clf = DecisionTreeClassifier()
    tree_clf.fit(X.values,y.values)
    tree_clf_prediction = tree_clf.predict([predict_data])    
    return tree_clf_prediction.tolist()[0]

def clf_proba(train_set:DataFrame, predict_data:list, column_name:str) -> array:
    '''
    用途：决策分类
    输入trainset：DataFrame格式的数据表，为训练数据集
    输入predict_data：列表格式的待预测数据
    输出：所有分类的置信度
    '''
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]

    tree_clf = DecisionTreeClassifier()
    tree_clf.fit(X.values,y.values)
    tree_clf_pred_proba = tree_clf.predict_proba([predict_data])
    # 因为预测结构是array类型，希望输出的是列表，所以这里应该输出的是预测结果的tolist()
    return tree_clf_pred_proba.tolist()[0]

def reg(train_set:DataFrame,depth:int,predict_data:list, column_name:str) -> array:
    '''
    用途：决策回归
    输入trainset：DataFrame格式的数据表，为训练数据集
    输入depth：梯度
    输入predict_data：列表格式的待预测数据
    输出：回归预测值
    '''
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]

    tree_reg = DecisionTreeRegressor(max_depth=depth)
    tree_reg.fit(X.values,y.values)
    tree_reg_prediction = tree_reg.predict([predict_data])

    return tree_reg_prediction.tolist()[0]

# 随机森林决策树分类 -> 返回的是置信度最高的值
def rf_clf(train_set:DataFrame, predict_data:list, column_name:str) -> array:
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    rnd_clf = RandomForestClassifier(n_estimators=60, max_leaf_nodes=20, n_jobs=-1)
    rnd_clf.fit(X.values, y.values)
    rnd_clf_prediction = rnd_clf.predict([predict_data])

    return rnd_clf_prediction.tolist()[0]

# 随机森林决策树分类 -> 返回的是置信度排序
# 输出：[预测值, 预测概率]
def rf_clf_proba(train_set:DataFrame,predict_data,column_name:str) -> array:
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    model = RandomForestClassifier(n_estimators=300, max_leaf_nodes=20, n_jobs=-1)
    model.fit(X.values, y.values)

    rnd_clf_prediction_proba = model.predict_proba([predict_data]).tolist()[0]

    # 提取随机森林投票的标签  clf.classes_
    labels_list = []
    for each in model.classes_:
        labels_list.append(each)
    
    proba_list = []
    for each in rnd_clf_prediction_proba:
        proba_list.append(round(each,2))
   
    output_list = list(t for t in zip(labels_list, proba_list))
    output_list.sort(key=lambda x: x[1],reverse=1)

    # 返回值的形式：
    # return [rnd_clf_prediction.tolist()[0], rnd_clf_prediction_proba.tolist()[0]]
    return output_list

def random_forest_clf_train(train_set:DataFrame,dir_name:str,column_name:str):
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    model = RandomForestClassifier(n_estimators=300, max_leaf_nodes=20, n_jobs=-1)
    model.fit(X.values, y.values)

    joblib.dump(model, dir_name+"./model/rf_clf.m")

def load_rf_clf_model(model_path:str, predict_data):
    clf = joblib.load(model_path)
    rnd_clf_prediction_proba = clf.predict_proba([predict_data]).tolist()[0]

    # 提取随机森林投票的标签  clf.classes_
    labels_list = []
    for each in clf.classes_:
        labels_list.append(each)
    
    proba_list = []
    for each in rnd_clf_prediction_proba:
        proba_list.append(round(each,2))
   
    output_list = list(t for t in zip(labels_list, proba_list))
    output_list.sort(key=lambda x: x[1],reverse=1)

    # 返回值的形式：
    # return [rnd_clf_prediction.tolist()[0], rnd_clf_prediction_proba.tolist()[0]]
    return output_list


def random_forest_reg_train(train_set:DataFrame,dir_name:str,column_name:str):
    X = train_set.drop(columns=column_name)
    y = train_set[column_name]
    model = RandomForestRegressor(n_estimators=300, criterion='squared_error', max_leaf_nodes=20, n_jobs=1)
    model.fit(X.values, y.values)

    joblib.dump(model, dir_name+"/model/rf_reg_1.1.3.m")


def load_rf_reg_model(model_path:str, predict_data):
    reg = joblib.load(model_path)
    prediction = reg.predict([predict_data])
    
    return prediction