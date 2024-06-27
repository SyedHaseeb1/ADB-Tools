import subprocess
import sys
from prog.utils import clear_screen, print_colored, center_text, display_table,print_main_heading
from prog.app_management import app_management
from prog.device_info import get_device_info
from prog.auto_connect_ip import auto_connect_device_via_wifi

from prog.installed_apps import list_installed_apps  # Import the function to list installed apps
from prog.menu import display_menu  # Import display_menu function

def list_connected_devices():
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    output_lines = result.stdout.strip().split('\n')
    devices = []
    for line in output_lines[1:]:
        if 'device' in line:
            device_id = line.split('\t')[0]
            devices.append(device_id)
    return devices

def connect_device_via_wifi(ip_address):
    try:
        subprocess.run(['adb', 'connect', f'{ip_address}:5555'], check=True)
        print_colored(f"Successfully connected to {ip_address}:5555 via WiFi.", color="green")
    except subprocess.CalledProcessError as e:
        print_colored(f"Failed to connect to {ip_address}:5555 via WiFi.", color="red")
        print(e)
        sys.exit()

def display_main_menu(devices_usb):
    clear_screen()
    print_colored("====== ADB Tool Main Menu ======", color="green", bold=True)
    print("===============================")
    print_colored("Connected Devices via USB:", color="cyan", bold=True)
    for idx, device in enumerate(devices_usb, start=1):
        print(f"{idx}. {device}")
    print("===============================")
    print_colored("Add WiFi Device::", color="cyan", bold=True)
    print("'ip' -> Add Device Using IP")
    print("'autoip' -> Search the network")
    print("===============================")
    print_colored("'exit' - Exit the program",color="red",bold=True)
    print("===============================")

def main_menu():
    try:
        while True:
            devices_usb = list_connected_devices()
            display_main_menu(devices_usb)
            choice = input("Select an option: ").strip()

            if choice.lower() == 'ip':
                ip_address = input("Enter the IP address of the device: ").strip()
                connect_device_via_wifi(ip_address)
                continue
            
            if choice.lower() == 'autoip':
            	 auto_connect_device_via_wifi()
            	 continue
               
            elif choice.lower() == 'exit':
                print_colored("Exiting program.", color="cyan")
                sys.exit()

            try:
                choice = int(choice)
                if 1 <= choice <= len(devices_usb):
                    selected_device = devices_usb[choice - 1]
                    while True:
                        display_menu(selected_device)
                        action = input("Enter your choice (1-6): ")

                        if action == '1':
                            list_installed_apps(selected_device)
                            input("\nPress Enter to continue...")

                        elif action == '2':
                            get_device_info(selected_device)
                            input("\nPress Enter to continue...")

                        elif action == '3':
                            app_management(selected_device)
                            input("\nPress Enter to continue...")

                        elif action == '5':
                            print_colored("Back to Main Menu...", color="cyan")
                            main_menu()
                            
                        elif action == '6':
                            print_colored("Exiting...", color="red")
                            sys.exit()
                        else:
                            print_colored("Invalid choice. Please enter a number from 1 to 5.", color="red")

            except ValueError:
                print_colored("Invalid input. Please enter a valid number, 'ip', or 'exit'.", color="red")
    except KeyboardInterrupt:
        print_colored("\nExiting program.", color="cyan")
        sys.exit()

if __name__ == "__main__":
    main_menu()
