import socket
import time
import random
import hashlib
import threading
import matplotlib.pyplot as plt

# Cấu hình
SERVER_ADDR = ('127.0.0.1', 9999)
LOSS_RATE = 0.1
TIMEOUT = 1.0 

class UDPClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.5)
        self.ack_received = set()
        self.cwnd = 1
        self.ssthresh = 16
        self.history = []

    def receive_ack(self):
        print("[HỆ THỐNG] Đã kích hoạt luồng nhận ACK...")
        while True:
            try:
                data, _ = self.sock.recvfrom(1024)
                msg = data.decode()
                if "ACK" in msg:
                    seq = int(msg.split(":")[1])
                    if seq not in self.ack_received:
                        self.ack_received.add(seq)
                        # Tăng CWND
                        if self.cwnd < self.ssthresh:
                            self.cwnd *= 2
                        else:
                            self.cwnd += 1
                        print(f"  <-- Nhận ACK: {seq} (CWND hiện tại: {self.cwnd})")
            except:
                continue

    def run(self):
        # Chạy luồng nhận ACK
        t = threading.Thread(target=self.receive_ack, daemon=True)
        t.start()

        messages = [f"Gói-{i}" for i in range(50)]
        base = 0
        sent_times = {}

        print("[HỆ THỐNG] Bắt đầu truyền dữ liệu...")
        
        while base < len(messages):
            # 1. Gửi các gói trong cửa sổ hiện tại
            end = min(base + int(self.cwnd), len(messages))
            for i in range(base, end):
                if i not in sent_times and i not in self.ack_received:
                    packet = f"{i}:{hashlib.md5(messages[i].encode()).hexdigest()[:8]}:{messages[i]}"
                    if random.random() > LOSS_RATE:
                        self.sock.sendto(packet.encode(), SERVER_ADDR)
                        print(f"--> Gửi Seq: {i}")
                    else:
                        print(f"  x Giả lập mất gói: {i}")
                    sent_times[i] = time.time()

            # 2. Kiểm tra Timeout
            now = time.time()
            for i in range(base, end):
                if i in sent_times and i not in self.ack_received:
                    if now - sent_times[i] > TIMEOUT:
                        print(f" [!] Timeout gói {i} - Reset CWND")
                        self.ssthresh = max(self.cwnd // 2, 2)
                        self.cwnd = 1
                        # Gửi lại ngay lập tức
                        self.sock.sendto(f"{i}:retransmit:{messages[i]}".encode(), SERVER_ADDR)
                        sent_times[i] = time.time()

            # 3. Trượt cửa sổ
            while base in self.ack_received:
                base += 1
            
            self.history.append(self.cwnd)
            time.sleep(0.1) # Quan trọng: Để CPU nghỉ và Terminal kịp in dữ liệu

        print("=== THÀNH CÔNG! ĐANG VẼ ĐỒ THỊ ===")
        self.plot()

    def plot(self):
        plt.plot(self.history)
        plt.title("Thay đổi CWND theo thời gian")
        plt.ylabel("Kích thước cửa sổ")
        plt.xlabel("Lượt gửi")
        plt.show()

if __name__ == "__main__":
    client = UDPClient()
    client.run()