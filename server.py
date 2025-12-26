import os
import socket
import threading
import queue

# --- Cấu hình Server ---
# Cho phép thay đổi HOST/PORT qua biến môi trường để dễ test/triển khai
# Ví dụ: trong PowerShell: $env:PORT = '2345'; python server.py
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '1234'))
waiting_queue = queue.Queue()


# Helper: mapping sang tiếng Việt (dùng khi gửi thông báo)
def move_to_vn(move: str) -> str:
    return "BÚA" if move == 'ROCK' else "BAO" if move == 'PAPER' else "KÉO"


def outcome_to_vn(outcome: str) -> str:
    return "THẮNG" if outcome == 'WIN' else "THUA" if outcome == 'LOSE' else "HÒA"
# waiting_queue defined above

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

    # Gửi kết quả về cho cả 2 (gồm mã cũ + nhãn tiếng Việt và tên nước đi VN)
    p1_vn_out = outcome_to_vn(result_p1)
    p2_vn_out = outcome_to_vn(result_p2)
    p1_move_vn = move_to_vn(p1.move)
    p2_move_vn = move_to_vn(p2.move)

    p1.send_msg(f"RESULT:{result_p1}|VN:{p1_vn_out}|YOU:{p1.move}|YOU_VN:{p1_move_vn}|OPP:{p2.move}|OPP_VN:{p2_move_vn}")
    p2.send_msg(f"RESULT:{result_p2}|VN:{p2_vn_out}|YOU:{p2.move}|YOU_VN:{p2_move_vn}|OPP:{p1.move}|OPP_VN:{p1_move_vn}")

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
                            player.send_msg("SYSTEM:Chưa có đối thủ, không thể ra đòn.|VN:Chưa có đối thủ, vui lòng đợi.")
                            continue

                        player.move = move
                        print(f"[{addr}] Đã chọn: {move}")

                        # Kiểm tra xem đối thủ đã đi chưa
                        if player.opponent.move is None:
                            # Đối thủ chưa đi -> Bảo người này đợi (gửi cả nhãn VN)
                            player.send_msg(f"WAIT|VN:Đang chờ đối thủ chọn.")
                            player.opponent.send_msg("SYSTEM:Đối thủ đã ra đòn, đến lượt bạn!|VN:Đối thủ đã chọn, đến lượt bạn!")
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
            # Gửi cả mã và nhãn VN cho client TCP
            player.opponent.send_msg("OPPONENT_LEFT|VN:Đối thủ đã rời trận.") # Báo cho đối thủ biết
            player.opponent.opponent = None # Hủy ghép cặp
        conn.close()
        print(f"[DISCONNECT] {addr} disconnected.")

def match_making(new_player):
    # (Giữ nguyên logic của Người 1)
    if waiting_queue.empty():
        waiting_queue.put(new_player)
        new_player.send_msg("SYSTEM:Đang tìm đối thủ...|VN:Đang tìm đối thủ...")
        threading.Thread(target=handle_client, args=(new_player,)).start()
    else:
        opponent = waiting_queue.get()
        new_player.opponent = opponent
        opponent.opponent = new_player
        
        # Gửi thông báo bắt đầu (giữ mã hướng dẫn nhưng bổ sung nhãn VN)
        start_msg = "SYSTEM:Game Start! Hãy chọn MOVE:ROCK, MOVE:PAPER, hoặc MOVE:SCISSORS|VN:Đã tìm thấy đối thủ! Hãy chọn BÚA/BAO/KÉO"
        new_player.send_msg(start_msg)
        opponent.send_msg(start_msg)
        
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