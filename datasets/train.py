import pandas as pd
from numpy import *
import deal_lib as inlib
import os
from rich.console import Console


console = Console()

# 读取数据集
DATA_PATH = os.path.dirname(__file__)
# CLF_DF = pd.read_csv(DATA_PATH+'all___20+1.csv').drop(columns=['time','item'])
REG_DF = pd.read_csv(DATA_PATH+'\\all_diff_20+1.csv').drop(columns=['time','item'])
# REG_DF = pd.read_csv(DATA_PATH+'test.csv')
# print(CLF_DF)
print(REG_DF)



# 指定目录为当前运行的脚本所在的目录
DIR = os.path.dirname(__file__)
console.print(f"[bold magenta]当前工作目录[/bold magenta]为：[red]{DIR}[/red]")

# clf = inlib.random_forest_clf_train(CLF_DF, DIR ,'result','clf_all_15___20221028_seed10.m')
# reg = inlib.random_forest_reg_train(REG_DF, DIR, 'result','reg_8_20221028_seed10.m')
reg = inlib.random_forest_reg_train(REG_DF, DIR, 'result','reg_5_20221220_seed10.m')