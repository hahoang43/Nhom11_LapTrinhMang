# UDP Optimization Techniques Demo

Ứng dụng này mô phỏng các kỹ thuật tối ưu hóa giao thức UDP để làm cho nó đáng tin cậy hơn, tương tự như TCP nhưng vẫn giữ được tốc độ cao của UDP.

## Các Kỹ Thuật Tối Ưu Hóa Được Minh Họa

### 1. Reliability (Đáng Tin Cậy)
- **ACK (Acknowledgment)**: Server gửi ACK cho mỗi gói nhận thành công.
- **Retransmission**: Client retransmit gói nếu không nhận ACK trong timeout.
- **Sequencing**: Sử dụng sequence number để đảm bảo thứ tự gói tin.

### 2. Error Detection (Phát Hiện Lỗi)
- **Checksum**: Sử dụng MD5 hash để kiểm tra tính toàn vẹn của dữ liệu.
- Nếu checksum không khớp, gói bị bỏ qua.

### 3. Congestion Control (Kiểm Soát Tắc Nghẽn)
- **Slow Start**: Bắt đầu với congestion window = 1, nhân đôi mỗi khi nhận ACK.
- **Congestion Avoidance**: Sau khi vượt ssthresh, tăng tuyến tính.
- **Timeout Handling**: Khi timeout, giảm cửa sổ về 1 và điều chỉnh ssthresh.

### 4. Flow Control (Kiểm Soát Luồng)
- **Sliding Window**: Client chỉ gửi số gói bằng kích thước cửa sổ hiện tại.
- Đảm bảo không vượt quá khả năng xử lý của receiver.

## Cách Chạy

1. Chạy server:
   ```bash
   python server.py
   ```

2. Chạy client trong terminal khác:
   ```bash
   python client.py
   ```

## Giả Lập Mạng Lỗi

- Client giả lập mất gói với tỉ lệ 20% (LOSS_RATE = 0.2)
- Điều này cho phép thấy rõ cách các kỹ thuật tối ưu hóa hoạt động trong điều kiện mạng không hoàn hảo.

## Output Mẫu

Client sẽ hiển thị:
- Các gói được gửi và mất.
- Retransmission khi timeout.
- Thay đổi congestion window.

Server sẽ hiển thị:
- Các gói nhận thành công.
- ACK được gửi.
- Xử lý gói đến sớm hoặc trễ.

## So Sánh Với UDP Thô

UDP thô không có các tính năng này:
- Không đảm bảo delivery.
- Không thứ tự.
- Không phát hiện lỗi.
- Không kiểm soát tắc nghẽn.

Ứng dụng này biến UDP thành một giao thức truyền tải đáng tin cậy, tương tự như TCP nhưng có thể tùy chỉnh hơn.