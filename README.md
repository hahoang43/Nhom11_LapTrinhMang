# Kỹ thuật lập trình bất đồng bộ

Lập trình bất đồng bộ (asynchronous programming) là kỹ thuật cho phép các tác vụ được thực thi song song hoặc không bị chặn lẫn nhau, giúp tăng hiệu suất và khả năng đáp ứng của ứng dụng, đặc biệt khi xử lý các tác vụ tốn thời gian như I/O, mạng, truy xuất file, v.v.

## Lợi ích của bất đồng bộ
- Tăng hiệu suất sử dụng CPU
- Giảm thời gian chờ đợi của người dùng
- Cho phép xử lý nhiều tác vụ cùng lúc

## Các kỹ thuật bất đồng bộ phổ biến
- **Callback (Hàm gọi lại):** Hàm được truyền vào như tham số và sẽ được gọi khi tác vụ hoàn thành.
- **Promise/Future:** Đại diện cho kết quả của một tác vụ sẽ hoàn thành trong tương lai, giúp quản lý chuỗi tác vụ bất đồng bộ dễ dàng hơn.
- **Async/Await:** Cú pháp hiện đại giúp viết code bất đồng bộ dễ đọc, dễ bảo trì, dựa trên Promise/Future.
- **Thread/Task (đa luồng, đa nhiệm):** Sử dụng nhiều luồng hoặc tiến trình để thực hiện song song các tác vụ.

## Ứng dụng
- Xử lý tải dữ liệu từ mạng, file, database
- Xây dựng server, ứng dụng realtime
- Tăng tốc các tác vụ tính toán hoặc I/O

## Ví dụ
Tham khảo các file demo trong thư mục này để xem minh họa các kỹ thuật bất đồng bộ bằng Python và JavaScript.

## Hướng dẫn chạy chương trình

### Chạy demo Python
1. Mở terminal, chuyển đến thư mục chứa file.
2. Chạy lệnh:
   
	```bash
	python async_demo.py
	```

### Chạy demo JavaScript
1. Mở terminal, chuyển đến thư mục chứa file.
2. Chạy lệnh:
   
	```bash
	node async_callback_demo.js
	```
