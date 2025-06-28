import multiprocessing
import threading
import time
import random

worker = 4
progressing = [0, 0, 0, 0]
def job(proc_name, idx):
    for i in range(1, 6):
        delay = random.randint(1, 3)
        time.sleep(delay)
        progressing[idx] += 1
        print(f"{proc_name}: iteration {i}", progressing)

def multi_processing_example():    
    num_processes = worker  # 你可以改成任意进程数
    processes = []

    for idx in range(num_processes):
        p = multiprocessing.Process(target=job, args=(f'Process-{idx}', idx))
        p.start()
        processes.append(p)

    while any(p != 5 for p in progressing):
        print(progressing)
        time.sleep(0.5)

    # 等待所有子进程结束
    for p in processes:
        p.join()
        print("One process finished.")

    print("All processes finished.")

def multi_thread_example():
    threads = []
    # 启动 worker 个线程
    for idx in range(worker):
        t = threading.Thread(target=job, args=(f"Thread-{idx}", idx))
        t.start()
        threads.append(t)

    # 主线程监控所有子线程进度
    while any(p != 5 for p in progressing):
        print(progressing)
        time.sleep(0.5)

    # 等待所有子线程结束
    for t in threads:
        t.join()
        print("One thread finished.")

    print("All threads finished.")

if __name__ == '__main__':
    # multi_processing_example()
    multi_thread_example()
