import socket

# 1. 建立一個 UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. 讓使用者輸入目標 IP 和埠號
target_ip = input("請輸入接收端的 IP（例如 127.0.0.1）：")
target_port = int(input("請輸入接收端的埠號（例如 12345）："))

print("輸入空白訊息可結束程式。")

while True:
    # 3. 讀取使用者輸入的字串
    message = input("請輸入要傳送的訊息：")
    if message == "":
        print("結束發送。")
        break

    # 4. 編碼成 bytes，並發送到指定的 IP、埠號
    data = message.encode('utf-8')
    sock.sendto(data, (target_ip, target_port))
    print(f"已發送到 {target_ip}:{target_port}")