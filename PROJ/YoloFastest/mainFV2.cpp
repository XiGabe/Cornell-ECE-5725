// Tencent is pleased to support the open source community by making ncnn available.
//
// Copyright (C) 2020 THL A29 Limited, a Tencent company. All rights reserved.
//
// Licensed under the BSD 3-Clause License (the "License"); you may not use this file except
// in compliance with the License. You may obtain a copy of the License at
//
// https://opensource.org/licenses/BSD-3-Clause
//
// Unless required by applicable law or agreed to in writing, software distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.

//modified 12-31-2021 Q-engineering
//modified 11-09-2025 for MJPEG streaming

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <stdio.h>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <sstream>
#include <signal.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <malloc.h>
#include <fstream>
#include <sstream>
// #include <iomanip>  // 暂时不需要
// #include <cmath>     // 暂时不需要
#include "yolo-fastestv2.h"
#include "system_monitor.h"
#include "motor_control.h"
#include "visual_servo.h"

yoloFastestv2 yoloF2;

const char* class_names[] = {
    "hand"
};

// Global variables for MJPEG streaming
std::mutex frame_mutex;
cv::Mat current_frame;
std::atomic<bool> streaming_active{true};
const int HTTP_PORT = 8080;

// JPEG buffer for efficient streaming
std::mutex jpeg_mutex;
std::vector<uchar> global_jpeg_buffer;

// System monitor
SystemMonitor sys_monitor;

// Visual servo controller
VisualServoController visual_servo;

// Function to read HTML template
std::string readHtmlTemplate() {
    std::ifstream file("/home/pi/ECE-5725-Everything/PROJ/YoloFastest/web_template.html");
    if (!file.is_open()) {
        std::cerr << "Could not open HTML template file" << std::endl;
        return "<html><body><h1>Hand Detection System</h1><img src='/stream' /></body></html>";
    }
    std::string content((std::istreambuf_iterator<char>(file)),
                        std::istreambuf_iterator<char>());
    file.close();
    return content;
}

// Function to generate system info JSON
std::string getSystemInfoJson() {
    SystemInfo info = sys_monitor.getSystemInfo();
    std::ostringstream json;
    json << "{"
         << "\"cpu_temp\":" << info.cpu_temp << ","
         << "\"cpu_freq\":" << info.cpu_freq << ","
         << "\"cpu_usage\":" << info.cpu_usage << ","
         << "\"memory_used\":" << info.memory_used << ","
         << "\"memory_total\":" << info.memory_total << ","
         << "\"memory_percent\":" << info.memory_percent << ","
         << "\"uptime\":" << info.uptime << ","
         << "\"uptime_formatted\":\"" << sys_monitor.formatUptime(info.uptime) << "\""
         << "}";
    return json.str();
}

// Memory cleanup function
void cleanup_memory() {
    std::cout << "\n=== Memory Cleanup Started ===" << std::endl;

    // 清理视觉伺服控制器 (包括电机控制)
    std::cout << "Cleaning up visual servo controller..." << std::endl;
    // visual_servo 析构函数会自动调用 cleanup_motors()

    // Release OpenCV Mat
    {
        std::lock_guard<std::mutex> lock(frame_mutex);
        if (!current_frame.empty()) {
            current_frame.release();
            std::cout << "Released OpenCV frame buffer" << std::endl;
        }
    }

    // Clear JPEG buffer
    {
        std::lock_guard<std::mutex> lock(jpeg_mutex);
        global_jpeg_buffer.clear();
        std::cout << "Cleared JPEG buffer" << std::endl;
    }

    // Note: OpenCV automatic memory management will handle Mat cleanup
    std::cout << "OpenCV buffers released" << std::endl;

    // System memory cleanup (Linux)
    std::cout << "Clearing system caches..." << std::endl;
    system("sync");
    system("echo 1 > /proc/sys/vm/drop_caches 2>/dev/null");
    system("echo 2 > /proc/sys/vm/drop_caches 2>/dev/null");
    system("echo 3 > /proc/sys/vm/drop_caches 2>/dev/null");

    // Return memory to system (if available)
#ifdef __GLIBC__
    malloc_trim(0);
    std::cout << "Trimmed malloc heap" << std::endl;
#endif

    std::cout << "=== Memory Cleanup Completed ===" << std::endl;
    std::cout << "Program terminated safely. All resources cleaned up." << std::endl;
}

