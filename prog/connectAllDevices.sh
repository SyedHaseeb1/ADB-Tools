#!/bin/bash
clear
adb kill-server
echo "Looking for devices on the network..."
nmap -v 172.16.30.1-255 -p 5555 | grep "open" > log.txt

# Extract IPs from the output and store them in an array
mapfile -t ips < <(grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' log.txt)

# Loop through each IP and run adb connect
for ip in "${ips[@]}"
do
    adb connect "$ip:5555"
done
echo "__________________________"

adb devices -l

