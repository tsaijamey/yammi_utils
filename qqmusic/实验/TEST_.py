import os
from rich.console import Console

console = Console()
DIR = os.path.dirname(__file__)
console.print(DIR+'\\model\\rf_reg.m')