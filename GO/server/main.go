package main

import (
	"bufio"
	"fmt"
	"log"
	"net"
	"strings"
)

const (
	HOST = "localhost"
	PORT = "9090"
	TYPE = "tcp"
)

func main() {
	listenAddr := HOST + ":" + PORT
	listener, err := net.Listen(TYPE, listenAddr)
	if err != nil {
		log.Fatal("Lỗi khởi tạo Server:", err)
	}
	defer listener.Close()

	fmt.Println(" Server đang chạy tại", listenAddr)
	fmt.Println("Đang chờ kết nối từ Client...")

	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Println("Lỗi kết nối:", err)
			continue
		}

		go handleClient(conn)
	}
}

func handleClient(conn net.Conn) {
	defer conn.Close()
	
	reader := bufio.NewReader(conn)
	
	fmt.Printf("Client [%s] đã kết nối.\n", conn.RemoteAddr().String())

	for {
		message, err := reader.ReadString('\n')
		if err != nil {
			fmt.Printf("Client [%s] đã ngắt kết nối.\n", conn.RemoteAddr().String())
			return
		}

		fmt.Print("-> Nhận được: ", message)

		response := strings.ToUpper(strings.TrimSpace(message))
		newMsg := "Server xác nhận: " + response + "\n"

		conn.Write([]byte(newMsg))
	}
}