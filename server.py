import socket
import threading
import time

# 儲存連線的 client：{name: (conn, ip, port)}
clients = {}

def handle_client(conn: socket.socket, addr: tuple):
    try:
        name = conn.recv(1024).decode().strip()
        if not name:
            conn.close()
            return

        print(f"[{name}] 已連線")
        clients[name] = (conn, addr[0], addr[1])  # 存 socket、IP、Port
        client_online_list()

        while True:
            data = conn.recv(1024)
            if not data:
                break

            command = data.decode().strip()
            print(f"[{name}] 指令: {command}")

            if command == "list":
                online_list = "\n".join(f"{n}: {clients[n][1]}, {clients[n][2]}" for n in clients.keys())
                conn.sendall(f"[在線客戶端列表]\n{online_list}".encode())

            elif command.startswith("chat "):
                target_name = command[5:].strip()
                if target_name == name:
                    conn.sendall("[錯誤] 不能與自己聊天".encode())
                    continue

                if target_name in clients:
                    target_conn, target_ip, target_port = clients[target_name]
                    try:
                        # 發送邀請給對方
                        target_conn.sendall(f"[{name}] 想和你聊天，要接受嗎？(y/n)".encode())

                        # 等待對方回應
                        response = target_conn.recv(1024).decode().strip().lower()
                        if response == "y":
                            conn.sendall(f"[{target_name}] 已接受聊天".encode())
                            target_conn.sendall(f"[{name}] 已接受聊天".encode())

                            # 傳送 START_CHAT 給兩方
                            conn.sendall(f"START_CHAT {target_ip}:{target_port + 1000}".encode())
                            target_conn.sendall(f"START_CHAT {addr[0]}:{addr[1] + 1000}".encode())

                        else:
                            conn.sendall(f"[{target_name}] 拒絕了聊天".encode())
                    except:
                        conn.sendall(f"[錯誤] 無法與 {target_name} 建立連線".encode())
                else:
                    conn.sendall(f"[錯誤] 客戶端 {target_name} 不在線上".encode())

            else:
                conn.sendall("[錯誤] 不支援的指令".encode())

    except ConnectionError:
        pass
    finally:
        print(f"[{name}] 離線")
        conn.close()
        if name in clients:
            del clients[name]
        client_online_list()

def client_online_list():
    print("\n[目前在線的用戶]")
    for name, (_, ip, port) in clients.items():
        print(f"{name} - {ip}:{port}")
    print("-" * 30)

def main():
    host = "0.0.0.0"
    port = 8888

    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.bind((host, port))
    srv_sock.listen(5)

    print(f"[Server 啟動中] {host}:{port} 等待連線...")
    while True:
        conn, addr = srv_sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
