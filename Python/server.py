import socket

HOST = '127.0.0.1'
PORT = 65432

print(f"Python Server dang lang nghe tai port {PORT}...")

# Tạo socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    
    # Chấp nhận kết nối từ Client
    conn, addr = s.accept()
    with conn:
        print(f"Da ket noi voi: {addr}")

        # --- TỐI ƯU HÓA TCP (Theo yêu cầu bài tập) ---
        # 1. Tắt Nagle (TCP_NODELAY)
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        # 2. Tăng Buffer nhận
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64 * 1024) # 64KB

        # Kiểm tra và in ra màn hình để chụp ảnh báo cáo
        nodelay_status = conn.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
        buff_size = conn.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)

        print(f">>> [SYSTEM] TCP_NODELAY: {'ENABLED (Python)' if nodelay_status else 'DISABLED'}")
        print(f">>> [SYSTEM] Buffer Size: {buff_size}")
        # ---------------------------------------------

        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            text_received = data.decode('utf-8')
            print(f"Nhan duoc tu Client: {text_received}")
            
            # Phản hồi lại cho Client
            response = f"Server Python da nhan: {text_received}"
            conn.sendall(response.encode('utf-8'))