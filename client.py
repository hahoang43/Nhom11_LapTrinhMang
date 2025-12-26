import os
import json
import threading
from typing import Callable, Optional

import websocket  # Yêu cầu thư viện websocket-client


class GameClient:
    """
    Client WebSocket để kết nối tới server (server_ws.py).
    Giao diện (Tkinter hoặc web) có thể truyền callback để nhận dữ liệu.
    """

    def __init__(self, host: str | None = None, port: int | None = None, on_message_received: Optional[Callable] = None):
        # Nếu không truyền host/port, đọc từ biến môi trường HOST/PORT
        self.host = host or os.getenv('HOST', '127.0.0.1')
        self.port = int(port or os.getenv('PORT', '8765'))
        self.ws_app: Optional[websocket.WebSocketApp] = None
        self.listen_thread: Optional[threading.Thread] = None
        self.is_connected = False
        self.connected_event = threading.Event()
        self.on_message_received = on_message_received

    # ------------------------------------------------------------------ #
    # Kết nối / Ngắt kết nối
    # ------------------------------------------------------------------ #
    def connect_to_server(self) -> bool:
        """Kết nối tới server WebSocket và khởi động luồng lắng nghe."""
        url = f"ws://{self.host}:{self.port}"
        self.connected_event.clear()

        self.ws_app = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        self.listen_thread = threading.Thread(target=self.ws_app.run_forever, daemon=True)
        self.listen_thread.start()

        # Đợi tối đa 3 giây xem có mở kết nối thành công không
        connected = self.connected_event.wait(timeout=3)
        if not connected:
            print("Không thể kết nối server WebSocket.")
            return False

        self.is_connected = True
        print(">>> Đã kết nối WebSocket!")
        return True

    def close(self):
        """Ngắt kết nối."""
        if self.ws_app and self.is_connected:
            try:
                self.ws_app.send(json.dumps({"type": "quit"}))
            except Exception:
                pass
            self.ws_app.close()
        self.is_connected = False

    # ------------------------------------------------------------------ #
    # WebSocket callbacks
    # ------------------------------------------------------------------ #
    def _on_open(self, ws):
        self.connected_event.set()

    def _on_close(self, ws, close_status_code, close_msg):
        self.is_connected = False
        print(f"[WS] Đóng kết nối: {close_status_code} {close_msg}")

    def _on_error(self, ws, error):
        print(f"[WS] Lỗi: {error}")

    def _on_message(self, ws, message: str):
        """Nhận message từ server, parse JSON và đẩy cho UI callback."""
        try:
            data = json.loads(message)
        except Exception:
            print(f"[WS] Không parse được message: {message}")
            return

        if self.on_message_received:
            self.on_message_received(data)

    # ------------------------------------------------------------------ #
    # API gửi lệnh
    # ------------------------------------------------------------------ #
    def send_move(self, move_type: str):
        """Gửi nước đi (ROCK/PAPER/SCISSORS)."""
        if not self.is_connected or not self.ws_app:
            print("Chưa kết nối server.")
            return
        try:
            payload = {"type": "move", "value": move_type}
            self.ws_app.send(json.dumps(payload))
            print(f">>> Đã gửi: {payload}")
        except Exception as exc:
            print(f"Lỗi gửi tin: {exc}")


# --- PHẦN CODE TEST (CLI) ---
if __name__ == "__main__":
    def test_ui_callback(msg):
        print(f"==> UI nhận: {msg}")

    # Tạo client; có thể đặt biến môi trường HOST/PORT trước khi chạy.
    # Ví dụ PowerShell: $env:HOST='127.0.0.1'; $env:PORT='8765'; python client.py
    client = GameClient(on_message_received=test_ui_callback)

    if client.connect_to_server():
        while True:
            cmd = input("Nhập r (Búa), p (Bao), s (Kéo) hoặc q (Thoát): ").strip().lower()
            if cmd == "r":
                client.send_move("ROCK")
            elif cmd == "p":
                client.send_move("PAPER")
            elif cmd == "s":
                client.send_move("SCISSORS")
            elif cmd == "q":
                client.close()
                break