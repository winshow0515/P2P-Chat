import socket
import threading
import json
import time

# 在線名單 name: ((ip, port), isChatting)
clients = {}
fmt = "\n| {: ^10s} | {: ^10s} |"

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

            if msg['type'] == "register":# 新客戶端連線，記錄下來，假設用戶名不重複
                name = msg["name"]
                clients[name] = (addr, False)  # ((ip, port), isChatting)
                print(f"[{name}] 已連線，IP: {addr[0]}, Port: {addr[1]}")
                sock.sendto(json.dumps({'type': "register", 'response': "Hi 這裡是 server."}).encode("utf-8"), addr)
                print(f"[在線客戶端列表] {clients}")

            elif msg['type'] == "list":
                temp = fmt.format("name", "isChatting")+fmt.format("-"*10, "-"*10)
                for i in clients:
                    temp += fmt.format(i, str(clients[i][1]))
                sock.sendto(json.dumps({"type": "list", "clients": temp}).encode("utf-8"), addr)
                
            elif msg['type'] == "logout":
                del clients[msg["name"]]
                print(f"[{msg['name']}] 已離線")
            
            elif msg['type'] == "chat":# 轉達聊天邀請
                target_name = msg['target']
                if target_name not in clients:
                    sock.sendto(json.dumps({"type": "chat_response", "response": f"[錯誤] 客戶端 {target_name} 不在線上"}).encode("utf-8"), addr)
                    print(f"[錯誤] 客戶端 {target_name} 不在線上")
                    continue
                if clients[target_name][1]:  # 如果對方正在聊天
                    sock.sendto(json.dumps({"type": "chat_response", "response": f"[錯誤] 客戶端 {target_name} 正在跟別人聊天中"}).encode("utf-8"), addr)
                    print(f"[錯誤] 客戶端 {target_name} 正在聊天中")
                    continue
                #轉達聊天邀請
                target_addr = clients[target_name][0]  # (ip, port)
                response_msg = {
                    "type": "chat",
                    "name": msg["name"],
                    "addr" : addr
                }
                print(response_msg)
                sock.sendto(json.dumps(response_msg).encode("utf-8"), target_addr)
            
            elif msg['type'] == "isChating":# 更新聊天狀態
                name = msg["name"]
                is_chatting = msg["status"]
                if name in clients:
                    clients[name] = (clients[name][0], is_chatting)
                

        except ConnectionError:
            break



#初始化
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ser_ip = input("請輸入你的IP: ")#"192.168.0.229"
ser_port = int(input("請輸入你的port: "))
server_sock.bind((ser_ip, ser_port))
print(f"[Server 啟動中] {ser_ip} : {ser_port} 等待連接")

threading.Thread(target=receive_messages, args=(server_sock,), daemon=True).start()
while True:
    inp = input(">")
    if inp.strip().lower() == "exit":
        print("[結束通訊]")
        break