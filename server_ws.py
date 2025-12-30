import asyncio
import json
import logging
from typing import Optional, List, Dict, Tuple

import websockets

# Thiết lập logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Cấu hình WebSocket
HOST = "0.0.0.0"
PORT = 8765

# Các hằng số cho nước đi và bản dịch
VALID_MOVES: Tuple[str, ...] = ("ROCK", "PAPER", "SCISSORS")
MOVE_VN: Dict[str, str] = {"ROCK": "BÚA", "PAPER": "BAO", "SCISSORS": "KÉO"}
OUTCOME_VN: Dict[str, str] = {"WIN": "THẮNG", "LOSE": "THUA", "DRAW": "HÒA"}

# Hàng đợi người chơi đang đợi ghép (được bảo vệ bởi lock để tránh race condition)
waiting_players: List["Player"] = []
waiting_lock = asyncio.Lock()


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

    async def send(self, data: dict) -> bool:
        try:
            if is_ws_closed(self.ws):
                logger.warning("WebSocket closed for %s, cannot send: %s", getattr(self.ws, "remote_address", "?"), data)
                return False
            message = json.dumps(data)
            await self.ws.send(message)
            logger.info("Sent to %s: %s", getattr(self.ws, "remote_address", "?"), data.get("type", "unknown"))
            return True
        except Exception:
            logger.exception("Failed to send message to %s", getattr(self.ws, "remote_address", "?"))
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

    if p2 is None or is_ws_closed(p2.ws):
        logger.info("Opponent disconnected before result for %s", getattr(p1.ws, "remote_address", "?"))
        await p1.send({"type": "opponent_left", "message": "Đối thủ đã rời trận."})
        p1.reset_move()
        return

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
            "outcome_vn": OUTCOME_VN.get(result_p1, "HÒA"),
            "your_move_vn": MOVE_VN.get(p1.move, "?"),
            "opponent_move_vn": MOVE_VN.get(p2.move, "?"),
        }
    )
    await p2.send(
        {
            "type": "result",
            "outcome": result_p2,
            "your_move": p2.move,
            "opponent_move": p1.move,
            # Trường tiếng Việt để client hiển thị trực tiếp nếu hỗ trợ
            "outcome_vn": OUTCOME_VN.get(result_p2, "HÒA"),
            "your_move_vn": MOVE_VN.get(p2.move, "?"),
            "opponent_move_vn": MOVE_VN.get(p1.move, "?"),
        }
    )

    p1.reset_move()
    p2.reset_move()
    logger.info("[GAME END] %s vs %s -> P1: %s", getattr(p1.ws, "remote_address", "?"), getattr(p2.ws, "remote_address", "?"), result_p1)


async def cleanup_waiting():
    """Loại bỏ player đã đóng kết nối khỏi hàng đợi (thread-safe)."""
    global waiting_players
    async with waiting_lock:
        waiting_players = [p for p in waiting_players if not is_ws_closed(p.ws)]
    logger.debug("After cleanup, waiting count=%d", len(waiting_players))


async def match_making(new_player: Player):
    """Ghép cặp người chơi (an toàn với nhiều coroutine)."""
    try:
        await cleanup_waiting()
        logger.info("[MATCHMAKING] Số người đang đợi: %d", len(waiting_players))

        async with waiting_lock:
            if not waiting_players:
                waiting_players.append(new_player)
                logger.info("[MATCHMAKING] %s được thêm vào hàng đợi. Tổng: %d", getattr(new_player.ws, "remote_address", "?"), len(waiting_players))
                await new_player.send({"type": "system", "message": "Đang tìm đối thủ..."})
                logger.debug("Sent searching message to %s", getattr(new_player.ws, "remote_address", "?"))
                return

            opponent = waiting_players.pop(0)

        logger.info("[MATCHMAKING] Tìm thấy đối thủ: %s cho %s", getattr(opponent.ws, "remote_address", "?"), getattr(new_player.ws, "remote_address", "?"))

        new_player.opponent = opponent
        opponent.opponent = new_player

        start_msg = {"type": "start", "message": "Đã tìm thấy đối thủ! Hãy chọn Búa/ Bao/ Kéo."}

        logger.debug("[MATCHMAKING] Sending start to %s and %s", getattr(new_player.ws, "remote_address", "?"), getattr(opponent.ws, "remote_address", "?"))
        await new_player.send(start_msg)
        await opponent.send(start_msg)

        logger.info("[MATCHMAKING] ✓ Đã ghép cặp thành công: %s vs %s", getattr(new_player.ws, "remote_address", "?"), getattr(opponent.ws, "remote_address", "?"))
    except Exception:
        logger.exception("Lỗi trong match_making")


async def handle_move(player: Player, move: str):
    """Xử lý nước đi từ một người chơi."""
    if player.opponent is None or is_ws_closed(player.opponent.ws):
        await player.send({"type": "system", "message": "Chưa có đối thủ, vui lòng đợi ghép cặp."})
        return

    player.move = move
    logger.info("[%s] Chosen: %s", getattr(player.ws, "remote_address", "?"), move)

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
        async with waiting_lock:
            waiting_players = [p for p in waiting_players if p != player]

        if player.opponent:
            opponent = player.opponent
            player.opponent = None
            opponent.opponent = None
            opponent.reset_move()
            if not is_ws_closed(opponent.ws):
                await opponent.send({"type": "opponent_left", "message": "Đối thủ đã rời trận."})
    except Exception:
        logger.exception("Lỗi trong handle_disconnect")


async def handler(websocket: websockets.WebSocketServerProtocol):
    player = Player(websocket)
    logger.info("[CONNECT] %s connected.", getattr(websocket, "remote_address", "?"))

    try:
        await match_making(player)
    except Exception:
        logger.exception("Lỗi khi match_making cho %s", getattr(websocket, "remote_address", "?"))
        return

    try:
        async for raw_msg in websocket:
            try:
                data = json.loads(raw_msg)
            except Exception:
                logger.exception("Lỗi parse JSON từ %s", getattr(websocket, "remote_address", "?"))
                await player.send({"type": "system", "message": "Định dạng không hợp lệ."})
                continue

            msg_type = data.get("type")
            if msg_type == "move":
                move_val = data.get("value")
                if move_val not in VALID_MOVES:
                    await player.send({"type": "system", "message": "Nước đi không hợp lệ."})
                    continue
                try:
                    await handle_move(player, move_val)
                except Exception:
                    logger.exception("Lỗi khi xử lý move từ %s", getattr(websocket, "remote_address", "?"))
            elif msg_type == "quit":
                break
    except websockets.ConnectionClosed:
        logger.info("[CLOSED] %s connection closed.", getattr(websocket, "remote_address", "?"))
    except Exception:
        logger.exception("Lỗi trong handler cho %s", getattr(websocket, "remote_address", "?"))
    finally:
        try:
            await handle_disconnect(player)
        except Exception:
            logger.exception("Lỗi khi disconnect %s", getattr(websocket, "remote_address", "?"))
        logger.info("[DISCONNECT] %s disconnected.", getattr(websocket, "remote_address", "?"))


async def main():
    logger.info("[LISTENING] WebSocket server on ws://%s:%d", HOST, PORT)
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()  # Chạy vô hạn


if __name__ == "__main__":
    asyncio.run(main())

