from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from numpy import *
import copy
import joblib
from kingdoms import random_forest_reg_train
import os
from rich.console import Console


console = Console()

# 读取数据集
DATA_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '\\input\\qmdata0819\\'
REG_DF = pd.read_csv(DATA_PATH+'all_num_datasets_rebuilt.csv')

# 指定目录为当前运行的脚本所在的目录
DIR = os.path.dirname(__file__)
console.print(f"[bold magenta]当前工作目录[/bold magenta]为：[red]{DIR}[/red]")

reg = random_forest_reg_train(REG_DF, DIR ,'item_num')