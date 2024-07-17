import subprocess

def start_scrcpy(device_id):
    # Start SCRCPY
    print(f"Device {device_id} Starting Scrcpy.")
    subprocess.run(['scrcpy', '-s', device_id, '-m 720', '-b 1M'])
    input("Press Enter to go back to the menu...")
