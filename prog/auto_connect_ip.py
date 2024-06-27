import socket
import subprocess
import ipaddress
import time
import itertools
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from prog.utils import print_colored, clear_screen, print_header
from pyfiglet import Figlet  # Import Figlet for ASCII art text
import re

def get_host_ip():
    """Get the host machine's IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # This doesn't have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
        print_colored(f"Host IP found: {ip}", color="cyan", bold=True)
    except Exception as e:
        ip = '127.0.0.1'
        print_colored(f"Failed to get host IP: {e}", color="red", bold=True)
    finally:
        s.close()
    return ip

def check_port_open(ip, port):
    """Check if a specific port is open on a given IP address."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Timeout for the connection attempt
    try:
        result = sock.connect_ex((ip, port))
        return result == 0
    finally:
        sock.close()

def get_mac_address(ip):
    """Get the MAC address for a given IP address."""
    try:
        arp_output = subprocess.check_output(['arp', '-n', ip])
        mac_match = re.search(r'(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})', arp_output.decode('utf-8'))
        if mac_match:
            return mac_match.group(0)
    except subprocess.CalledProcessError:
        pass
    return None

def scan_ip(ip):
    """Scan a single IP for open port 5555."""
    if check_port_open(ip, 5555):
        return ip
    return None

def scan_network(ip_range):
    """Scan the network for devices with port 5555 open."""
    print_colored(f"Scanning network range: {ip_range}", color="yellow", bold=True)
    devices = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_ip = {executor.submit(scan_ip, str(ip)): ip for ip in ipaddress.IPv4Network(ip_range)}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                if result:
                    mac_addr = get_mac_address(result)
                    if mac_addr:
                        print_colored(f"Port 5555 open on device: {result}, MAC: {mac_addr}", color="green", bold=True)
                        devices.append((result, mac_addr))
                    else:
                        print_colored(f"Port 5555 open on device: {result}, MAC address not found", color="green", bold=True)
                        devices.append((result, "Unknown"))
            except Exception as e:
                print_colored(f"Error scanning {ip}: {e}", color="red", bold=True)
    print()  # Print newline after scanning
    return devices

def connect_devices(devices):
    """Run adb connect on all found devices."""
    for ip, _ in devices:
        print_colored(f"Connecting to device: {ip}", color="blue", bold=True)
        subprocess.run(['adb', 'connect', ip], check=True)

def determine_ip_range():
    host_ip = get_host_ip()
    ip_parts = host_ip.split('.')
    return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"

def auto_connect_device_via_wifi():
    clear_screen()
    print_colored("Auto Connect via Wi-Fi", color='cyan', bold=True)
    host_ip = get_host_ip()
    ip_parts = host_ip.split('.')
    ip_range = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
    devices = scan_network(ip_range)
    print_colored("Scanning complete. Results:", color="yellow", bold=True)
    if devices:
        print_colored(f"Devices found: {', '.join([ip for ip, _ in devices])}", color="green", bold=True)
        connect_devices(devices)
    else:
        print_colored("No devices with port 5555 open found", color="red", bold=True)
    input("Press Enter to go back to the menu...")

def main():
    while True:
        user_input = input("Enter the IP range to scan (or press Enter to use the connected router's IP range): ").strip()
        if user_input:
            ip_range = user_input
        else:
            ip_range = determine_ip_range()
            print(f"Using connected router's IP range: {ip_range}")

        devices = scan_network(ip_range)
        print_colored("Scan Results", color="cyan", bold=True)
        print_colored("{:<20} {:<20}".format("IP Address", "MAC Address"), color="yellow", bold=True)
        print_colored("-" * 40, color="yellow", bold=True)
        for ip, mac in devices:
            print_colored("{:<20} {:<20}".format(ip, mac), color="green", bold=True)

        input("Press Enter to go back to the menu...")

if __name__ == "__main__":
    main()
