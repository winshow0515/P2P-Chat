import socket
import threading
import json
import time

# 在線名單 name: (socket, (ip, port))
clients = {}

# 接收client來的指令並處理
def receive_messages(sock):
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if not data:
                print("\n[連線已斷開]")
                break
            msg = json.loads(data.decode())
            print(msg)
            if msg['type'] == "register":
                # 新客戶端連線，記錄下來，假設用戶名不重複
                name = msg["name"]
                clients[name] = (sock, addr)
                print(f"[{name}] 已連線，IP: {addr[0]}, Port: {addr[1]}")
                sock.sendto(json.dumps({'type': "register", 'response': "Hi 這裡是 server."}, ensure_ascii=False).encode("utf-8"), addr)
            
            elif msg['type'] == "list":
                online_list = "\n".join(f"{n}: {clients[n][1]}" for n in clients.keys())
                sock.sendto(json.dumps({"type": "list", "clients": online_list}).encode(), addr)
                
            elif msg['type'] == "logout":
                del clients[msg["name"]]
                print(f"[{msg['name']}] 已離線")
            elif msg['type'] == "chat":
                pass

        except ConnectionError:
            break



#初始化
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ser_ip = "0.0.0.0"
ser_port = 8888
server_sock.bind((ser_ip, ser_port))
print(f"[Server 啟動中] 0.0.0.0 : 8888 等待連接")

threading.Thread(target=receive_messages, args=(server_sock,), daemon=True).start()
while True:
    inp = input(">")
    if inp.strip().lower() == "exit":
        print("[結束通訊]")
        break