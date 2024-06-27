import os
import sys
import shutil
import subprocess
from pyfiglet import Figlet  # Import Figlet for ASCII art text

def clear_screen():
    if sys.platform.startswith('win'):
        os.system('cls')
        print_main_heading()
    else:
        os.system('clear')
        print_main_heading()

def print_colored(text, color="white", bold=False):
    colors = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'purple': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
    }
    modifiers = {
        'bold': '\033[1m',
        'underline': '\033[4m',
        'reset': '\033[0m'
    }
    if color in colors:
        color_code = colors[color]
    else:
        color_code = colors['white']

    if bold:
        text = modifiers['bold'] + text + modifiers['reset']

    print(color_code + text + modifiers['reset'])

def display_table(table):
    if not table:
        print("No data to display.")
        return

    max_key_length = max(len(row[0]) for row in table) if table else 0
    max_value_length = max(len(row[1]) for row in table) if table else 0

    # Print the table with formatted borders
    print('┌' + '─' * (max_key_length + 2) + '┬' + '─' * (max_value_length + 2) + '┐')
    for row in table:
        print(f"│ {row[0]:<{max_key_length}} │ {row[1]:<{max_value_length}} │")
    print('└' + '─' * (max_key_length + 2) + '┴' + '─' * (max_value_length + 2) + '┘')

def center_text(text):
    terminal_width = shutil.get_terminal_size().columns
    text_length = len(text)
    if text_length >= terminal_width:
        return text
    spaces = (terminal_width - text_length) // 2
    return ' ' * spaces + text

def print_header(text):
    figlet = Figlet(font='slant')
    header = figlet.renderText(text)
    print_colored(center_text(header), color="cyan", bold=True)

def print_main_heading():
    result = subprocess.run(['figlet', '-f', 'smslant', 'ADB Tools by\nSyed Haseeb'], capture_output=True, text=True)
    if result.returncode == 0:
        output = result.stdout
        columns = shutil.get_terminal_size().columns
        centered_output = "\n".join(line.center(columns) for line in output.split("\n"))
        lolcat_process = subprocess.Popen(['lolcat'], stdin=subprocess.PIPE)
        lolcat_process.communicate(input=centered_output.encode('utf-8'))
    else:
        print_colored("ADB Tools by Syed Haseeb", color="cyan", bold=True)