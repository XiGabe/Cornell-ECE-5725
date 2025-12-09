#include "system/system_monitor.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <unistd.h>

SystemMonitor::SystemMonitor() : last_idle_time(0), last_total_time(0) {
}

SystemMonitor::~SystemMonitor() {
}

std::string SystemMonitor::readFile(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        return "";
    }
    std::string content((std::istreambuf_iterator<char>(file)),
                        std::istreambuf_iterator<char>());
    file.close();
    return content;
}

float SystemMonitor::parseCpuTemp(const std::string& temp_str) {
    float temp = 0.0f;
    try {
        temp = std::stof(temp_str) / 1000.0f; // Convert from millidegrees to degrees
    } catch (...) {
        // Try different thermal zones
        for (int zone = 0; zone < 10; zone++) {
            std::string path = "/sys/class/thermal/thermal_zone" + std::to_string(zone) + "/temp";
            std::string temp_data = readFile(path);
            if (!temp_data.empty()) {
                try {
                    temp = std::stof(temp_data) / 1000.0f;
                    if (temp > 0 && temp < 150) break; // Valid temperature range
                } catch (...) {}
            }
        }
    }
    return temp;
}

float SystemMonitor::getCpuTemperature() {
    // Try Raspberry Pi specific path first
    std::string temp_str = readFile("/sys/class/thermal/thermal_zone0/temp");
    if (!temp_str.empty()) {
        return parseCpuTemp(temp_str);
    }

    // Fallback to vcgencmd (Raspberry Pi)
    FILE* pipe = popen("vcgencmd measure_temp", "r");
    if (pipe) {
        char buffer[128];
        if (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
            std::string result(buffer);
            pclose(pipe);
            // Parse "temp=45.5'C"
            size_t start = result.find("=");
            size_t end = result.find("'");
            if (start != std::string::npos && end != std::string::npos) {
                try {
                    return std::stof(result.substr(start + 1, end - start - 1));
                } catch (...) {}
            }
        }
        pclose(pipe);
    }

    return 0.0f;
}

float SystemMonitor::parseCpuFreq(const std::string& freq_str) {
    try {
        return std::stof(freq_str) / 1000.0f; // Convert to MHz
    } catch (...) {
        return 0.0f;
    }
}

float SystemMonitor::getCpuFrequency() {
    // Try reading current CPU frequency
    std::string freq_str = readFile("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq");
    if (!freq_str.empty()) {
        return parseCpuFreq(freq_str);
    }

    // Fallback: try reading min and max frequencies
    std::string min_freq = readFile("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq");
    std::string max_freq = readFile("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq");

    if (!min_freq.empty() && !max_freq.empty()) {
        try {
            float min_f = std::stof(min_freq) / 1000.0f;
            float max_f = std::stof(max_freq) / 1000.0f;
            return (min_f + max_f) / 2.0f; // Return average
        } catch (...) {}
    }

    // Last resort: try /proc/cpuinfo
    FILE* pipe = popen("lscpu | grep 'CPU MHz'", "r");
    if (pipe) {
        char buffer[256];
        if (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
            std::string result(buffer);
            pclose(pipe);
            size_t pos = result.find(":");
            if (pos != std::string::npos) {
                try {
                    return std::stof(result.substr(pos + 1));
                } catch (...) {}
            }
        }
        pclose(pipe);
    }

    return 0.0f;
}

float SystemMonitor::getCpuUsage() {
    std::string stat = readFile("/proc/stat");
    if (stat.empty()) return 0.0f;

    std::istringstream iss(stat);
    std::string cpu_label;
    long user, nice, system, idle, iowait, irq, softirq, steal;

    if (iss >> cpu_label >> user >> nice >> system >> idle >> iowait >> irq >> softirq >> steal) {
        long total_time = user + nice + system + idle + iowait + irq + softirq + steal;
        long idle_time = idle + iowait;

        if (last_total_time != 0) {
            long total_diff = total_time - last_total_time;
            long idle_diff = idle_time - last_idle_time;

            if (total_diff > 0) {
                float usage = 100.0f * (1.0f - (float)idle_diff / total_diff);
                last_idle_time = idle_time;
                last_total_time = total_time;
                return usage;
            }
        }

        last_idle_time = idle_time;
        last_total_time = total_time;
    }

    return 0.0f;
}

void SystemMonitor::getMemoryInfo(int& used, int& total, float& percent) {
    std::string meminfo = readFile("/proc/meminfo");
    if (meminfo.empty()) {
        used = total = 0;
        percent = 0.0f;
        return;
    }

    std::istringstream iss(meminfo);
    std::string line;
    long mem_total = 0, mem_free = 0, mem_available = 0, buffers = 0, cached = 0;

    while (std::getline(iss, line)) {
        if (line.find("MemTotal:") == 0) {
            sscanf(line.c_str(), "MemTotal: %ld kB", &mem_total);
        } else if (line.find("MemFree:") == 0) {
            sscanf(line.c_str(), "MemFree: %ld kB", &mem_free);
        } else if (line.find("MemAvailable:") == 0) {
            sscanf(line.c_str(), "MemAvailable: %ld kB", &mem_available);
        } else if (line.find("Buffers:") == 0) {
            sscanf(line.c_str(), "Buffers: %ld kB", &buffers);
        } else if (line.find("Cached:") == 0) {
            sscanf(line.c_str(), "Cached: %ld kB", &cached);
        }
    }

    if (mem_total > 0) {
        if (mem_available > 0) {
            used = mem_total - mem_available;
        } else {
            used = mem_total - mem_free - buffers - cached;
        }
        total = mem_total;
        percent = (float)used / total * 100.0f;
    } else {
        used = total = 0;
        percent = 0.0f;
    }
}

long SystemMonitor::getUptime() {
    std::string uptime_str = readFile("/proc/uptime");
    if (!uptime_str.empty()) {
        try {
            return std::stol(uptime_str);
        } catch (...) {}
    }
    return 0;
}

std::string SystemMonitor::formatUptime(long seconds) {
    long days = seconds / 86400;
    long hours = (seconds % 86400) / 3600;
    long minutes = (seconds % 3600) / 60;

    std::ostringstream oss;
    if (days > 0) {
        oss << days << "d " << hours << "h " << minutes << "m";
    } else if (hours > 0) {
        oss << hours << "h " << minutes << "m";
    } else {
        oss << minutes << "m";
    }
    return oss.str();
}

SystemInfo SystemMonitor::getSystemInfo() {
    SystemInfo info;
    info.cpu_temp = getCpuTemperature();
    info.cpu_freq = getCpuFrequency();
    info.cpu_usage = getCpuUsage();
    getMemoryInfo(info.memory_used, info.memory_total, info.memory_percent);
    info.uptime = getUptime();

    return info;
}