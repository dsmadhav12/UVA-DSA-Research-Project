package org.example;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.concurrent.*;
import org.bytedeco.opencv.global.*;
import org.bytedeco.opencv.opencv_core.*;
import org.bytedeco.opencv.opencv_videoio.*;

import org.bytedeco.javacpp.*;

public class Client {
    //configurations
    private static final String Host = "127.0.0.1";
    private static final int Udp_Port = 65432;
    private static final String Path = "/Users/madhav/Desktop/Coding/Research/UVA-DSA-Research-Project/video/1.mov";

    //socket variables
    private static Socket s;
    private static DatagramSocket udpS;

    public static void main(String[] args) {
        try {
            //thread to handle Socket.IO communication with server
            Thread socketThread = new Thread(new Runnable() {
                public void run() {
                    try {
                        s = IO.socket("http://127.0.0.1:8080");
                        
                        //listeners to handle the various stages such as connect, relay feedback and disconnect
                        Emitter.Listener connectListener = new Emitter.Listener() {
                            public void call(Object... args) {
                                System.out.println("Connected to python server");
                            }
                        };
    
                        Emitter.Listener feedbackListener = new Emitter.Listener() {
                            public void call(Object... args) {
                                //args[0] already formated as desired output
                                System.out.println("Received feedback: " + args[0]);
                            }
                        };
    
                        Emitter.Listener disconnectListener = new Emitter.Listener() {
                            public void call(Object... args) {
                                System.out.println("Disconnected from server");
                            }
                        };
                        
                        //attaches listeners
                        s.on(Socket.EVENT_CONNECT, connectListener);
                        s.on("frame_feedback", feedbackListener);
                        s.on(Socket.EVENT_DISCONNECT, disconnectListener);
                        s.connect();
    
                    } catch (Exception e) {
                        e.printStackTrace();
                        shutdown();
                    }
                }
            });
            //starts the socket.io thread
            socketThread.start();
            //thread to stream video frames over UDP
            Thread streamThread = new Thread(new Runnable() {
                public void run() {
                    try {
                        udpS = new DatagramSocket();
                        streamVideoFrames(Path);
                    } catch (Exception e) {
                        e.printStackTrace();
                        shutdown();
                    }
                }
            });
            streamThread.start();
    
        } catch (Exception e) {
            e.printStackTrace();
            //issues came up so this closes sockets in the case of an error
            shutdown();
        }
    }
    //stream video frames through UDP
    private static void streamVideoFrames(String path) {
    try {
        VideoCapture videoCapture = new VideoCapture(path);
        if (videoCapture.isOpened() == false) {
            System.out.println("Failed to open video file");
            return;
        }
        //image container and address
        Mat frame = new Mat();
        InetAddress address = InetAddress.getByName(Host);

        while (true) {
            //end of video case
            if (!videoCapture.read(frame)){
                break;
            }
            //invalid frame case
            if (frame.empty()){
                continue;
            }
            //resizes image to prevent errors that came up when sending to the server
            opencv_imgproc.resize(frame, frame, new Size(640, 360));

            //makes a frame a jpg file
            BytePointer buffer = new BytePointer();
            IntPointer params = new IntPointer(opencv_imgcodecs.IMWRITE_JPEG_QUALITY, 50);
            opencv_imgcodecs.imencode(".jpg", frame, buffer, params);

            //converts to byte array
            byte[] frameSize = new byte[(int) buffer.limit()];
            buffer.get(frameSize);
            //sends packet to server using UDP
            DatagramPacket packet = new DatagramPacket(frameSize, frameSize.length, address, Udp_Port);
            udpS.send(packet);

            Thread.sleep(100);
        }
        //when completed
        videoCapture.release();
        System.out.println("Done");

    } catch (Exception e) {
        e.printStackTrace();
    }
}
//incase process fails invoke this method to close sockets
private static void shutdown() {
    if ((s != null) && (s.connected())) {
        s.disconnect();
        System.out.println("Socket.IO connection: Closed");
    }
    if ((udpS != null )&& (!udpS.isClosed())) {
        udpS.close();
        System.out.println("UDP socket: Closed");
    }
}
}

