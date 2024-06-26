# open_app.py

import subprocess
from prog.utils import clear_screen, print_colored
from prog.installed_apps import list_installed_apps

def open_app(device_id):
    while True:
        clear_screen()
        print_colored(f"Open App - Device: {device_id}", color="cyan", bold=True)

        # Display the installed apps
        list_installed_apps(device_id)

        # Prompt user to enter the package name
        package_name = input("Enter the package name of the app to open (or 'back' to return to the main menu): ").strip()

        if package_name.lower() == 'back':
            return  # Return to the main menu

        if package_name:
            # Construct the ADB command
            adb_command = ['adb', '-s', device_id, 'shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1']

            try:
                # Execute the ADB command
                result = subprocess.run(adb_command, capture_output=True, text=True, check=True)

                # Print the ADB command executed
                print_colored(f"ADB Command Executed: {' '.join(adb_command)}", color="yellow")

                # Print the output of the ADB command
                if result.stdout:
                    print_colored("ADB Command Output:", color="yellow")
                    print(result.stdout.strip())

                print_colored(f"App '{package_name}' opened successfully.", color="green")

            except subprocess.CalledProcessError as e:
                # Print error message if ADB command execution fails
                print_colored(f"Failed to open the app '{package_name}'. Make sure the package name is correct.", color="red")
                print_colored("Error Message:", color="red")
                print(e.stderr.strip() if e.stderr else str(e))

                # Ask if the user wants to try opening another app
                open_another = input("Do you want to open another app? (y/n): ").strip().lower()
                if open_another != 'y':
                    break  # Return to the main menu

        else:
            print_colored("No package name entered. Please enter a valid package name or 'back' to return to the main menu.", color="red")

    print_colored("Returning to the main menu.", color="cyan")
