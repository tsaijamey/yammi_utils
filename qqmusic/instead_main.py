'''新版的主程序
'''


# 引用库
from base64 import encode
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
console = Console(theme=Theme({
    "pre": "bold purple blink",  # predict
    "re": "cyan bold blink",   # result
    "st": "#e3e3e3",  # statement
    "wa": "red bold",   # warning
    }))
import time
import datetime
import os
import traceback


# 自定义库
import instead_lib as inlib

# 预设变量
DIR = os.path.dirname(__file__)
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

# 每回合的数据列表，每回合都会变。
count_item          = []
offset_item         = []
item_copd = []

# 数据历史的列表，累计
position_history        = []
diff_history            = []

# 预设20个posi历史记录，方便开局就进行预测
for i in range(20):
    position_history.append(0)
# 预设20个diff历史记录，方便开局就进行预测
for i in range(20):
    diff_history.append(0)

reg_predict_history         = []
reg_predict_infact_error    = []

clf_predict_history = []

start_timestamp = 0
item_history = []
time_history = []
record_history = []


if __name__ == '__main__':
    
    try:
        while True:

            # 在获取结果时，容易因为点击意外导致列表为空，然后无法继续，因此增加这一段保障代码
            recent_result = []
            try_times = 0
            while len(recent_result) == 0 or len(recent_result[0]) == 0:
                inlib.screenshot_via_adb('shot.png')
                # 返回值是 [[名称] , [[时间, 时间戳]]]
                try:
                    recent_result = inlib.treasure_result_ocr(DIR + './img/shot.png')
                    try_times += 1
                    if (len(recent_result[0]) == 0) and try_times >= 3:
                        test_result = inlib.interface_ocr(DIR + './img/shot.png')
                        current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime( int( time.time() ) )  )
                        inlib.screenshot_via_adb('error_'+current_time+'.png')
                        exit(-1)
                except Exception as e:
                    print(e)

            # 区分第一次和后面的其他回合
            if start_timestamp == 0:
                print('路径1')
                # 获取第一次识别结果里的所有结果
                item_history.append(recent_result[0])
                time_history.append(recent_result[1][0])

                # 获得识别结果后，确定 计算时间的时间戳 如何计算
                start_timestamp = recent_result[1][1]
                record_history.append([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)), recent_result[0]])
                # 循环写入第一次识别的4个结果
                r = open(DIR+'./auto.csv', 'a', encoding='utf8')
                r.write(time_history[-1]+','+item_history[-1]+'\n')
                r.close()
                total = 1

            else:
                print('路径2')
                record_history.append([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)), recent_result[0]])
                if len(record_history) > 20:
                    record_history.pop(0)
                    
                    # 当个数超过20时，本回合即将消失的车头，如果会导致 4个小倍率的对应个数出现相等，应显示警告提示
                    no_head_record = record_history[1:]
                    no_head_count = inlib.item_sum(no_head_record)
                    # 设定一个测试是否有相同值的容器
                    equal_counter = []
                    for each in no_head_count[:4]:
                        # 逻辑如果 去头的统计值，4个物品有哪个没在这个容器里
                        if each not in equal_counter:
                            equal_counter.append(each)
                        else:
                            console.print(f'[wa]>>警告<<[/wa]发现下一回合会可能出现2个物品的数量相同')
                            console.print(f'[wa]>>不要下注<<[/wa]')



                r = open(DIR+'./auto.csv', 'a', encoding='utf8')
                r.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) + ',' + recent_result[0] + '\n')
                r.close()

                total += 1
                

            console.print('[st]最新记录：[/st]')
            console.print(record_history[-3:])
            console.print(f'总数：{total}')

            # 把出货历史，泛化成数字
            item_num_history = ''
            for each in record_history:
                if each[1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                    item_num_history += '{' + DICT[each[1]] + '}'
                else:
                    item_num_history += DICT[each[1]]

            if len(item_num_history) - item_num_history.count('{') - item_num_history.count('}') > 20:
                if item_num_history[0] == '{':
                    item_num_history = item_num_history[3:]
                else:
                    item_num_history = item_num_history[1:]   
            
            console.print(f'近20回合记录： {item_num_history}')
            # 保存上一次的记录
            if len(item_copd) > 0:
                last_copd = item_copd
            else:
                last_copd = []

            # 开始计算各项值
            count_item              = inlib.item_sum(record_history)
            offset_item             = inlib.item_offset(count_item)
            item_copd               = inlib.position_sorted(offset_item,count_item)

            # 这里追加的记录是上一个循环的各物品值，所以要用 last_copd
            '''
            如果预测效果不如预期，应把 last_copd 改回item_copd，且last_copd弃用。
            '''
            # if len(last_copd) > 0:
            #     for each in last_copd:
            #         if record_history[-1][1] in each:
            #             position_history.append(each[3])
            if len(item_copd) > 0:
                for each in item_copd:
                    if record_history[-1][1] in each:
                        position_history.append(each[3])

            # posi值的历史，最多不超过20个。
            if len(position_history) > 20:
                position_history.pop(0)
            
            # 适当时机，显示posi值的历史
            if len(position_history) > 0:
                console.print(f'POSI历史值：{position_history}')

                # 计算当前回合 各个物品的 Diff 值（预期值）
                for each in item_copd:
                    each[4] = each[3]-position_history[-1]

            # 适当时机，开始计算 diff值，计算的依据是最近2个posi值的差
            if len(position_history) >= 2:
                diff_history.append(position_history[-1] - position_history[-2])

            # diff值得历史，最多不超过20个。
            if len(diff_history) > 20:
                diff_history.pop(0)

            # 适当时机，显示 diff 值的历史
            if len(diff_history) > 0:
                console.print(f'DIFF历史值：{diff_history} | 历史值之和：{sum(diff_history)}')           
            
            # 根据Diff值的预测：
            if len(diff_history) == 20:
                reg_predict = inlib.load_rf_reg_model(DIR+'\\model\\rf_reg.m',diff_history).tolist()[0]
                console.print(reg_predict)
                if reg_predict == 0:
                    reg_predict_to_int = 0
                else:
                    reg_predict_to_int = int(reg_predict)

                reg_predict_history.append(reg_predict_to_int)

            # 格式化展示，方便查看数值
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("物品", style="dim", width=12)
            table.add_column("4 - 差分", justify="right", width=12)
            table.add_column("1 - 数量", justify="right", width=12)
            table.add_column("2 - 偏移", justify="right", width=12)
            table.add_column("3 - 位序", justify="right", width=12)            
            for each in item_copd:
                table.add_row(
                    each[0],
                    str(each[4])+'('+ str(reg_predict_to_int) +')',
                    str(each[1]),
                    str(each[2]),
                    str(each[3]),
                )

            console.print(table)

            
            # 预测的历史，只保留最近的20个。
            if len(reg_predict_history) > 21:
                reg_predict_history.pop(0)

            # 计算 预测diff 和 实际diff 的误差，存入 reg_predict_infact_error
            # 用于计算的 预测diff 来自 reg_predict_history[-2]
            if len(reg_predict_history) >= 2:
                if record_history[-1][1] in ['架子鼓','竖琴','萨克斯风','圆号']:
                    reg_predict_infact_error.append(str(diff_history[-1] - reg_predict_history[-2]))
                else:
                    reg_predict_infact_error.append(diff_history[-1] - reg_predict_history[-2])

                if len(reg_predict_infact_error) > 20:
                    reg_predict_infact_error.pop(0)
                console.print(f'[st]预测与实际结果的误差量（最后一个值，是上一次“预测”vs“实际”的结果）[/st]')
                console.print(f'{reg_predict_infact_error}')
                console.print(f'[st]历史预测值[/st]')
                console.print(f'[re]{reg_predict_history[:-1]}[/re]')
                console.print(f'[st]本次预测值[/st]：[pre]{reg_predict_history[-1]}[/pre]')


            # 根据4类特征值（共计32项）的预测：
            # item_offset_postion 的排序实际上是按位序值排列的，而算法需要的是按名称排序
            feature_pos         = []
            feature_diff        = []
            feature_dict = ['钢琴','小提琴','吉他','贝斯','架子鼓','竖琴','萨克斯风','圆号']
            for each in feature_dict:
                for list_ in item_copd:
                    if list_[0] == each:
                        feature_pos.append(list_[3])
                        feature_diff.append(list_[4])

            features = count_item + offset_item + feature_pos + feature_diff
            console.print(f'特征值：{features}')

            # clf_predict = inlib.load_rf_clf_model(DIR+'\\model\\rf_clf.m',features)
            # console.print(clf_predict)
            
            # clf_predic 的结果是 [diff汉字 , diff数值] 的形式
            # 要把 clf_predict 转化成 [物品,概率] 的形式
            # diff_predict_sort = []
            # for each in clf_predict:
            #     text_ = each[0]
            #     num_ = DIFF_DICT[text_]
            #     for list_ in 

            #     proba_ = each[1]




            inlib.wait_next(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_timestamp)) , 58)
            start_timestamp += 58

    except Exception as e:
        print(e,traceback.format_exc())

        # unsupported operand type(s) for -: 'int' and 'list'