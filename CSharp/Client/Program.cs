using System;
using System.Net.Sockets;
using System.IO;
using System.Threading;

class Program
{
    static void Main(string[] args)
    {
        try
        {
            TcpClient client = new TcpClient();
            client.Connect("127.0.0.1", 65432);

            // --- TỐI ƯU HÓA TCP ---
            client.NoDelay = true; // Gửi lệnh game đi ngay lập tức
            // ----------------------

            NetworkStream stream = client.GetStream();
            StreamReader reader = new StreamReader(stream);
            StreamWriter writer = new StreamWriter(stream) { AutoFlush = true };

            // Danh sách lệnh giả lập
            string[] commands = { "Shoot", "Move_Left", "Jump", "Reload" };

            foreach (string cmd in commands)
            {
                // 1. Gửi lệnh đi
                Console.WriteLine($"Dang gui: {cmd}");
                writer.WriteLine(cmd);

                // 2. Nhận phản hồi
                string response = reader.ReadLine();
                Console.WriteLine($"Server phan hoi: {response}");

                // Nghỉ 1 giây giả lập thao tác tay
                Thread.Sleep(1000);
            }
            
            client.Close();
        }
        catch (Exception e)
        {
            Console.WriteLine("Loi: " + e.Message);
        }
    }
}