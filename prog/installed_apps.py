import subprocess
from itertools import zip_longest
from prog.utils import clear_screen, print_colored

def list_installed_apps(device_id):
    clear_screen()
    print_colored(f"Installed Apps - Device: {device_id}\n", color="cyan", bold=True)
    
    # Step 1: Get list of installed packages
    result = subprocess.run(['adb', '-s', device_id, 'shell', 'pm', 'list', 'packages'], capture_output=True, text=True)
    package_lines = result.stdout.strip().split('\n')
    
    if package_lines:
        system_apps = []
        user_apps = []
        
        for line in package_lines:
            if line.startswith('package:'):
                package_name = line.split(':')[-1].strip()
                if package_name.startswith('com.android') or package_name.startswith('android.'):
                    system_apps.append(package_name)
                else:
                    user_apps.append(package_name)
        
        # Display up to 30 apps in each category
        max_apps_to_display = 30
        system_apps_display = system_apps[:max_apps_to_display]
        user_apps_display = user_apps[:max_apps_to_display]
        
        # Prepare data for display
        app_data = []
        app_data.append(["System Apps", "User Apps"])  # Header row
        
        # Zip the lists together, filling missing values with ""
        for sys_app, user_app in zip_longest(system_apps_display, user_apps_display, fillvalue=""):
            app_data.append([sys_app, user_app])
        
        # Display the table
        display_table(app_data)
        
        # Ask user if they want to see all apps
        if len(system_apps) > max_apps_to_display or len(user_apps) > max_apps_to_display:
            show_all = input(f"\nFound {len(system_apps)} System Apps and {len(user_apps)} User Apps. Show all? (y/n): ").strip().lower() == 'y'
            
            if show_all:
                app_data_full = []
                app_data_full.append(["System Apps", "User Apps"])  # Header row
                
                # Zip all apps together, filling missing values with ""
                for sys_app, user_app in zip_longest(system_apps, user_apps, fillvalue=""):
                    app_data_full.append([sys_app, user_app])
                
                display_table(app_data_full)
            
    else:
        print("No installed apps found.")


def display_table(table):
    if not table:
        print("No data to display.")
        return
    
    max_key_length = max(len(row[0]) for row in table)
    max_value_length = max(len(row[1]) for row in table) if len(table[0]) > 1 else 0
    
    # Display the table headers
    print(f"┌{'─' * (max_key_length + 2)}┬{'─' * (max_value_length + 2)}┐")
    print(f"│ {'System Apps':<{max_key_length}} │ {'User Apps':<{max_value_length}} │")
    print(f"├{'─' * (max_key_length + 2)}┼{'─' * (max_value_length + 2)}┤")
    
    # Display the table content
    for row in table[1:]:
        print(f"│ {row[0]:<{max_key_length}} │ {row[1]:<{max_value_length}} │")
    
    # Display the table footer
    print(f"└{'─' * (max_key_length + 2)}┴{'─' * (max_value_length + 2)}┘")

