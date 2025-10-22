# cpu_load.py
import time

def compute_heavy_task():
    # 执行一个占用 CPU 的计算任务 (例如多次平方根计算)
    result = 0
    for i in range(1, 10000000):
        result += i * i / (i + 1)
    return result

print("Starting single CPU core load...")
while True:
    # 重复执行计算任务
    compute_heavy_task()