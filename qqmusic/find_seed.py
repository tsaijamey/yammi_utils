import os
import platform


DIR = os.path.dirname(__file__)
if platform.system().lower() == 'windows':
    read_file_path = DIR + './seed.txt'
if platform.system().lower() == 'linux':
    read_file_path = DIR + '/seed.txt'

read_file = open(read_file_path, 'r', encoding='utf8')

mae = []
mse = []
for line in read_file:
    line = line.strip()
    error_name, value_ = line.split('：')
    if 'MAE' == error_name:
        mae.append(round(float(value_), 4))
    if 'MSE' == error_name:
        mse.append(round(float(value_), 4))

print(mae.index(min(mae)))
print(mse.index(min(mse)))