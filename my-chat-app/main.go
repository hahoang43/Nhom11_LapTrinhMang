package main

import (
	"fmt"
	"log"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

type Message struct {
	Type    string `json:"type"`
	Sender  string `json:"sender"`
	Content string `json:"content"`
	RoomID  string `json:"roomID"`
}

type Room struct {
	ID       string
	Password string
	Clients  map[*Client]bool
}

type Client struct {
	conn   *websocket.Conn
	send   chan Message
	roomID string
}

var rooms = make(map[string]*Room)
var mu sync.Mutex

func handleConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		return
	}

	roomID := r.URL.Query().Get("roomID")
	password := r.URL.Query().Get("password")

	mu.Lock()
	if _, ok := rooms[roomID]; !ok {
		rooms[roomID] = &Room{
			ID:       roomID,
			Password: password,
			Clients:  make(map[*Client]bool),
		}
	}

	if rooms[roomID].Password != password {
		ws.WriteJSON(Message{Type: "error", Content: "Sai mật khẩu phòng!"})
		ws.Close()
		mu.Unlock()
		return
	}

	// Tạo client mới với buffer channel là 256 để tránh nghẽn
	client := &Client{conn: ws, send: make(chan Message, 256), roomID: roomID}
	rooms[roomID].Clients[client] = true
	mu.Unlock()

	// Thông báo cập nhật số lượng người online
	updateRoomCount(roomID)

	// Luồng Ghi (Writer): Lấy tin từ channel và gửi xuống trình duyệt
	go func() {
		defer ws.Close()
		for msg := range client.send {
			if err := ws.WriteJSON(msg); err != nil {
				break
			}
		}
	}()

	// Luồng Đọc (Reader): Nhận tin từ trình duyệt và đẩy vào hub
	defer func() {
		mu.Lock()
		delete(rooms[roomID].Clients, client)
		mu.Unlock()
		updateRoomCount(roomID)
		ws.Close()
	}()

	for {
		var msg Message
		err := ws.ReadJSON(&msg)
		if err != nil {
			break
		}
		msg.RoomID = roomID
		broadcastToRoom(roomID, msg)
	}
}

func updateRoomCount(roomID string) {
	mu.Lock()
	count := len(rooms[roomID].Clients)
	mu.Unlock()
	broadcastToRoom(roomID, Message{Type: "count", Content: fmt.Sprintf("%d", count)})
}

func broadcastToRoom(roomID string, msg Message) {
	mu.Lock()
	defer mu.Unlock()
	if room, ok := rooms[roomID]; ok {
		for client := range room.Clients {
			select {
			case client.send <- msg:
			default:
				// Nếu channel đầy, đóng kết nối để tránh treo hệ thống
				close(client.send)
				delete(room.Clients, client)
			}
		}
	}
}

func main() {
	http.Handle("/", http.FileServer(http.Dir("./public")))
	http.HandleFunc("/ws", handleConnections)
	fmt.Println("Server Chat High-Load đang chạy tại: http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}