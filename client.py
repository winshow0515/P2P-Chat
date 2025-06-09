import socket
import threading

def receive_messages(sock):
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            print(f"\n< 對方回覆: {data.decode()}\n> 請輸入訊息: ", end="")
        except:
            break

def main():
    # 使用者輸入自己的 IP 與 Port
    my_ip_port = input("請輸入你要掛的 ip:port: ").strip().split()
    my_ip = my_ip_port[0]
    my_port = int(my_ip_port[1])

    # 使用者輸入對方的 IP 與 Port
    peer_ip_port = input("請輸入對方的 ip:port: ").strip().split()
    peer_ip = peer_ip_port[0]
    peer_port = int(peer_ip_port[1])

    # 建立 UDP socket 並綁定自己的 IP:port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((my_ip, my_port))

    # 啟動接收訊息的執行緒
    recv_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    recv_thread.start()

    # 傳送訊息的迴圈
    while True:
        try:
            message = input("> 請輸入訊息: ")
            sock.sendto(message.encode(), (peer_ip, peer_port))
        except KeyboardInterrupt:
            print("\n[結束通訊]")
            break

    sock.close()

if __name__ == "__main__":
    main()
