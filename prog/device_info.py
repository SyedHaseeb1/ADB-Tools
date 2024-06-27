import subprocess
import re
from prog.utils import clear_screen, print_colored, display_table

def get_device_info(device_id):
    clear_screen()
    print_colored(f"Device Info - Device: {device_id}", color="cyan", bold=True)

    # Retrieve device properties
    prop_commands = {
        'Model': 'ro.product.model',
        'Android Version': 'ro.build.version.release',
        'CPU': 'ro.product.cpu.abi',
        'Codename': 'ro.build.version.codename',
        'Build ID': 'ro.build.id',
        'Manufacturer': 'ro.product.brand',
        'Device': 'ro.product.device',
        'Product Name': 'ro.product.name',
        'Board': 'ro.product.board',
        'Build Tags': 'ro.build.tags',
        'Build Type': 'ro.build.type',
        'Build User': 'ro.build.user',
        'Build Description': 'ro.build.description',
    }

    info_dict = {}
    for key, command in prop_commands.items():
        result = subprocess.run(['adb', '-s', device_id, 'shell', 'getprop', command], capture_output=True, text=True)
        value = result.stdout.strip()
        if value:
            info_dict[key] = value

    # Get RAM and ROM information
    meminfo_result = subprocess.run(['adb', '-s', device_id, 'shell', 'cat', '/proc/meminfo'], capture_output=True, text=True)
    storage_result = subprocess.run(['adb', '-s', device_id, 'shell', 'df', '/sdcard'], capture_output=True, text=True)

    ram_total = None
    ram_free = None
    for line in meminfo_result.stdout.strip().split('\n'):
        if line.startswith('MemTotal'):
            ram_total = int(line.split()[1])  # In KB
        elif line.startswith('MemFree'):
            ram_free = int(line.split()[1])   # In KB

    rom_total = None
    rom_free = None
    for line in storage_result.stdout.strip().split('\n'):
        if '/storage/emulated' in line:
            parts = line.split()
            rom_total = int(parts[1])  # In KB
            rom_free = int(parts[3])   # In KB

    # Get Battery information
    battery_result = subprocess.run(['adb', '-s', device_id, 'shell', 'dumpsys', 'battery'], capture_output=True, text=True)
    battery_level = None
    for line in battery_result.stdout.strip().split('\n'):
        if 'level' in line:
            battery_level = line.split(':')[1].strip()

    # Get Battery information
    charging_status = "Unknown"
    for line in battery_result.stdout.strip().split('\n'):
        if 'AC powered: true' in line:
            charging_status = 'Charging (AC)'
        elif 'USB powered: true' in line:
            charging_status = 'Charging (USB)'
        elif 'Wireless powered: true' in line:
            charging_status = 'Charging (Wireless)'
        elif 'status:' in line:
            if 'discharging' in line:
                charging_status = 'Discharging'


    # Get Network information
    network_result = subprocess.run(['adb', '-s', device_id, 'shell', 'dumpsys', 'wifi'], capture_output=True, text=True)
    ip_address = None
    gateway = None
    dns_servers = []

    # Extract IP address and other network details
    ip_regex = r'IP address (.+?)/'
    gateway_regex = r'Gateway (.+?) '
    dns_regex = r'DNS servers: \[ (.+?) \]'

    ip_match = re.search(ip_regex, network_result.stdout)
    if ip_match:
        ip_address = ip_match.group(1)

    gateway_match = re.search(gateway_regex, network_result.stdout)
    if gateway_match:
        gateway = gateway_match.group(1)

    dns_match = re.search(dns_regex, network_result.stdout)
    if dns_match:
        dns_servers = dns_match.group(1).split()

    # Convert KB to MB or GB as appropriate
    def convert_size(size_kb):
        if size_kb >= 1024 ** 2:  # GB
            return f"{size_kb / (1024 ** 2):.2f} GB"
        elif size_kb >= 1024:     # MB
            return f"{size_kb / 1024:.2f} MB"
        else:                     # KB
            return f"{size_kb} KB"

    # Prepare device info table
    table = [
        ["Device Info - Device:", device_id],
        ["Model", info_dict.get("Model", "")],
        ["Android Version", info_dict.get("Android Version", "")],
        ["CPU", info_dict.get("CPU", "")],
        ["Codename", info_dict.get("Codename", "")],
        ["Build ID", info_dict.get("Build ID", "")],
        ["Manufacturer", info_dict.get("Manufacturer", "")],
        ["Device", info_dict.get("Device", "")],
        ["Product Name", info_dict.get("Product Name", "")],
        ["Board", info_dict.get("Board", "")],
        ["Build Tags", info_dict.get("Build Tags", "")],
        ["Build Type", info_dict.get("Build Type", "")],
        ["Build User", info_dict.get("Build User", "")],
        ["Build Description", info_dict.get("Build Description", "")],
        ["Total RAM", convert_size(ram_total) if ram_total else ""],
        ["Free RAM / Used RAM", f"({convert_size(ram_free)} / {convert_size(ram_total - ram_free)})" if ram_total and ram_free else ""],
        ["ROM (Internal Storage)", convert_size(rom_total) if rom_total else ""],
        ["Free ROM / Used ROM", f"({convert_size(rom_free)} / {convert_size(rom_total - rom_free)})" if rom_total and rom_free else ""],
        ["Battery Level", f"{battery_level}%" if battery_level else ""],
        ["Charging Status", charging_status if charging_status else ""],
        ["IP Address", ip_address if ip_address else ""],
        ["Gateway", gateway if gateway else ""],
        ["DNS Servers", ", ".join(dns_servers) if dns_servers else ""]
    ]

    # Display the formatted table
    display_table(table)

# Example usage
if __name__ == "__main__":
    device_id = "your_device_serial_number"
    get_device_info(device_id)