// Signal handler for Ctrl+C
void signal_handler(int signum) {
    std::cout << "\nReceived signal " << signum << " (Ctrl+C)" << std::endl;
    std::cout << "Initiating graceful shutdown..." << std::endl;

    // Stop streaming
    streaming_active = false;

    // Give threads time to finish
    usleep(500000); // 500ms

    // Clean up memory
    cleanup_memory();

    exit(signum);
}

// Function to handle individual HTTP requests
void handle_http_request(int new_socket) {
    char buffer[2048] = {0};
    int bytes_received = recv(new_socket, buffer, sizeof(buffer) - 1, 0);
    if (bytes_received <= 0) {
        close(new_socket);
        return;
    }

    buffer[bytes_received] = '\0';
    std::cout << "HTTP Request received: " << std::string(buffer).substr(0, 100) << "..." << std::endl;

    // Parse HTTP request
    std::string request(buffer);
    std::string response;

    if (request.find("GET /system-info") != std::string::npos) {
        // System info JSON API
        std::string sys_json = getSystemInfoJson();
        response = "HTTP/1.1 200 OK\r\n";
        response += "Content-Type: application/json\r\n";
        response += "Access-Control-Allow-Origin: *\r\n";
        response += "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n";
        response += "Access-Control-Allow-Headers: Content-Type\r\n";
        response += "Cache-Control: no-cache, no-store, must-revalidate\r\n";
        response += "Content-Length: " + std::to_string(sys_json.length()) + "\r\n\r\n";
        response += sys_json;
        send(new_socket, response.c_str(), response.length(), 0);
    } else if (request.find("GET /stream") != std::string::npos) {
        std::cout << "Starting MJPEG stream for client" << std::endl;

        // MJPEG streaming response
        response = "HTTP/1.1 200 OK\r\n";
        response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n";
        response += "Cache-Control: no-cache\r\n";
        response += "Connection: close\r\n\r\n";

        if (send(new_socket, response.c_str(), response.length(), 0) < 0) {
            close(new_socket);
            return;
        }

        // Stream frames efficiently - use pre-encoded JPEG
        int stream_frame_count = 0;
        while(streaming_active) {
            std::vector<uchar> jpeg_buffer_copy;
            {
                // Get the latest JPEG data (already encoded by main thread)
                std::lock_guard<std::mutex> lock(jpeg_mutex);
                if (global_jpeg_buffer.empty()) {
                    usleep(33000); // Wait for first frame to be encoded
                    continue;
                }
                jpeg_buffer_copy = global_jpeg_buffer;
            }

            // Send frame header
            std::string frame_header = "--frame\r\n";
            frame_header += "Content-Type: image/jpeg\r\n";
            frame_header += "Content-Length: " + std::to_string(jpeg_buffer_copy.size()) + "\r\n\r\n";

            // Send data efficiently
            if (send(new_socket, frame_header.c_str(), frame_header.length(), 0) < 0) {
                std::cout << "Client disconnected from stream" << std::endl;
                break;
            }
            if (send(new_socket, jpeg_buffer_copy.data(), jpeg_buffer_copy.size(), 0) < 0) {
                std::cout << "Failed to send frame data" << std::endl;
                break;
            }
            if (send(new_socket, "\r\n", 2, 0) < 0) {
                std::cout << "Failed to send frame boundary" << std::endl;
                break;
            }

            stream_frame_count++;
            // Removed frame count logging to reduce console output

            usleep(33000); // ~30 FPS
        }
    } else {
        // Default response - use beautiful HTML template
        std::string html_content = readHtmlTemplate();
        response = "HTTP/1.1 200 OK\r\n";
        response += "Content-Type: text/html\r\n";
        response += "Cache-Control: no-cache\r\n";
        response += "Content-Length: " + std::to_string(html_content.length()) + "\r\n\r\n";
        response += html_content;
        send(new_socket, response.c_str(), response.length(), 0);
    }

    close(new_socket);
}

