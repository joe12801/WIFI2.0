#!/bin/bash

PATH_TO_PYTHON_FILE="/home/user/WIFI2.0/network/wifi/main.py"
PORT_TO_CHECK=8080

CHECK_INTERVAL=60  # 延时检查的时间间隔，单位为秒
DELAY=3  # 命令之间的延时，单位为秒

connected=true

check_network_connection() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" "http://www.baidu.com")
    sleep 2
    if [ "$response" = "200" ]; then
        connected=true
        echo "Turning on green internet LED..."
        echo "default-on" > /sys/class/leds/green:internet/trigger
    else
        connected=false
        echo "Turning off green internet LED..."
        echo "none" > /sys/class/leds/green:internet/trigger
    fi
}

check_internet_connection() {
    ping -c 1 baidu.com > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        connected=true
        echo "Turning on green internet LED..."
        echo "default-on" > /sys/class/leds/green:internet/trigger    
        echo "已联网"
    else
        connected=false
        echo "Turning off green internet LED..."
        echo "none" > /sys/class/leds/green:internet/trigger
    fi
}

#while true; do
    check_internet_connection
    sleep 1
    check_internet_connection
    if [[ "$connected" == false ]]; then
        port_in_use=$(lsof -i :$PORT_TO_CHECK)
        if [[ -n "$port_in_use" ]]; then
            echo "Port $PORT_TO_CHECK is already in use. Terminating the process..."
            pid=$(echo "$port_in_use" | awk 'NR==2{print $2}')
            sleep 5
            kill -9 $pid
            echo "Process with PID $pid has been terminated."
        else
            echo "Port $PORT_TO_CHECK is available."
        fi
        
        echo "Connecting to Wi-Fi hotspot..."
        nmcli d wifi hotspot ifname wlan0 ssid 4G-WIFI-gree password 12345678
        sleep $DELAY
        python3 "${PATH_TO_PYTHON_FILE}"
    else
        echo "No further action needed."
    fi
    #sleep $CHECK_INTERVAL  
#done
