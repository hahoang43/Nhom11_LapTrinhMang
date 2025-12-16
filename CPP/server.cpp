#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <algorithm> 
#pragma comment(lib, "ws2_32.lib")

#define PORT 9090
#define BUFFER_SIZE 4096

int main() {
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "Khoi tao Winsock that bai.\n";
        return 1;
    }

    SOCKET serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket == INVALID_SOCKET) {
        std::cerr << "Khong the tao socket.\n";
        WSACleanup();
        return 1;
    }

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(PORT);

    if (bind(serverSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        std::cerr << "Bind that bai. Co the cong " << PORT << " dang ban.\n";
        closesocket(serverSocket);
        WSACleanup();
        return 1;
    }

    if (listen(serverSocket, SOMAXCONN) == SOCKET_ERROR) {
        std::cerr << "Listen that bai.\n";
        return 1;
    }

    std::cout << "Server C++ dang chay tai cong " << PORT << "...\n";

    SOCKET clientSocket;
    sockaddr_in clientAddr;
    int clientAddrLen = sizeof(clientAddr);

    while (true) {
        clientSocket = accept(serverSocket, (sockaddr*)&clientAddr, &clientAddrLen);
        if (clientSocket == INVALID_SOCKET) {
            std::cerr << "Loi ket noi Client.\n";
            continue;
        }

        std::cout << "Client da ket noi!\n";

        char buffer[BUFFER_SIZE];
        while (true) {
            ZeroMemory(buffer, BUFFER_SIZE); 

            int bytesReceived = recv(clientSocket, buffer, BUFFER_SIZE, 0);
            if (bytesReceived <= 0) {
                std::cout << "Client ngat ket noi.\n";
                break;
            }

            std::cout << "-> Nhan duoc: " << buffer << "\n";

            std::string msg(buffer);
            std::transform(msg.begin(), msg.end(), msg.begin(), ::toupper);
            
            std::string response = "Server C++ xac nhan: " + msg;

            send(clientSocket, response.c_str(), response.length(), 0);
        }

        closesocket(clientSocket); 
    }

    closesocket(serverSocket);
    WSACleanup();
    return 0;
}