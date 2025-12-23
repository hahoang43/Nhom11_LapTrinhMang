import socket
import threading

class GameClient:
    def __init__(self, host='127.0.0.1', port=1234, on_message_received=None):
        """
        :param host: Địa chỉ IP của Server (mặc định localhost)
        :param port: Cổng kết nối (phải trùng Server)
        :param on_message_received: Một hàm (callback) từ bên UI. 
               Khi nhận được tin nhắn từ Server, class này sẽ gọi hàm đó để UI cập nhật.
        """
        self.host = host
        self.port = port
        self.socket = None
        self.is_connected = False
        self.on_message_received = on_message_received 

    def connect_to_server(self):
        """Hàm kết nối đến Server và bắt đầu luồng lắng nghe"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            print(">>> Đã kết nối thành công đến Server!")

            # Bắt đầu một luồng (Thread) riêng để lắng nghe tin nhắn
            # Nếu không có luồng này, giao diện sẽ bị đơ khi đợi tin nhắn
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True # Tự tắt khi chương trình chính tắt
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Không thể kết nối Server: {e}")
            return False

    def receive_messages(self):
        """Vòng lặp vô tận để nghe Server nói gì"""
        while self.is_connected:
            try:
                # Đọc dữ liệu từ Server
                message = self.socket.recv(1024).decode('utf-8').strip()
                
                if not message:
                    print("Mất kết nối với Server.")
                    self.is_connected = False
                    break
                
                print(f"[SERVER]: {message}") # Log để debug
                
                # Nếu bên UI có đăng ký hàm xử lý, thì gọi hàm đó và truyền tin nhắn sang
                if self.on_message_received:
                    self.on_message_received(message)
                    
            except Exception as e:
                print(f"Lỗi khi nhận dữ liệu: {e}")
                self.is_connected = False
                break

    def send_move(self, move_type):
        """
        Gửi nước đi lên Server.
        move_type: 'ROCK', 'PAPER', hoặc 'SCISSORS'
        """
        if self.is_connected:
            protocol_msg = f"MOVE:{move_type}" # Tuân thủ giao thức của Người 2
            try:
                self.socket.sendall(protocol_msg.encode('utf-8'))
                print(f">>> Đã gửi: {protocol_msg}")
            except:
                print("Lỗi gửi tin nhắn.")

    def close(self):
        """Ngắt kết nối"""
        if self.socket:
            self.socket.sendall("QUIT".encode('utf-8'))
            self.socket.close()
        self.is_connected = False

# --- PHẦN CODE TEST (Chạy thử không cần giao diện) ---
# Người 3 có thể chạy file này độc lập để test với Server của Người 1, 2
if __name__ == "__main__":
    
    # Hàm giả lập UI để test
    def test_ui_callback(msg):
        print(f"==> UI NHẬN ĐƯỢC: {msg}")
        if "RESULT" in msg:
            print("!!! KẾT QUẢ ĐÃ VỀ !!!")

    # Tạo client
    client = GameClient(host='127.0.0.1', port=1234, on_message_received=test_ui_callback)
    
    if client.connect_to_server():
        while True:
            # Nhập lệnh từ bàn phím để test gửi đi
            cmd = input("Nhập r (Rock), p (Paper), s (Scissors) hoặc q (Quit): ")
            if cmd == 'r':
                client.send_move('ROCK')
            elif cmd == 'p':
                client.send_move('PAPER')
            elif cmd == 's':
                client.send_move('SCISSORS')
            elif cmd == 'q':
                client.close()
                break