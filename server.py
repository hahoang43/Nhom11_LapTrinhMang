import os
import socket
import threading
import queue
import logging
from typing import Optional, Tuple, Dict

# Thiết lập logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# --- Cấu hình Server ---
# Cho phép thay đổi HOST/PORT qua biến môi trường để dễ test/triển khai
# Ví dụ: trong PowerShell: $env:PORT = '2345'; python server.py
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '1234'))
waiting_queue = queue.Queue()

# Các hằng số
VALID_MOVES: Tuple[str, ...] = ("ROCK", "PAPER", "SCISSORS")
MOVE_VN: Dict[str, str] = {"ROCK": "BÚA", "PAPER": "BAO", "SCISSORS": "KÉO"}
OUTCOME_VN: Dict[str, str] = {"WIN": "THẮNG", "LOSE": "THUA", "DRAW": "HÒA"} 


# Helper: mapping sang tiếng Việt (dùng khi gửi thông báo)
def move_to_vn(move: str) -> str:
    return MOVE_VN.get(move, "?")


def outcome_to_vn(outcome: str) -> str:
    return OUTCOME_VN.get(outcome, "?")


class Player:
    def __init__(self, conn: socket.socket, addr: tuple):
        self.conn = conn
        self.addr = addr
        self.opponent: Optional['Player'] = None
        self.move: Optional[str] = None

    def send_msg(self, msg: str) -> bool:
        try:
            self.conn.sendall((msg + "\n").encode('utf-8'))
            return True
        except Exception:
            logger.exception("Lỗi gửi tin tới %s", self.addr)
            return False

    def reset_move(self) -> None:
        self.move = None

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            logger.exception("Error closing connection for %s", self.addr)

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

def evaluate_game(player: Player) -> None:
    """Hàm này được gọi khi cả 2 người đều đã có nước đi (self.move khác None)"""
    p1 = player
    p2 = player.opponent

    if p2 is None:
        logger.info("Opponent is None for %s, aborting evaluate", p1.addr)
        p1.reset_move()
        return

    if p2.conn._closed:  # type: ignore[attr-defined]
        logger.info("Opponent disconnected before evaluate for %s", p1.addr)
        p1.send_msg("OPPONENT_LEFT|VN:Đối thủ đã rời trận.")
        p1.reset_move()
        return

    # Tính kết quả từ góc nhìn của P1
    result_p1 = check_winner(p1.move, p2.move)
    result_p2 = 'DRAW' if result_p1 == 'DRAW' else ('LOSE' if result_p1 == 'WIN' else 'WIN')

    p1_vn_out = outcome_to_vn(result_p1)
    p2_vn_out = outcome_to_vn(result_p2)
    p1_move_vn = move_to_vn(p1.move)
    p2_move_vn = move_to_vn(p2.move)

    p1.send_msg(f"RESULT:{result_p1}|VN:{p1_vn_out}|YOU:{p1.move}|YOU_VN:{p1_move_vn}|OPP:{p2.move}|OPP_VN:{p2_move_vn}")
    p2.send_msg(f"RESULT:{result_p2}|VN:{p2_vn_out}|YOU:{p2.move}|YOU_VN:{p2_move_vn}|OPP:{p1.move}|OPP_VN:{p1_move_vn}")

    p1.reset_move()
    p2.reset_move()
    logger.info("[GAME END] %s vs %s -> P1: %s", p1.addr, p2.addr, result_p1)

# --- PHẦN XỬ LÝ KẾT NỐI (Đã sửa đổi bởi Người 2) ---
def handle_client(player: Player) -> None:
    conn = player.conn
    addr = player.addr
    logger.info("[NEW CONNECTION] %s connected.", addr)
    conn.settimeout(300)

    try:
        while True:
            # Nhận tin nhắn
            try:
                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode('utf-8').strip()
            except socket.timeout:
                logger.info("Connection timed out: %s", addr)
                break
            except ConnectionResetError:
                logger.info("Connection reset by peer: %s", addr)
                break
            except Exception:
                logger.exception("Error receiving data from %s", addr)
                break

            logger.info("[%s] Sent: %s", addr, msg)

            # --- LOGIC XỬ LÝ TIN NHẮN (PROTOCOL) ---

            if msg.startswith("MOVE:"): 
                        # Cắt chuỗi để lấy nước đi (ROCK, PAPER, hoặc SCISSORS)
                        move = msg.split(":", 1)[1]

                        if move not in VALID_MOVES:
                            player.send_msg("SYSTEM:Nước đi không hợp lệ.|VN:Nước đi không hợp lệ.")
                            continue

                        # Kiểm tra xem có đối thủ chưa
                        if player.opponent is None:
                            player.send_msg("SYSTEM:Chưa có đối thủ, không thể ra đòn.|VN:Chưa có đối thủ, vui lòng đợi.")
                            continue

                        player.move = move
                        logger.info("[%s] Đã chọn: %s", addr, move)

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
                logger.info("%s requested to quit.", addr)
                break

    except Exception:
        logger.exception("Unexpected error in client handler %s", addr)
    finally:
        # Xử lý khi ngắt kết nối
        try:
            if player.opponent:
                try:
                    player.opponent.send_msg("OPPONENT_LEFT|VN:Đối thủ đã rời trận.")  # Báo cho đối thủ biết
                except Exception:
                    logger.exception("Failed to notify opponent %s", player.opponent.addr)
                player.opponent.opponent = None  # Hủy ghép cặp
        finally:
            try:
                player.close()
            except Exception:
                logger.exception("Error closing connection for %s", addr)
            logger.info("[DISCONNECT] %s disconnected.", addr)

def match_making(new_player: Player) -> None:
    # Đặt vào hàng đợi hoặc ghép cặp nếu có người chờ
    if waiting_queue.empty():
        waiting_queue.put(new_player)
        new_player.send_msg("SYSTEM:Đang tìm đối thủ...|VN:Đang tìm đối thủ...")
        logger.info("Queued player %s", new_player.addr)
    else:
        opponent = waiting_queue.get()
        new_player.opponent = opponent
        opponent.opponent = new_player

        # Gửi thông báo bắt đầu (giữ mã hướng dẫn nhưng bổ sung nhãn VN)
        start_msg = "SYSTEM:Game Start! Hãy chọn MOVE:ROCK, MOVE:PAPER, hoặc MOVE:SCISSORS|VN:Đã tìm thấy đối thủ! Hãy chọn BÚA/BAO/KÉO"
        new_player.send_msg(start_msg)
        opponent.send_msg(start_msg)
        logger.info("Matched %s with %s", new_player.addr, opponent.addr)

def start_server() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    logger.info("[LISTENING] Server listening on %s:%s", HOST, PORT)

    try:
        while True:
            conn, addr = server.accept()
            new_player = Player(conn, addr)
            # Start a dedicated daemon thread to handle this client
            thread = threading.Thread(target=handle_client, args=(new_player,), daemon=True)
            thread.start()
            match_making(new_player)
    except KeyboardInterrupt:
        logger.info("Shutting down server")
    finally:
        try:
            server.close()
        except Exception:
            logger.exception("Error closing server socket")

if __name__ == "__main__":
    start_server()