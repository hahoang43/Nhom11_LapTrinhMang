package main

import (
	"bufio"
	"fmt"
	"log"
	"net"
	"os"
)

const (
	HOST = "localhost"
	PORT = "9090"
	TYPE = "tcp"
)

func main() {
	serverAddr := HOST + ":" + PORT

	conn, err := net.Dial(TYPE, serverAddr)
	if err != nil {
		log.Fatal("Không thể kết nối đến Server:", err)
	}
	defer conn.Close()

	fmt.Println(" Đã kết nối đến Server " + serverAddr)
	fmt.Println("Gõ tin nhắn và nhấn Enter để gửi (Gõ 'exit' để thoát):")

	inputReader := bufio.NewReader(os.Stdin)
	serverReader := bufio.NewReader(conn)

	for {
		fmt.Print("Bạn: ")
		text, _ := inputReader.ReadString('\n')

		fmt.Fprintf(conn, text)

		if text == "exit\n" {
			break
		}

		response, err := serverReader.ReadString('\n')
		if err != nil {
			log.Println("Mất kết nối với Server.")
			return
		}

		fmt.Print("Server: " + response)
	}
}
