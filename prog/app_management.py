# app_management.py

import subprocess
import os
from prog.utils import clear_screen, print_colored
from prog.installed_apps import list_installed_apps  # Import the function to list installed apps
from pyfiglet import Figlet  # Import Figlet from pyfiglet

def open_app(device_id):
    clear_screen()
    print_colored(f"Open App - Device: {device_id}", color="cyan", bold=True)

    # Display the installed apps
    list_installed_apps(device_id)

    # Prompt user to enter the package name
    package_name = input("\nEnter the package name of the app to open (or 'back' to return to the main menu): ").strip()

    if package_name.lower() == 'back':
        return  # Return to the main menu

    if package_name:
        # Try to open the specified app
        try:
            subprocess.run(['adb', '-s', device_id, 'shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'], check=True)
            print_colored(f"App '{package_name}' opened successfully.", color="green")
        except subprocess.CalledProcessError:
            print_colored(f"Failed to open the app '{package_name}'. Make sure the package name is correct.", color="red")
    else:
        print_colored("No package name entered. Please enter a valid package name or 'back' to return to the main menu.", color="red")

    input("\nPress Enter to continue...")

def close_app(device_id):
    clear_screen()
    print_colored(f"Close App - Device: {device_id}", color="cyan", bold=True)

    # Display the installed apps
    list_installed_apps(device_id)

    # Prompt user to enter the package name
    package_name = input("\nEnter the package name of the app to close (or 'back' to return to the main menu): ").strip()

    if package_name.lower() == 'back':
        return  # Return to the main menu

    if package_name:
        # Try to close the specified app
        try:
            subprocess.run(['adb', '-s', device_id, 'shell', 'am', 'force-stop', package_name], check=True)
            print_colored(f"App '{package_name}' closed successfully.", color="green")
        except subprocess.CalledProcessError:
            print_colored(f"Failed to close the app '{package_name}'. Make sure the package name is correct.", color="red")
    else:
        print_colored("No package name entered. Please enter a valid package name or 'back' to return to the main menu.", color="red")

    input("\nPress Enter to continue...")

def install_app(device_id):
    clear_screen()
    print_colored(f"Install App - Device: {device_id}", color="cyan", bold=True)

    # Prompt user for APK path
    apk_path = input("\nEnter the APK file path to install (or 'back' to return to the main menu): ").strip()

    if apk_path.lower() == 'back':
        return  # Return to the main menu

    if os.path.isfile(apk_path):
        # Try to install the app from the specified APK path
        try:
            subprocess.run(['adb', '-s', device_id, 'install', apk_path], check=True)
            print_colored(f"App installed successfully from '{apk_path}'.", color="green")
        except subprocess.CalledProcessError:
            print_colored(f"Failed to install app from '{apk_path}'. Check if the APK path is correct or if the app is already installed.", color="red")
    else:
        print_colored(f"Invalid APK file path: '{apk_path}'. Please enter a valid APK file path or 'back' to return to the main menu.", color="red")

    input("\nPress Enter to continue...")

def uninstall_app(device_id):
    clear_screen()
    print_colored(f"Uninstall App - Device: {device_id}", color="cyan", bold=True)

    # Display the installed apps
    list_installed_apps(device_id)

    # Prompt user to enter the package name
    package_name = input("\nEnter the package name of the app to uninstall (or 'back' to return to the main menu): ").strip()

    if package_name.lower() == 'back':
        return  # Return to the main menu

    if package_name:
        # Try to uninstall the specified app
        try:
            subprocess.run(['adb', '-s', device_id, 'uninstall', package_name], check=True)
            print_colored(f"App '{package_name}' uninstalled successfully.", color="green")
        except subprocess.CalledProcessError:
            print_colored(f"Failed to uninstall the app '{package_name}'. Make sure the package name is correct.", color="red")
    else:
        print_colored("No package name entered. Please enter a valid package name or 'back' to return to the main menu.", color="red")

    input("\nPress Enter to continue...")

def list_installed_apps_menu(device_id):
    clear_screen()
    print_colored(f"Installed Apps - Device: {device_id}", color="cyan", bold=True)
    list_installed_apps(device_id)
    input("\nPress Enter to continue...")

def show_main_menu():
    f = Figlet(font='standard')
    clear_screen()
    print_colored(f.renderText('App Management'), color='green', bold=True)
    print("1. List Installed Apps")
    print("2. Open App")
    print("3. Close App")
    print("4. Install App")
    print("5. Uninstall App")
    print("6. Go Back")
    print("============================\n")

def app_management(device_id):
    while True:
        try:
            show_main_menu()

            choice = input("Enter your choice (1-6): ").strip()

            if choice == '1':
                list_installed_apps_menu(device_id)

            elif choice == '2':
                open_app(device_id)

            elif choice == '3':
                close_app(device_id)

            elif choice == '4':
                install_app(device_id)

            elif choice == '5':
                uninstall_app(device_id)

            elif choice == '6':
                print_colored("Returning to main menu.", color="cyan")
                break

            else:
                print_colored("Invalid choice. Please enter a number from 1 to 6.", color="red")
                input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print_colored("\n\nExiting due to keyboard interrupt.", color="red")
            break
        except ValueError:
            print_colored("Invalid input. Please enter a valid number.", color="red")
            input("\nPress Enter to continue...")

