from multiprocessing.util import is_exiting
import os
import sys


# 遍历文件夹下的文件，返回文件名
def readDirFiles(path:str) -> list:
    '''
    输入：路径
    输出：文件名及路径（列表）
    '''
    if os.path.isfile(path):
        print('YammiUtils: Path is a file.')
        if "\\" in path:
            print("YammiUtils: OS is Windows")
            filename = path.split('\\')[-1]
        elif "/" in path:
            print("YammiUtils: OS is Linux/Unix")
            filename = path.split('/')[-1]
        
        files = [filename, path]
        print(files)
        return files
    if os.path.isdir(path):
        print('YammiUtils: Path is a DIR.')
        for (i,j,k) in os.walk(path):
            for each in k:
                print(i)
                print(j)
                print(each)
                print("*"*50)


'''
Testing
'''

readDirFiles(r"D:\OneDrive\桌面\我的")