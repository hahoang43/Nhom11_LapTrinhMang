import socket
import hashlib

class UDPServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', 9999))
        self.received_messages = {}
        self.expected_seq = 0

    def calculate_checksum(self, data):
        return hashlib.md5(data.encode()).hexdigest()[:8]

    def process_packet(self, data, addr):
        try:
            packet_str = data.decode()
            parts = packet_str.split(':', 2)
            if len(parts) < 3: return

            seq_num = int(parts[0])
            checksum = parts[1]
            message = parts[2]

            # Kiểm tra lỗi (Error Detection)
            if checksum != self.calculate_checksum(message) and parts[1] != "retransmit":
                print(f"(!) Lỗi Checksum tại Seq={seq_num}")
                return

            # Gửi ACK ngay lập tức cho gói nhận được
            self.sock.sendto(f"ACK:{seq_num}".encode(), addr)

            if seq_num == self.expected_seq:
                print(f"Nhận: Seq={seq_num}")
                self.expected_seq += 1
                # Kiểm tra các gói nhận sớm đã lưu trong buffer
                while self.expected_seq in self.received_messages:
                    del self.received_messages[self.expected_seq]
                    self.expected_seq += 1
            elif seq_num > self.expected_seq:
                self.received_messages[seq_num] = message
                print(f"Nhận sớm: Seq={seq_num}, lưu vào bộ đệm")
            else:
                print(f"Gói trùng lặp: Seq={seq_num}")

        except Exception as e:
            print(f"Lỗi: {e}")

    def run(self):
        print("=== SERVER UDP TỐI ƯU ĐANG CHẠY ===")
        while True:
            data, addr = self.sock.recvfrom(1024)
            self.process_packet(data, addr)

if __name__ == "__main__":
    server = UDPServer()
    server.run()