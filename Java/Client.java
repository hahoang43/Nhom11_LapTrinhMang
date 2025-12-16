import java.io.*;
import java.net.*;

public class Client {
    public static void main(String[] args) {
        String host = "127.0.0.1";
        int port = 65432;
        String[] messages = {"Shoot", "Move_Left", "Jump", "Reload"};

        try {
            Socket socket = new Socket(host, port);
            socket.setTcpNoDelay(true);

            socket.setSendBufferSize(64 * 1024);
            // --------------------------------------------

            PrintWriter output = new PrintWriter(socket.getOutputStream(), true);
            BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            for (String msg : messages) {
                System.out.println("Dang gui: " + msg);
                output.println(msg);

                String response = input.readLine();
                System.out.println("Server phan hoi: " + response);

                Thread.sleep(1000);
            }

            socket.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}