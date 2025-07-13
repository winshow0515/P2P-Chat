import socket
import threading
import json
import time

# 接收訊息(server端或client端)
def receive_messages(sock):
    global mode, peer_addr,SERVER_ADDR
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
            
            if addr == SERVER_ADDR: #處理來自server的訊息
                if msg['type'] == "register":
                    print(msg['response'])
                    mode = "server" #回到server模式

                elif msg['type'] == 'list':
                    print(f"\n[在線客戶端列表]\n{msg['clients']}")

                elif msg['type'] == 'chat':# 收到聊天邀請
                    mode = "responding" #切換到回應模式
                    peer_addr = tuple(msg['addr']) #更新對方ip, port
                    print(f"\n> [{msg['name']}]邀請進行1v1聊天，是否接受聊天邀請? (yes/no): ")

                elif msg['type'] == 'chat_response': #被server拒絕
                    print(msg['response'])
                    mode = "server" #回到server模式


            else: #處理來自1v1聊天室的聊天訊息
                if msg['type'] == 'chat_response':
                    if msg['response'] == 'yes':
                        print(f"\n[對方已接受你的聊天邀請]")
                        peer_addr = tuple(msg['my_addr']) #更新對方ip, port
                        mode = "chatting" #切換到聊天模式
                        sock.sendto(json.dumps({"type": "isChating", "status": True, "name": my_name}).encode("utf-8"), SERVER_ADDR)
                    else:
                        print(f"\n[對方拒絕了你的聊天邀請]")
                        mode = "server" #回到server模式

                elif msg['type'] == 'chat':
                    print(f"\n[{msg['name']}]: {msg['message']}\n請輸入訊息 (或輸入 'exit' 離開): ", end="")
                
                elif msg['type'] == 'logout':
                    print(f"\n[{msg['name']}] 已離線")
                    print("現在可以對server輸入指令了")
                    mode = "server" #回到server模式
                    sock.sendto(json.dumps({"type": "isChating", "status": False, "name": my_name}).encode("utf-8"), SERVER_ADDR)
                    
        except ConnectionError as e:
            print("\n[連線已斷開] {e}")
            break

def send_message(sock):
    global mode, my_name, SERVER_ADDR, peer_addr
    
    #初次連線，先跟server報備身分
    mode = "waiting_response" #等待server回應
    print("正在等待 server 回應...")
    msg = {"type":"register", "name": my_name}
    sock.sendto(json.dumps(msg).encode(), SERVER_ADDR)
    
    
    while True:
        if mode == "waiting_response":  #等待回應
            time.sleep(0.1)
            continue 

        msg = input("> 請輸入訊息(或輸入 'exit' 離開): ")

        if mode == "server":    #向server發送指令
            if msg.strip().lower() == "exit":
                sock.sendto(json.dumps({"type": "logout", "name": my_name}).encode("utf-8"), SERVER_ADDR)
                print("[結束通訊]")
                break
            
            elif msg.strip().lower() == "help":
                print("exit : 離開\nlist : 列出現在在線的名單\nchat name : 發出1v1聊天邀請，請將name換成對象的名字")
                
            elif msg.strip().lower() == "list":# 請求在線列表
                sock.sendto(json.dumps({"type": "list"}).encode("utf-8"), SERVER_ADDR)
                
            elif msg.strip().startswith("chat "):# 發送聊天邀請
                target_name = msg[5:].strip()
                sock.sendto(json.dumps({"type": "chat", 
                                        "name": my_name, 
                                        "target": target_name}).encode("utf-8"), SERVER_ADDR)
                print("正在等待對方回應...")
                mode = "waiting_response" #等待對方回應
        
        elif mode == "responding": #回應對方的聊天邀請
            if msg in ["yes", "no"]:
                sock.sendto(json.dumps({"type": "chat_response", 
                                    "name": my_name, 
                                    "my_addr": (my_ip, my_port),
                                    "response": msg.lower()}).encode("utf-8"), peer_addr)
                
                if msg.lower() == "yes":
                    print(f"\n[已接受對方的聊天邀請]")
                    mode = "chatting"
                    sock.sendto(json.dumps({"type": "isChating","status": True, "name": my_name}).encode("utf-8"), SERVER_ADDR)
                    
                else:
                    print(f"\n[拒絕了對方的聊天邀請]")
                    mode = "server"
            else:
                print("請輸入 'yes' 或 'no'")
                continue
        
        elif mode == "chatting": #在1v1聊天室中聊天
            if msg.strip().lower() == "exit":
                sock.sendto(json.dumps({"type": "logout", "name": my_name}).encode("utf-8"), peer_addr)
                print("已離開1v1聊天室，現在可以對server輸入指令了")
                mode = "server"
                sock.sendto(json.dumps({"type": "isChating", "status": False, "name": my_name}).encode("utf-8"), SERVER_ADDR)
            
            elif msg.strip():# 普通發送聊天訊息給對方
                sock.sendto(json.dumps({"type": "chat", 
                                        "name": my_name, 
                                        "message": msg}).encode("utf-8"), peer_addr)
                
        time.sleep(0.01)


#初始化
my_ip = input("請輸入自己的 IP: ").strip()
my_port = int(input("請輸入自己的 Port: ").strip())
my_name = input("請輸入自己的名稱: ").strip()
cli_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cli_sock.bind((my_ip, my_port))

SERVER_ADDR = ("192.168.0.239", 8888)

#"server", "waiting_response", "responding", "chatting"
mode = "server" #預設對象為server

peer_addr = ("", None)#聊天對象的ip, port


threading.Thread(target=receive_messages, args=(cli_sock,), daemon=True).start()
send_message(cli_sock)