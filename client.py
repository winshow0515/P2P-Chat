import socket
import threading
import json
import time

# 接收訊息(server端或client端)
def receive_messages(sock):
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if not data:
                print("\n[連線已斷開]")
                break
            try:
                msg = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                print(f"[無法解析 JSON] 收到：{data}")
                continue
            
            if msg['type'] == "register":
                print(msg['response'])
            elif msg['type'] == 'list':
                print(f"\n[在線客戶端列表]\n{msg['clients']}")
            else:
                pass
                
        except ConnectionError:
            break

def send_message(sock):
    #初次連線，先跟server報備身分
    msg = {"type":"register", "name": my_name}
    sock.sendto(json.dumps(msg).encode(), (peer_ip, peer_port))


    while True:
        msg = input("> 請輸入訊息: ")
        if msg.strip().lower() == "exit":
            sock.sendto(json.dumps({"type": "logout", "name": my_name}).encode("utf-8"), (peer_ip, peer_port))
            print("[結束通訊]")
            break
        elif msg.strip().lower() == "list":
            # 請求在線列表
            sock.sendto(json.dumps({"type": "list"}, ensure_ascii=False).encode("utf-8"), (peer_ip, peer_port))

        time.sleep(0.01)


#初始化
my_ip = input("請輸入自己的 IP: ").strip()
my_port = int(input("請輸入自己的 Port: ").strip())
my_name = input("請輸入自己的名稱: ").strip()
cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cli_sock.bind((my_ip, my_port))
#預設對象為server
peer_ip = "127.0.0.1"
peer_port = 8888

threading.Thread(target=receive_messages, args=(cli_sock,), daemon=True).start()
send_message(cli_sock)