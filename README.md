# Nhom11_LapTrinhMang

Repository của nhóm chứa một ứng dụng chat đơn giản viết bằng Go.

**Mục tiêu**: Ứng dụng chat theo phòng (Room) sử dụng WebSocket, phù hợp cho bài tập mạng.

**Cấu trúc**
- `my-chat-app/` : source code server Go và thư mục `public` chứa giao diện front-end
	- `main.go` : server chính (chạy trên `:8080`)
	- `public/` : file tĩnh (HTML/JS/CSS)

**Yêu cầu**
- Go 1.18+ (hoặc phiên bản Go phù hợp với `go.mod`)

**Chạy local**
1. Mở terminal tại thư mục dự án:
```
cd my-chat-app
```
2. Chạy server:
```
go run main.go
```
3. Mở trình duyệt và truy cập:
```
http://localhost:8080
```

**Lưu ý vận hành**
- Server lắng nghe WebSocket tại endpoint `/ws`.
- Khi chạy trên Windows, Git có thể thay đổi CRLF/LF — đã thêm `.gitattributes` để chuẩn hóa (nếu cần).

**Đóng góp & Push lên nhánh `elearning-5`**
- Tạo nhánh local và đẩy lên remote:
```
git checkout -b elearning-5
git add .
git commit -m "Add README and run instructions"
git push -u origin elearning-5
```