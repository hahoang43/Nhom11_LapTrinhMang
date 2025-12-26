import asyncio
import json
from typing import Optional

import websockets

# Cấu hình WebSocket
HOST = "0.0.0.0"
PORT = 8765

# Hàng đợi người chơi đang đợi ghép
waiting_players = []


def is_ws_closed(ws) -> bool:
    """
    Kiểm tra trạng thái websocket, an toàn với phiên bản websockets 15 (ServerConnection không có thuộc tính 'closed').
    """
    return bool(getattr(ws, "closed", False))


class Player:
    def __init__(self, websocket: websockets.WebSocketServerProtocol):
        self.ws = websocket
        self.opponent: Optional["Player"] = None
        self.move: Optional[str] = None

    async def send(self, data: dict):
        try:
            if is_ws_closed(self.ws):
                print(f"[WARNING] WebSocket đã đóng cho {getattr(self.ws, 'remote_address', '?')}, không thể gửi: {data}")
                return False
            message = json.dumps(data)
            await self.ws.send(message)
            print(f"[SEND] Đã gửi đến {self.ws.remote_address}: {data.get('type', 'unknown')}")
            return True
        except Exception as e:
            print(f"[ERROR] Không thể gửi message đến {self.ws.remote_address}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def reset_move(self):
        self.move = None


def check_winner(move_p1: str, move_p2: str) -> str:
    """Trả về 'WIN' (p1 thắng), 'LOSE', hoặc 'DRAW'."""
    if move_p1 == move_p2:
        return "DRAW"

    if (move_p1 == "ROCK" and move_p2 == "SCISSORS") or \
       (move_p1 == "SCISSORS" and move_p2 == "PAPER") or \
       (move_p1 == "PAPER" and move_p2 == "ROCK"):
        return "WIN"
    return "LOSE"


async def evaluate_game(player: Player):
    """Khi cả hai đã ra đòn, tính kết quả và gửi cho từng bên."""
    p1 = player
    p2 = player.opponent

    result_p1 = check_winner(p1.move, p2.move)
    result_p2 = "DRAW"
    if result_p1 == "WIN":
        result_p2 = "LOSE"
    elif result_p1 == "LOSE":
        result_p2 = "WIN"

    await p1.send(
        {
            "type": "result",
            "outcome": result_p1,
            "your_move": p1.move,
            "opponent_move": p2.move,
            # Trường tiếng Việt để client hiển thị trực tiếp nếu hỗ trợ
            "outcome_vn": ("THẮNG" if result_p1 == "WIN" else "THUA" if result_p1 == "LOSE" else "HÒA"),
            "your_move_vn": ("BÚA" if p1.move == "ROCK" else "BAO" if p1.move == "PAPER" else "KÉO"),
            "opponent_move_vn": ("BÚA" if p2.move == "ROCK" else "BAO" if p2.move == "PAPER" else "KÉO"),
        }
    )
    await p2.send(
        {
            "type": "result",
            "outcome": result_p2,
            "your_move": p2.move,
            "opponent_move": p1.move,
            # Trường tiếng Việt để client hiển thị trực tiếp nếu hỗ trợ
            "outcome_vn": ("THẮNG" if result_p2 == "WIN" else "THUA" if result_p2 == "LOSE" else "HÒA"),
            "your_move_vn": ("BÚA" if p2.move == "ROCK" else "BAO" if p2.move == "PAPER" else "KÉO"),
            "opponent_move_vn": ("BÚA" if p1.move == "ROCK" else "BAO" if p1.move == "PAPER" else "KÉO"),
        }
    )

    p1.reset_move()
    p2.reset_move()
    print(f"[GAME END] {p1.ws.remote_address} vs {p2.ws.remote_address} -> P1: {result_p1}")


async def cleanup_waiting():
    """Loại bỏ player đã đóng kết nối khỏi hàng đợi."""
    global waiting_players
    waiting_players = [p for p in waiting_players if not is_ws_closed(p.ws)]


async def match_making(new_player: Player):
    """Ghép cặp người chơi."""
    try:
        await cleanup_waiting()
        print(f"[MATCHMAKING] Số người đang đợi: {len(waiting_players)}")
        
        if not waiting_players:
            waiting_players.append(new_player)
            print(f"[MATCHMAKING] {new_player.ws.remote_address} được thêm vào hàng đợi. Tổng: {len(waiting_players)}")
            await new_player.send({"type": "system", "message": "Đang tìm đối thủ..."})
            print(f"[MATCHMAKING] Đã gửi 'Đang tìm đối thủ' đến {new_player.ws.remote_address}")
            return

        opponent = waiting_players.pop(0)
        print(f"[MATCHMAKING] Tìm thấy đối thủ: {opponent.ws.remote_address} cho {new_player.ws.remote_address}")
        
        new_player.opponent = opponent
        opponent.opponent = new_player

        start_msg = {"type": "start", "message": "Đã tìm thấy đối thủ! Hãy chọn Búa/ Bao/ Kéo."}
        
        print(f"[MATCHMAKING] Đang gửi start message đến {new_player.ws.remote_address}...")
        await new_player.send(start_msg)
        print(f"[MATCHMAKING] Đã gửi start message đến {new_player.ws.remote_address}")
        
        print(f"[MATCHMAKING] Đang gửi start message đến {opponent.ws.remote_address}...")
        await opponent.send(start_msg)
        print(f"[MATCHMAKING] Đã gửi start message đến {opponent.ws.remote_address}")
        
        print(f"[MATCHMAKING] ✓ Đã ghép cặp thành công: {new_player.ws.remote_address} vs {opponent.ws.remote_address}")
    except Exception as e:
        print(f"[ERROR] Lỗi trong match_making: {e}")
        import traceback
        traceback.print_exc()


async def handle_move(player: Player, move: str):
    """Xử lý nước đi từ một người chơi."""
    if player.opponent is None:
        await player.send({"type": "system", "message": "Chưa có đối thủ, vui lòng đợi ghép cặp."})
        return

    player.move = move
    print(f"[{player.ws.remote_address}] Đã chọn: {move}")

    if player.opponent.move is None:
        # Đối thủ chưa đánh
        await player.send({"type": "wait", "message": "Đối thủ chưa chọn xong. Vui lòng đợi!"})
        await player.opponent.send({"type": "opponent_moved", "message": "Đối thủ đã chọn, đến lượt bạn!"})
    else:
        # Cả hai đã có nước đi
        await evaluate_game(player)


async def handle_disconnect(player: Player):
    """Khi một người rời đi, thông báo cho đối thủ và dọn hàng đợi."""
    try:
        await cleanup_waiting()
        # Loại bỏ player khỏi hàng đợi nếu có
        global waiting_players
        waiting_players = [p for p in waiting_players if p != player]
        
        if player.opponent:
            opponent = player.opponent
            player.opponent = None
            opponent.opponent = None
            opponent.reset_move()
            if not opponent.ws.closed:
                await opponent.send({"type": "opponent_left", "message": "Đối thủ đã rời trận."})
    except Exception as e:
        print(f"[ERROR] Lỗi trong handle_disconnect: {e}")
        import traceback
        traceback.print_exc()


async def handler(websocket: websockets.WebSocketServerProtocol):
    player = Player(websocket)
    print(f"[CONNECT] {websocket.remote_address} đã kết nối.")
    
    try:
        await match_making(player)
    except Exception as e:
        print(f"[ERROR] Lỗi khi match_making cho {websocket.remote_address}: {e}")
        import traceback
        traceback.print_exc()
        return

    try:
        async for raw_msg in websocket:
            try:
                data = json.loads(raw_msg)
            except Exception as e:
                print(f"[ERROR] Lỗi parse JSON từ {websocket.remote_address}: {e}")
                await player.send({"type": "system", "message": "Định dạng không hợp lệ."})
                continue

            msg_type = data.get("type")
            if msg_type == "move":
                move_val = data.get("value")
                if move_val not in ("ROCK", "PAPER", "SCISSORS"):
                    await player.send({"type": "system", "message": "Nước đi không hợp lệ."})
                    continue
                try:
                    await handle_move(player, move_val)
                except Exception as e:
                    print(f"[ERROR] Lỗi khi xử lý move từ {websocket.remote_address}: {e}")
                    import traceback
                    traceback.print_exc()
            elif msg_type == "quit":
                break
    except websockets.ConnectionClosed:
        print(f"[CLOSED] {websocket.remote_address} đóng kết nối.")
    except Exception as e:
        print(f"[ERROR] Lỗi trong handler cho {websocket.remote_address}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await handle_disconnect(player)
        except Exception as e:
            print(f"[ERROR] Lỗi khi disconnect {websocket.remote_address}: {e}")
        print(f"[DISCONNECT] {websocket.remote_address} disconnected.")


async def main():
    print(f"[LISTENING] WebSocket server on ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()  # Chạy vô hạn


if __name__ == "__main__":
    asyncio.run(main())

