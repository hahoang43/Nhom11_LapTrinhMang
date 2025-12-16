import java.io.*;
import java.net.*;

public class Server {
    public static void main(String[] args) {
        int port = 65432;

        try (ServerSocket serverSocket = new ServerSocket(port)) {
            System.out.println("Java Server dang lang nghe tai port " + port + "...");

        
            Socket socket = serverSocket.accept();
            System.out.println("Da ket noi voi: " + socket.getInetAddress());

            socket.setTcpNoDelay(true); 

          
            socket.setReceiveBufferSize(64 * 1024);
            
            System.out.println(">>> [SYSTEM] TCP_NODELAY: ENABLED (Java)");
            System.out.println(">>> [SYSTEM] Buffer Size: " + socket.getReceiveBufferSize());
            
            BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter output = new PrintWriter(socket.getOutputStream(), true);

            String message;
            while ((message = input.readLine()) != null) {
                System.out.println("Nhan duoc tu Client: " + message);
                
              
                output.println("Server Java da nhan: " + message);
            }

            socket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}