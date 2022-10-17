import os
from rich.console import Console


DIR = os.path.dirname(__file__)
console = Console()

if __name__ == '__main__':
    try:
        # 读取auto.csv文件
        pass
    except Exception as e:
        console.print(e)