import subprocess

def start_tcp(device_id):
    # Restart device in TCP/IP mode on port 5555
    subprocess.run(['adb', '-s', device_id, 'tcpip', '5555'])
    print(f"Device {device_id} restarted in TCP/IP mode on port 5555.")
    input("Press Enter to go back to the menu...")
