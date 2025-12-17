using System;
using System.Net;
using System.Net.Sockets;
using System.IO;

class Program
{
    static void Main(string[] args)
    {
        int port = 65432;
        TcpListener server = new TcpListener(IPAddress.Any, port);
        server.Start();

        Console.WriteLine($"C# Server dang lang nghe tai port {port}...");

        // Chấp nhận kết nối
        TcpClient client = server.AcceptTcpClient();
        Console.WriteLine("Da ket noi voi: " + client.Client.RemoteEndPoint);

        // --- TỐI ƯU HÓA TCP ---
        // 1. Tắt Nagle (TCP_NODELAY)
        client.NoDelay = true;

        // 2. Tăng Buffer nhận
        client.ReceiveBufferSize = 64 * 1024; // 64KB

        // In ra màn hình để chụp ảnh báo cáo
        Console.WriteLine($">>> [SYSTEM] TCP_NODELAY: {(client.NoDelay ? "ENABLED (C#)" : "DISABLED")}");
        Console.WriteLine($">>> [SYSTEM] Buffer Size: {client.ReceiveBufferSize}");
        // ----------------------

        NetworkStream stream = client.GetStream();
        StreamReader reader = new StreamReader(stream);
        StreamWriter writer = new StreamWriter(stream) { AutoFlush = true };

        try
        {
            while (client.Connected)
            {
                string text = reader.ReadLine();
                if (text == null) break;

                Console.WriteLine($"Nhan duoc tu Client: {text}");

                // Phản hồi lại
                writer.WriteLine($"Server C# da nhan: {text}");
            }
        }
        catch { Console.WriteLine("Client da ngat ket noi."); }
        finally { client.Close(); }
    }
}