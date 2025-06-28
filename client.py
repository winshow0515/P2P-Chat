import socket
import threading
import time

def private_chat_listener(my_ip, my_port):  # 允許別人連過來
    def handle_peer(peer_conn, peer_addr):
        print(f"\n[私聊連線] 來自 {peer_addr}")
        def receive_from_peer(sock):
            while True:
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    print(f"\n< 對方: {data.decode()}")
                except:
                    break

        threading.Thread(target=receive_from_peer, args=(peer_conn,), daemon=True).start()

        while True:
            msg = input("> (私聊中) 輸入訊息: ")
            if msg.strip().lower() == "exit":
                break
            peer_conn.sendall(msg.encode())
        peer_conn.close()
        print("[已離開私聊]")

    def listen():
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_sock.bind((my_ip, my_port + 1000))
        listen_sock.listen(1)
        print(f"[私聊監聽中] {my_ip}:{my_port + 1000}")
        while True:
            conn, addr = listen_sock.accept()
            threading.Thread(target=handle_peer, args=(conn, addr), daemon=True).start()

    threading.Thread(target=listen, daemon=True).start()

def start_private_chat(peer_ip, peer_port):  # 主動連線
    try:
        chat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        chat_sock.connect((peer_ip, peer_port))
        print("[私聊開始] 輸入 exit 離開私聊")

        def receive_from_peer(sock):
            while True:
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    print(f"\n< 對方: {data.decode()}")
                except:
                    break

        threading.Thread(target=receive_from_peer, args=(chat_sock,), daemon=True).start()

        while True:
            msg = input("> (私聊中) 輸入訊息: ")
            if msg.strip().lower() == "exit":
                break
            chat_sock.sendall(msg.encode())
        chat_sock.close()
        print("[已離開私聊]")
    except Exception as e:
        print(f"[錯誤] 無法建立私聊: {e}")

def server_messages(sock):  # 統一接收 server 指令
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[與 server 斷線]")
                break

            msg = data.decode().strip()

            if msg.startswith("START_CHAT"):
                _, peer_info = msg.split()
                peer_ip, peer_port = peer_info.split(":")
                peer_port = int(peer_port)

                print(f"[server] 對方已接受聊天，準備連線到 {peer_ip}:{peer_port}")
                time.sleep(0.5)  # 等對方 listener 建好
                start_private_chat(peer_ip, peer_port)
            elif "想和你聊天，要接受嗎？(y/n)" in msg:
                print(f"\n< [server]: {msg}")
                answer = input("(y/n): ").strip().lower()
                sock.sendall(answer.encode())  # 回覆 server
            else:
                print(f"\n< [server]: {msg}")
        except ConnectionError:
            break

def main():
    my_ip = input("請輸入自己的 IP: ").strip()
    my_port = int(input("請輸入自己的 Port: ").strip())
    my_name = input("請輸入自己的名稱: ").strip()

    # 與 server 建立連線
    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli_sock.bind((my_ip, my_port))
    cli_sock.connect(("127.0.0.1", 8888))
    print("[已連線至 server]")
    cli_sock.sendall(my_name.encode())

    # 啟動私聊 listener
    private_chat_listener(my_ip, my_port)

    # 啟動 server 訊息接收 thread
    threading.Thread(target=server_messages, args=(cli_sock,), daemon=True).start()

    try:
        while True:
            msg = input("> 請輸入指令 (list, chat <name>, exit): ").strip()
            if msg.lower() == "exit":
                print("[結束通訊]")
                break
            cli_sock.sendall(msg.encode())
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n[結束通訊]")
    finally:
        cli_sock.close()

if __name__ == "__main__":
    main()
