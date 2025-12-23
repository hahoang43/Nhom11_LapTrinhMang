import socket
import threading
import queue

# --- Cấu hình Server ---
HOST = '0.0.0.0'
PORT = 1234
waiting_queue = queue.Queue()

class Player:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.opponent = None
        self.move = None  # Cập nhật của Người 2: Lưu nước đi (ROCK/PAPER/SCISSORS)

    def send_msg(self, msg):
        try:
            self.conn.sendall((msg + "\n").encode('utf-8'))
        except:
            print(f"Lỗi gửi tin tới {self.addr}")

    def reset_move(self):
        self.move = None

# --- LOGIC CỦA NGƯỜI 2: XỬ LÝ THẮNG THUA ---
def check_winner(move_p1, move_p2):
    """
    Trả về kết quả cho P1: 'WIN', 'LOSE', hoặc 'DRAW'
    """
    if move_p1 == move_p2:
        return 'DRAW'
    
    if (move_p1 == 'ROCK' and move_p2 == 'SCISSORS') or \
       (move_p1 == 'SCISSORS' and move_p2 == 'PAPER') or \
       (move_p1 == 'PAPER' and move_p2 == 'ROCK'):
        return 'WIN'
    
    return 'LOSE'

def evaluate_game(player):
    """
    Hàm này được gọi khi cả 2 người đều đã có nước đi (self.move khác None)
    """
    p1 = player
    p2 = player.opponent

    # Tính kết quả từ góc nhìn của P1
    result_p1 = check_winner(p1.move, p2.move)
    
    # Tính kết quả từ góc nhìn của P2 (ngược lại của P1)
    if result_p1 == 'WIN':
        result_p2 = 'LOSE'
    elif result_p1 == 'LOSE':
        result_p2 = 'WIN'
    else:
        result_p2 = 'DRAW'

    # Gửi kết quả về cho cả 2
    p1.send_msg(f"RESULT:{result_p1}")  # Ví dụ: RESULT:WIN
    p2.send_msg(f"RESULT:{result_p2}")  # Ví dụ: RESULT:LOSE

    # Reset nước đi để chuẩn bị ván mới
    p1.reset_move()
    p2.reset_move()
    print(f"[GAME END] {p1.addr} vs {p2.addr} -> P1: {result_p1}")

# --- PHẦN XỬ LÝ KẾT NỐI (Đã sửa đổi bởi Người 2) ---
def handle_client(player):
    conn = player.conn
    addr = player.addr
    print(f"[NEW CONNECTION] {addr} connected.")

    try:
        connected = True
        while connected:
            # Nhận tin nhắn
            msg = conn.recv(1024).decode('utf-8').strip()
            if not msg:
                break

            print(f"[{addr}] Sent: {msg}")

            # --- LOGIC XỬ LÝ TIN NHẮN (PROTOCOL) ---
            
            # 1. Nếu client gửi nước đi (Ví dụ: MOVE:ROCK)
            if msg.startswith("MOVE:"):
                # Cắt chuỗi để lấy nước đi (ROCK, PAPER, hoặc SCISSORS)
                move = msg.split(":")[1] 
                
                # Kiểm tra xem có đối thủ chưa
                if player.opponent is None:
                    player.send_msg("SYSTEM:Chưa có đối thủ, không thể ra đòn.")
                    continue

                player.move = move
                print(f"[{addr}] Đã chọn: {move}")

                # Kiểm tra xem đối thủ đã đi chưa
                if player.opponent.move is None:
                    # Đối thủ chưa đi -> Bảo người này đợi
                    player.send_msg("WAIT") 
                    player.opponent.send_msg("SYSTEM:Đối thủ đã ra đòn, đến lượt bạn!")
                else:
                    # Đối thủ đã đi rồi -> Tính thắng thua ngay lập tức
                    evaluate_game(player)

            # 2. Xử lý thoát game
            elif msg == "QUIT":
                connected = False

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Xử lý khi ngắt kết nối
        if player.opponent:
            player.opponent.send_msg("OPPONENT_LEFT") # Báo cho đối thủ biết
            player.opponent.opponent = None # Hủy ghép cặp
        conn.close()
        print(f"[DISCONNECT] {addr} disconnected.")

def match_making(new_player):
    # (Giữ nguyên logic của Người 1)
    if waiting_queue.empty():
        waiting_queue.put(new_player)
        new_player.send_msg("SYSTEM:Đang tìm đối thủ...")
        threading.Thread(target=handle_client, args=(new_player,)).start()
    else:
        opponent = waiting_queue.get()
        new_player.opponent = opponent
        opponent.opponent = new_player
        
        new_player.send_msg("SYSTEM:Game Start! Hãy chọn MOVE:ROCK, MOVE:PAPER, hoặc MOVE:SCISSORS")
        opponent.send_msg("SYSTEM:Game Start! Hãy chọn MOVE:ROCK, MOVE:PAPER, hoặc MOVE:SCISSORS")
        
        threading.Thread(target=handle_client, args=(new_player,)).start()

def start_server():
    # (Giữ nguyên logic của Người 1)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        new_player = Player(conn, addr)
        match_making(new_player)

if __name__ == "__main__":
    start_server()