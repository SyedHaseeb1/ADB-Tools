from prog.utils import clear_screen, print_colored, center_text

def display_menu(device_id):
    clear_screen()
    print_colored(f"Selected Device: {device_id}\n", color="green", bold=True)
    print_colored("====== ADB Tool Menu ======", color="green", bold=True)
    print("1. List Installed Apps")
    print("2. Device Info")
    print("3. Apps Management")  # New menu item
    print("5. Go to Main Menu")
    print("6. Quit")
    print("============================\n")
