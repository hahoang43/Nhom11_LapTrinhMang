import socket
import time

HOST = '127.0.0.1'
PORT = 65432

# Danh sách lệnh giả lập
commands = ["Shoot", "Move_Left", "Jump", "Reload"]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        
        # --- TỐI ƯU HÓA TCP ---
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # ----------------------

        for cmd in commands:
            # 1. Gửi lệnh đi
            print(f"Dang gui: {cmd}")
            s.sendall(cmd.encode('utf-8'))

            # 2. Nhận phản hồi
            data = s.recv(1024)
            print(f"Server phan hoi: {data.decode('utf-8')}")
            
            # Nghỉ 1 giây để dễ quan sát (Giống thao tác người thật)
            time.sleep(1)
            
    except ConnectionRefusedError:
        print("Loi: Khong tim thay Server! Hay chay server.py truoc.")