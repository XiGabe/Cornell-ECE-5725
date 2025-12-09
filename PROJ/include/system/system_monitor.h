#ifndef SYSTEM_MONITOR_H
#define SYSTEM_MONITOR_H

#include <string>
#include <fstream>
#include <sstream>

struct SystemInfo {
    float cpu_temp;
    float cpu_freq;
    float cpu_usage;
    int memory_used;
    int memory_total;
    float memory_percent;
    long uptime;
};

class SystemMonitor {
public:
    SystemMonitor();
    ~SystemMonitor();

    SystemInfo getSystemInfo();
    float getCpuTemperature();
    float getCpuFrequency();
    float getCpuUsage();
    void getMemoryInfo(int& used, int& total, float& percent);
    long getUptime();
    std::string formatUptime(long seconds);

private:
    long last_idle_time, last_total_time;

    std::string readFile(const std::string& path);
    float parseCpuTemp(const std::string& temp_str);
    float parseCpuFreq(const std::string& freq_str);
};

#endif