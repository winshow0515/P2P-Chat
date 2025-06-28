import threading
import time
import random
count = 0

lock = threading.Lock()
def worker():
    global count
    for _ in range(10):
        # 這裡的 += 操作其實包含讀取、加 1、寫回 三步
        # lock: 只有一個人可以拿到這個 lock，其他thread拿不到就會在這邊卡著，直到有人釋放為止
        # 釋放: 出去 with 的這個區間就會自動釋放
        # 或者可以使用 lock.acquire(), lock.realease() 手動要求跟釋放
        with lock:
            a = count
            time.sleep(random.random()/10)
            a = a + 1
            count = a
            time.sleep(random.random()/10)

t1 = threading.Thread(target=worker)
t2 = threading.Thread(target=worker)
t1.start(); t2.start()
t1.join(); t2.join()
print(count)  # 預期 20，但往往小於 20