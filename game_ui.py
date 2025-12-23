import tkinter as tk
from tkinter import messagebox
from client import GameClient # Import code của Người 3

class RockPaperScissorsUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Kéo Búa Bao Online")
        self.root.geometry("400x350")
        
        # Khởi tạo Client (kết nối với code Người 3)
        # Truyền hàm self.handle_server_message để xử lý khi có tin nhắn tới
        self.client = GameClient(on_message_received=self.handle_server_message)
        
        # --- THIẾT KẾ GIAO DIỆN ---
        
        # 1. Tiêu đề trạng thái
        self.lbl_status = tk.Label(root, text="Chào mừng! Hãy kết nối Server", 
                                   font=("Arial", 12, "bold"), fg="blue", wraplength=380)
        self.lbl_status.pack(pady=20)

        # 2. Khung chứa các nút chơi game
        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack(pady=20)

        # Nút Kéo - Búa - Bao (Dùng Emoji cho đẹp)
        self.btn_rock = tk.Button(self.frame_buttons, text="✊ BÚA", font=("Arial", 14), 
                                  width=8, command=lambda: self.send_choice("ROCK"))
        self.btn_rock.grid(row=0, column=0, padx=5)

        self.btn_paper = tk.Button(self.frame_buttons, text="✋ BAO", font=("Arial", 14), 
                                   width=8, command=lambda: self.send_choice("PAPER"))
        self.btn_paper.grid(row=0, column=1, padx=5)

        self.btn_scissors = tk.Button(self.frame_buttons, text="✌ KÉO", font=("Arial", 14), 
                                      width=8, command=lambda: self.send_choice("SCISSORS"))
        self.btn_scissors.grid(row=0, column=2, padx=5)

        # Ban đầu khóa các nút lại (chưa kết nối chưa được chơi)
        self.toggle_buttons(False)

        # 3. Nút Kết nối Server
        self.btn_connect = tk.Button(root, text="Kết nối tới Server", bg="green", fg="white",
                                     command=self.connect_server)
        self.btn_connect.pack(pady=10)

        # Xử lý khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def connect_server(self):
        """Gọi hàm kết nối của Người 3"""
        if self.client.connect_to_server():
            self.lbl_status.config(text="Đang tìm đối thủ...", fg="orange")
            self.btn_connect.config(state="disabled", text="Đã kết nối")
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối tới Server. Kiểm tra lại IP/Port.")

    def toggle_buttons(self, state):
        """Hàm tiện ích để Bật/Tắt nút bấm (state=True là bật)"""
        val = "normal" if state else "disabled"
        self.btn_rock.config(state=val)
        self.btn_paper.config(state=val)
        self.btn_scissors.config(state=val)

    def send_choice(self, move):
        """Gửi nước đi và khóa nút để tránh spam"""
        self.client.send_move(move)
        self.lbl_status.config(text=f"Bạn đã chọn {move}. Đang đợi kết quả...", fg="black")
        self.toggle_buttons(False) # Khóa nút, chờ kết quả ván này

    def handle_server_message(self, msg):
        """
        Hàm callback quan trọng: Xử lý tin nhắn từ Server gửi về.
        Đây là nơi 'Bộ não' của Client hoạt động.
        """
        print(f"UI nhận được: {msg}") # Debug log

        # 1. Xử lý thông báo hệ thống
        if msg.startswith("SYSTEM:"):
            txt = msg.split(":", 1)[1]
            self.lbl_status.config(text=txt, fg="blue")
            # Nếu tìm thấy đối thủ hoặc game start -> Mở khóa nút
            if "Game Start" in txt:
                self.toggle_buttons(True)

        # 2. Xử lý lệnh WAIT (Đối thủ chưa đánh)
        elif msg == "WAIT":
            self.lbl_status.config(text="Đối thủ chưa chọn xong. Vui lòng đợi!", fg="orange")
        
        # 3. Xử lý thông báo đối thủ đã đánh (Người 2 gửi)
        elif msg == "OPPONENT_SAID:SYSTEM:Đối thủ đã ra đòn, đến lượt bạn!":
             self.lbl_status.config(text="Đối thủ đã chọn rồi! Đến lượt bạn.", fg="red")

        # 4. Xử lý Kết quả (RESULT:WIN/LOSE/DRAW)
        elif msg.startswith("RESULT:"):
            result = msg.split(":")[1]
            if result == "WIN":
                display_text = "🎉 BẠN ĐÃ THẮNG!"
                color = "green"
            elif result == "LOSE":
                display_text = "💀 BẠN ĐÃ THUA!"
                color = "red"
            else:
                display_text = "⚖️ HÒA!"
                color = "gray"
            
            # Cập nhật giao diện
            self.lbl_status.config(text=display_text, fg=color)
            messagebox.showinfo("Kết quả", display_text)
            
            # Mở lại nút để chơi ván mới
            self.toggle_buttons(True)

        # 5. Xử lý đối thủ thoát
        elif msg == "OPPONENT_LEFT":
            messagebox.showwarning("Thông báo", "Đối thủ đã thoát game!")
            self.lbl_status.config(text="Đang tìm đối thủ mới...", fg="orange")
            self.toggle_buttons(False)

    def on_close(self):
        """Khi tắt cửa sổ thì ngắt kết nối luôn"""
        self.client.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RockPaperScissorsUI(root)
    root.mainloop()