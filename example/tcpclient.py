import socket
import threading

# ------------------ 共用：接收執行緒 ------------------ #
def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:          # 對方關閉
                print("\n[連線已斷開]")
                break
            print(f"\n< 對方回覆: {data.decode()}\n> 請輸入訊息: ", end="")
        except ConnectionError:
            break

# ------------------ 主程式 ------------------ #
def main():
    role = input("請選擇角色 (server/client) [s/c]: ").strip().lower()
    is_server = role in ("s", "server")


    if is_server:
        # 自己要綁定或連線的 IP:Port
        my_ip, my_port = input("請輸入自己的 ip:port: ").strip().split(":")
        my_port = int(my_port)
        # ---------- Server 角色 ----------
        srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket
        srv_sock.bind((my_ip, my_port))
        srv_sock.listen(1)      #啟動監聽，最多允許一個連線（你也可以改成 listen(5)）
        print(f"[等待連線] {my_ip}:{my_port} ...")
        conn, addr = srv_sock.accept()
        print(f"[已連線] 對方位址: {addr}")

        # 啟動接收執行緒
        threading.Thread(target=receive_messages, args=(conn,), daemon=True).start()

        # 傳送訊息
        try:
            while True:
                msg = input("> 請輸入訊息: ")
                conn.sendall(msg.encode())
        except KeyboardInterrupt:
            print("\n[結束通訊]")
        finally:
            conn.close()
            srv_sock.close()

    else:
        # ---------- Client 角色 ----------
        peer_ip, peer_port = input("請輸入對方 (Server) 的 ip:port: ").strip().split(":")
        peer_port = int(peer_port)

        cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli_sock.connect((peer_ip, peer_port))
        print(f"[已連線] 對方位址: {peer_ip}:{peer_port}")

        # 啟動接收執行緒
        threading.Thread(target=receive_messages, args=(cli_sock,), daemon=True).start()

        # 傳送訊息
        try:
            while True:
                msg = input("> 請輸入訊息: ")
                cli_sock.sendall(msg.encode())
        except KeyboardInterrupt:
            print("\n[結束通訊]")
        finally:
            cli_sock.close()

if __name__ == "__main__":
    main()