// MJPEG HTTP server function
void http_server() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        return;
    }

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("setsockopt");
        return;
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;  // Listen on all interfaces
    address.sin_port = htons(HTTP_PORT);

    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address))<0) {
        perror("bind failed");
        return;
    }

    if (listen(server_fd, 10) < 0) {  // Increased backlog
        perror("listen");
        return;
    }

    std::cout << "MJPEG server started on port " << HTTP_PORT << std::endl;
    std::cout << "Local access: http://localhost:" << HTTP_PORT << std::endl;
    std::cout << "Network access: http://192.168.1.17:" << HTTP_PORT << std::endl;

    while(streaming_active) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen))<0) {
            if (streaming_active) {
                perror("accept");
            }
            continue;
        }

        // Get client IP for logging
        char client_ip[INET6_ADDRSTRLEN];
        void *addr_ptr;
        if (address.sin_family == AF_INET) {
            addr_ptr = &((struct sockaddr_in*)&address)->sin_addr;
        } else {
            addr_ptr = &((struct sockaddr_in6*)&address)->sin6_addr;
        }
        inet_ntop(address.sin_family, addr_ptr, client_ip, INET6_ADDRSTRLEN);
        std::cout << "Connection from: " << client_ip << std::endl;

        // Create a new thread to handle this request
        std::thread request_thread(handle_http_request, new_socket);
        request_thread.detach();  // Detach to handle independently
    }

    close(server_fd);
}

static void draw_objects(cv::Mat& cvImg, const std::vector<TargetBox>& boxes)
{
    for(size_t i = 0; i < boxes.size(); i++) {
//        std::cout<<boxes[i].x1<<" "<<boxes[i].y1<<" "<<boxes[i].x2<<" "<<boxes[i].y2
//                 <<" "<<boxes[i].score<<" "<<boxes[i].cate<<std::endl;

        char text[256];
        sprintf(text, "%s %.1f%%", class_names[boxes[i].cate], boxes[i].score * 100);

        int baseLine = 0;
        cv::Size label_size = cv::getTextSize(text, cv::FONT_HERSHEY_SIMPLEX, 0.5, 1, &baseLine);

        int x = boxes[i].x1;
        int y = boxes[i].y1 - label_size.height - baseLine;
        if (y < 0) y = 0;
        if (x + label_size.width > cvImg.cols) x = cvImg.cols - label_size.width;

        cv::rectangle(cvImg, cv::Rect(cv::Point(x, y), cv::Size(label_size.width, label_size.height + baseLine)),
                      cv::Scalar(255, 255, 255), -1);

        cv::putText(cvImg, text, cv::Point(x, y + label_size.height),
                    cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 0, 0));

        cv::rectangle (cvImg, cv::Point(boxes[i].x1, boxes[i].y1),
                       cv::Point(boxes[i].x2, boxes[i].y2), cv::Scalar(255,0,0));
    }
}

