import java.net.*;
import java.io.*;

public class TcpServer{
    public static void main(String [] args){
        try{
            ServerSocket ss = new ServerSocket(58849);
            Socket s = ss.accept();

            InputStream ips = s.getInputStream();
            OutputStream ops = s.getOutputStream();

            byte [] buf = new byte[1024];
            System.out.println("start ...");
            int cnt = -1;
            while((cnt=ips.read(buf, 0, buf.length))!=-1){
                System.out.println("total len:" + cnt);
                int author = getInt(subBytes(buf, 0, 4));
                int version = getInt(subBytes(buf, 4, 8));;
                int request = getInt(subBytes(buf, 8, 12));;
                int length = getInt(subBytes(buf, 12, 16));;
                int verify = getInt(subBytes(buf, 16, 20));;
                int device = getInt(subBytes(buf, 20, 24));;
                System.out.println("author:\t" + author);
                System.out.println("version:\t" + version);
                System.out.println("request:\t" + request);
                System.out.println("length:\t" + length);
                System.out.println("verify:\t" + verify);
                System.out.println("device:\t" + device);
                String str = new String(subBytes(buf, 24, cnt-24));
                System.out.println("body:\t" + str + '\n');
            }
            ips.close();
            ops.close();
            s.close();
            ss.close();
        }
        catch(Exception e){
            e.printStackTrace();
        }
    }
    public static int getInt(byte[] bytes){
        return (0xff & bytes[0]) | (0xff00 & (bytes[1] << 8)) | (0xff0000 & (bytes[2] << 16)) | (0xff000000 & (bytes[3] << 24));
    }
    public static byte[] subBytes(byte[] src, int begin, int count) {
        byte[] bs = new byte[count];
        for (int i=begin; i<begin+count; i++)
            bs[i-begin] = src[i];
        return bs;
    }
}
