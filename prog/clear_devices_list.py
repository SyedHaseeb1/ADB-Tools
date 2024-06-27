import subprocess

def clear_adb_devices():
    try:
        # Run adb command to disconnect all devices
        subprocess.run(["adb", "disconnect"], check=True)
        print("ADB connected devices list cleared.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")