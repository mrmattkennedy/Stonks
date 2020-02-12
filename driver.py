import sys
import os
import subprocess
from pathlib import Path

system = os.name
if system == 'nt': #Windows
    pid = subprocess.Popen(["pythonw.exe", sys.path[0] + "\\modules\\stonks_main.py"])
elif system == 'posix':
    pid = subprocess.Popen(["pythonw.exe", sys.path[0] + "//modules//stonks_main.py"], shell=True)