int main(int argc, char** argv)
{
    // Register signal handlers for graceful shutdown
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    float f;
    float FPS[16];
    int i,Fcnt=0;
    cv::Mat frame;
    //some timing
    std::chrono::steady_clock::time_point Tbegin, Tend;

    for(i=0;i<16;i++) FPS[i]=0.0;

    std::cout << "Initializing YOLO hand detection system..." << std::endl;

    yoloF2.init(false); //we have no GPU

    yoloF2.loadModel("yolo-fastestv2-opt.param","yolo-fastestv2-opt.bin");
    std::cout << "Model loaded successfully" << std::endl;

    // 初始化视觉伺服控制器
    if (visual_servo.initialize() != 0) {
        std::cerr << "Failed to initialize visual servo controller!" << std::endl;
        return -1;
    }

    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "ERROR: Unable to open the camera" << std::endl;
        std::cout << "Trying different camera indices..." << std::endl;

        // Try different camera indices
        for(int i = 1; i < 5; i++) {
            cap.open(i);
            if (cap.isOpened()) {
                std::cout << "Camera found at index " << i << std::endl;
                break;
            }
        }

        if (!cap.isOpened()) {
            std::cerr << "ERROR: No camera found" << std::endl;
            return 0;
        }
    }

    // 优化的摄像头设置
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
    cap.set(cv::CAP_PROP_FPS, 30);

    // 关键优化：减少缓冲区延迟
    cap.set(cv::CAP_PROP_BUFFERSIZE, 1);  // 最小缓冲区
    cap.set(cv::CAP_PROP_FOURCC, cv::VideoWriter::fourcc('M','J','P','G'));  // 尝试MJPEG格式

    // 如果MJPEG不支持，回退到YUYV但优化其他参数
    if (cap.get(cv::CAP_PROP_FOURCC) != cv::VideoWriter::fourcc('M','J','P','G')) {
        std::cout << "MJPEG not supported, using YUYV format" << std::endl;
        cap.set(cv::CAP_PROP_FOURCC, cv::VideoWriter::fourcc('Y','U','Y','V'));
    }

    std::cout << "Camera initialized successfully" << std::endl;

    // Start HTTP server thread
    std::thread server_thread(http_server);

    std::cout << "Start grabbing, press ESC on terminal to terminate" << std::endl;
    std::cout << "Camera feed is now streaming to http://localhost:8080" << std::endl;

	int frame_count = 0;
	while(1){
//        frame=cv::imread("000139.jpg");  //need to refresh frame before dnn class detection
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "ERROR: Unable to grab from the camera" << std::endl;
            usleep(1000000); // Wait 1 second before retry
            continue;
        }

        frame_count++;
        if (frame_count % 30 == 0) {
            std::cout << "Processing frame " << frame_count << std::endl;
        }

        Tbegin = std::chrono::steady_clock::now();

        std::vector<TargetBox> boxes;
        yoloF2.detection(frame, boxes, 0.4);
        draw_objects(frame, boxes);
        Tend = std::chrono::steady_clock::now();

        // 基于YOLO检测结果的视觉伺服控制
        visual_servo.process_detection(boxes);

        //calculate frame rate
        f = std::chrono::duration_cast <std::chrono::milliseconds> (Tend - Tbegin).count();
        if(f>0.0) FPS[((Fcnt++)&0x0F)]=1000.0/f;
        for(f=0.0, i=0;i<16;i++){ f+=FPS[i]; }
        putText(frame, cv::format("FPS %0.2f", f/16),cv::Point(10,20),cv::FONT_HERSHEY_SIMPLEX,0.6, cv::Scalar(0, 0, 255));

        // Update global frame for streaming
        {
            std::lock_guard<std::mutex> lock(frame_mutex);
            current_frame = frame.clone();
        }

        // Encode JPEG once for all streaming clients - optimized
        {
            std::vector<uchar> temp_jpeg_buffer;
            std::vector<int> params = {cv::IMWRITE_JPEG_QUALITY, 75, cv::IMWRITE_JPEG_OPTIMIZE, 1};

            // 使用更小的ROI区域编码以减少处理时间
            cv::Rect roi(0, 0, frame.cols, frame.rows);
            cv::Mat jpeg_frame = frame(roi);

            cv::imencode(".jpg", jpeg_frame, temp_jpeg_buffer, params);

            std::lock_guard<std::mutex> lock(jpeg_mutex);
            global_jpeg_buffer = std::move(temp_jpeg_buffer);
        }

        // Optional: Keep local preview window (comment out if not needed)
        // cv::imshow("Hand Detection",frame);

        // Check for ESC key to exit (requires OpenCV window)
        char esc = cv::waitKey(5);
        if(esc == 27) break;

        // Also exit if streaming is no longer active
        if(!streaming_active) break;
	}

    // Stop streaming and wait for server thread
    streaming_active = false;
    server_thread.join();

    std::cout << "Streaming stopped" << std::endl;

    // Clean up memory on normal exit
    cleanup_memory();

    return 0;
}
