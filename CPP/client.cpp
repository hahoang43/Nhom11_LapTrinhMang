#include <iostream>
#include <string>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

#define PORT 9090
#define SERVER_ADDR "127.0.0.1"
#define BUFFER_SIZE 4096

int main() {
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) return 1;

    SOCKET clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (clientSocket == INVALID_SOCKET) return 1;

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(PORT);
    serverAddr.sin_addr.s_addr = inet_addr(SERVER_ADDR);

    if (connect(clientSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        std::cerr << "Khong the ket noi den Server. Server co dang bat khong?\n";
        closesocket(clientSocket);
        WSACleanup();
        return 1;
    }

    std::cout << "Da ket noi den Server " << SERVER_ADDR << ":" << PORT << "\n";
    std::cout << "Go tin nhan va Enter (go 'exit' de thoat)...\n";

    char buffer[BUFFER_SIZE];
    std::string userInput;

    while (true) {
        std::cout << "Ban: ";
        std::getline(std::cin, userInput);

        if (userInput == "exit") break;

        send(clientSocket, userInput.c_str(), userInput.length() + 1, 0);

        ZeroMemory(buffer, BUFFER_SIZE);
        int bytesReceived = recv(clientSocket, buffer, BUFFER_SIZE, 0);
        if (bytesReceived > 0) {
            std::cout << "Server: " << buffer << "\n";
        }
    }

    closesocket(clientSocket);
    WSACleanup();
    return 0;
}