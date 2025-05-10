import socket

# 1. 建立一個 UDP socket
#    AF_INET 表示使用 IPv4；SOCK_DGRAM 表示使用 UDP 協議
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. 綁定要監聽的 IP 與埠號
#    這裡預設監聽本機的 0.0.0.0（所有網卡）和埠號 12345
HOST = '0.0.0.0'
PORT = 12345
sock.bind((HOST, PORT))
print(f"接收端啟動，監聽 {HOST}:{PORT} ...")

while True:
    # 3. 等待並接收資料
    #    recvfrom 回傳 (data, addr)，其中 addr 是送來端的 (IP, port) tuple
    data, addr = sock.recvfrom(1024)  # 最多接收 1024 bytes
    message = data.decode('utf-8')    # 解碼成字串
    print(f"收到來自 {addr[0]}:{addr[1]} 的訊息：{message}")
