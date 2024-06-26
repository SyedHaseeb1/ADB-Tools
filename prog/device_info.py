import subprocess
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
        ["Free ROM / Used ROM", f"({convert_size(rom_free)} / {convert_size(rom_total - rom_free)})" if rom_total and rom_free else ""]
    ]
    
    # Display the formatted table
    display_table(table)
