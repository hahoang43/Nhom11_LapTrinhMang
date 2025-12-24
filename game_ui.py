import tkinter as tk
from tkinter import messagebox

from client import GameClient


class RockPaperScissorsUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Kéo Búa Bao Online (WebSocket)")
        self.root.geometry("420x360")

        # Khởi tạo Client WebSocket
        self.client = GameClient(on_message_received=self.handle_server_message)

        # --- THIẾT KẾ GIAO DIỆN ---
        self.lbl_status = tk.Label(
            root,
            text="Chào mừng! Hãy kết nối Server",
            font=("Arial", 12, "bold"),
            fg="blue",
            wraplength=400,
        )
        self.lbl_status.pack(pady=20)

        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack(pady=20)

        self.btn_rock = tk.Button(
            self.frame_buttons,
            text="✊ BÚA",
            font=("Arial", 14),
            width=8,
            command=lambda: self.send_choice("ROCK"),
        )
        self.btn_rock.grid(row=0, column=0, padx=5)

        self.btn_paper = tk.Button(
            self.frame_buttons,
            text="✋ BAO",
            font=("Arial", 14),
            width=8,
            command=lambda: self.send_choice("PAPER"),
        )
        self.btn_paper.grid(row=0, column=1, padx=5)

        self.btn_scissors = tk.Button(
            self.frame_buttons,
            text="✌ KÉO",
            font=("Arial", 14),
            width=8,
            command=lambda: self.send_choice("SCISSORS"),
        )
        self.btn_scissors.grid(row=0, column=2, padx=5)

        self.toggle_buttons(False)

        self.btn_connect = tk.Button(
            root,
            text="Kết nối tới Server",
            bg="green",
            fg="white",
            command=self.connect_server,
        )
        self.btn_connect.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def connect_server(self):
        """Gọi hàm kết nối của client WebSocket."""
        if self.client.connect_to_server():
            self.lbl_status.config(text="Đang tìm đối thủ...", fg="orange")
            self.btn_connect.config(state="disabled", text="Đã kết nối")
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối tới Server. Kiểm tra lại IP/Port.")

    def toggle_buttons(self, state: bool):
        """Bật/Tắt nút bấm (state=True là bật)."""
        val = "normal" if state else "disabled"
        self.btn_rock.config(state=val)
        self.btn_paper.config(state=val)
        self.btn_scissors.config(state=val)

    def send_choice(self, move: str):
        """Gửi nước đi và khóa nút để tránh spam."""
        self.client.send_move(move)
        self.lbl_status.config(text=f"Bạn đã chọn {move}. Đang đợi kết quả...", fg="black")
        self.toggle_buttons(False)

    def handle_server_message(self, msg):
        """
        Callback nhận dữ liệu JSON từ server WebSocket.
        msg: dict có key 'type' và các trường liên quan.
        """
        if not isinstance(msg, dict):
            return

        msg_type = msg.get("type")
        if msg_type in ("system", "start"):
            text = msg.get("message", "Thông báo từ server.")
            color = "blue" if msg_type == "system" else "green"
            self.lbl_status.config(text=text, fg=color)
            if msg_type == "start":
                self.toggle_buttons(True)

        elif msg_type == "wait":
            self.lbl_status.config(text=msg.get("message", "Đang đợi đối thủ..."), fg="orange")

        elif msg_type == "opponent_moved":
            self.lbl_status.config(text=msg.get("message", "Đối thủ đã chọn, đến lượt bạn!"), fg="red")
            self.toggle_buttons(True)

        elif msg_type == "result":
            outcome = msg.get("outcome", "DRAW")
            if outcome == "WIN":
                display_text = "🎉 BẠN ĐÃ THẮNG!"
                color = "green"
            elif outcome == "LOSE":
                display_text = "💀 BẠN ĐÃ THUA!"
                color = "red"
            else:
                display_text = "⚖️ HÒA!"
                color = "gray"

            self.lbl_status.config(text=display_text, fg=color)
            messagebox.showinfo(
                "Kết quả",
                f"{display_text}\nBạn: {msg.get('your_move')}, Đối thủ: {msg.get('opponent_move')}",
            )
            self.toggle_buttons(True)

        elif msg_type == "opponent_left":
            messagebox.showwarning("Thông báo", "Đối thủ đã thoát game!")
            self.lbl_status.config(text="Đang tìm đối thủ mới...", fg="orange")
            self.toggle_buttons(False)

    def on_close(self):
        """Khi tắt cửa sổ thì ngắt kết nối luôn."""
        self.client.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RockPaperScissorsUI(root)
    root.mainloop()