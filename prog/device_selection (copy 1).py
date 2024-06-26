import subprocess
import os
import sys
from installed_apps import list_installed_apps
from device_info import get_device_info
from menu import display_menu  # Import display_menu from menu.py
from open_app import open_app  # Import open_app function
from utils import clear_screen, print_colored, center_text

# Function to list connected devices using adb
def list_connected_devices():
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    output_lines = result.stdout.strip().split('\n')
    devices = []
    for line in output_lines[1:]:
        if 'device' in line:
            device_id = line.split('\t')[0]
            devices.append(device_id)
    return devices

def main_menu():
    try:
        devices = list_connected_devices()

        if not devices:
            print_colored("No devices connected. Exiting.", color="red", bold=True)
            sys.exit()

        while True:
            clear_screen()
            print_colored(center_text("Select a device:"), color="green", bold=True)
            for idx, device in enumerate(devices, start=1):
                print(f"{idx}. {device}")
            print()

            try:
                choice = int(input("Enter device number (1-{}): ".format(len(devices))))
                if 1 <= choice <= len(devices):
                    selected_device = devices[choice - 1]
                    while True:
                        display_menu(selected_device)
                        action = input("Enter your choice (1-4): ")

                        if action == '1':
                            list_installed_apps(selected_device)
                            input("\nPress Enter to continue...")
                        
                        elif action == '2':
                            get_device_info(selected_device)
                            input("\nPress Enter to continue...")
                        
                        elif action == '3':
                            package_name = input("Enter the package name of the app to open: ")
                            open_app(selected_device, package_name)
                            input("\nPress Enter to continue...")
                        
                        elif action == '4':
                            print("Exiting...")
                            sys.exit()
                        
                        else:
                            print("Invalid choice. Please enter a number from 1 to 4.")
                
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit()
