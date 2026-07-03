# Feature Documentation

## Overview

ADB-Tools Desktop provides comprehensive Android device management through a modern, intuitive interface. This document details each feature, how to use it, and the underlying implementation.

---

## 1. Device Management

### 1.1 Device List & Connection

**What it does**: Displays all connected Android devices (USB and WiFi) with real-time status.

**How to use**:
1. Launch the app
2. Connected devices appear in the **Device Panel** (left sidebar)
3. Click a device to select it and view details
4. Observe connection type: USB icon or WiFi icon

**Device Card Shows**:
- Device name / model
- Connection type (USB/WiFi)
- Battery percentage and status icon
- Connection status (Connected, Disconnected, Offline)

**Supported Connections**:
- **USB**: Direct USB cable connection (ADB over USB)
- **WiFi**: Wireless debugging (ADB over TCP/IP)

**Implementation**:
- Backend: `adb devices -l` (polled every 2 seconds)
- Frontend: React `DevicePanel` component, caches and updates UI
- IPC: `list-devices` channel

---

### 1.2 Connect via WiFi

**What it does**: Establish wireless ADB connection to a device using its IP address.

**How to use**:
1. From the menu, select "Add WiFi Device" or use the IP button
2. Enter device IP address (or use auto-discovery)
3. Click "Connect"
4. Device appears in device list within 2 seconds

**Modes**:
- **Manual IP**: Type device IP address directly
- **Auto-Discovery**: Scan network for nearby Android devices
- **TCP Setup**: Convert USB device to WiFi (enable ADB on port 5555)

**Prerequisites**:
- Device on same network as computer
- USB debugging enabled on device (for initial setup)
- Network connectivity between devices

**Implementation**:
- Backend: `adb connect <ip>:5555`
- Python auto-discovery: Ping sweep + ADB service detection
- Frontend: WiFi connection modal with input field

---

### 1.3 Device Details & Monitoring

**What it does**: Displays real-time hardware information and system stats.

**How to use**:
1. Select a device from the device list
2. View the **Device Details** panel
3. Hardware info displays automatically
4. Real-time metrics update every 3-5 seconds (configurable)

**Information Displayed**:

| Category | Details |
|----------|---------|
| **Hardware** | Model, Manufacturer, Device Name, CPU, Board |
| **Software** | Android Version, SDK, Build ID, Build Type, Build Date |
| **Storage** | Total/Used/Free (GB) with visual bar |
| **Memory** | Total/Used/Free RAM (GB) with usage graph |
| **Battery** | Current %, Temperature, Health (Good/Fair/Dead) |
| **Network** | Connected SSID, IP Address, Signal Strength |
| **Identifiers** | Device ID (serial), Product Name, Codename |

**Real-time Updates**:
- Battery: Updates every 3 seconds
- RAM/Storage: Updates every 5 seconds
- Network: On-demand (updated when changed)
- Hardware: Static (fetched once on device select)

**User Preferences**:
- Toggle auto-refresh on/off
- Adjust refresh rate (3s, 5s, 10s, manual)
- Clear update history

**Implementation**:
- Backend: `adb shell getprop`, `cat /proc/meminfo`, `df /sdcard`
- Frontend: React hooks for periodic polling
- Caching: Device properties cached until device re-selected

---

### 1.4 Device Actions

**What it does**: Perform device-level operations.

**Available Actions** (right-click device or via menu):
- **Reboot**: Restart device normally
- **Reboot to Bootloader**: For firmware updates
- **Reboot to Recovery**: For system recovery/factory reset
- **Disconnect WiFi**: Remove WiFi device from list (doesn't affect device)
- **Clear Cache**: Clear system cache partition

**Implementation**:
- Backend: `adb reboot`, `adb reboot bootloader`, `adb shell rm -rf /cache/*`
- Confirmation dialogs before destructive operations
- Error handling if device disconnects mid-operation

---

## 2. App Management

### 2.1 List Installed Apps

**What it does**: Display all installed applications with detailed information.

**How to use**:
1. Select a device
2. Navigate to **App Manager** tab
3. View list of installed apps with icons and details

**App Information Shown**:
- App name (display name from manifest)
- Package name (e.g., `com.example.app`)
- App icon (fetched from device)
- Version (version name from manifest)
- Size (total app + data size)
- Install date
- Badge: "System" if pre-installed

**Filtering & Search**:
- Search by app name or package name (real-time filter)
- Filter by: System apps, User-installed, Recently updated
- Sort by: Name, Size, Install Date

**Implementation**:
- Backend: `adb shell pm list packages -f` + manifest parsing
- App icons: Retrieved from `/data/app/` or system dir
- Caching: List cached per device, refreshed on-demand

---

### 2.2 Install App

**What it does**: Install APK files to a connected device.

**How to use**:
1. In App Manager, click **"Install App"** button
2. Either:
   - **Drag-drop** .apk file onto the panel
   - **Browse** file dialog and select .apk
3. Installation progress shown with bar
4. Confirmation when complete or error details if failed

**Features**:
- Supports single or batch install (multiple .apk files)
- Progress tracking: % complete, transfer speed, ETA
- Cancel during installation
- Auto-reinstall (overwrites existing app)

**Error Handling**:
- "App already installed": Option to uninstall first
- "Insufficient storage": Show required space vs available
- "Signature mismatch": Show error details
- "Installation failed": Detailed error logs

**Implementation**:
- Backend: `adb install <apk>` (with progress parsing)
- Frontend: Drag-drop zone, file picker
- Error logging: Captured stderr from ADB

---

### 2.3 Uninstall App

**What it does**: Remove app from device.

**How to use**:
1. Right-click app in list or select and click "Uninstall"
2. Confirmation dialog appears
3. Click "Uninstall" to confirm
4. App removed; list updates automatically

**Options**:
- Keep app data (if applicable)
- Remove system apps (dangerous, requires confirmation)

**Implementation**:
- Backend: `adb uninstall <package>`
- Confirmation UX prevents accidental removal

---

### 2.4 Clear App Data/Cache

**What it does**: Remove app-specific data or cache to free space/reset state.

**How to use**:
1. Right-click app → "Clear Cache" or "Clear Data"
2. App resumes default state on next launch

**Options**:
- **Clear Cache**: Safe, only removes temporary files
- **Clear Data**: Removes settings, databases, etc. (warning shown)

**Implementation**:
- Backend: `adb shell pm clear <package>`

---

### 2.5 Launch App

**What it does**: Start an app on the device.

**How to use**:
1. Double-click app in list or right-click → "Launch"
2. App starts on device (appears in foreground or background)

**Implementation**:
- Backend: `adb shell monkey -p <package> 1` or `adb shell am start`

---

## 3. File Manager

### 3.1 Device File Browser

**What it does**: Browse device file system and transfer files.

**How to use**:
1. Select a device
2. Navigate to **File Manager** tab
3. Left pane: PC file system
4. Right pane: Device storage

**Device Browsing**:
- Start at `/sdcard/` (user storage)
- Navigate to other directories: `/data/`, `/system/` (read-only)
- View file details: name, size, date modified, permissions
- Double-click folder to enter, back button to go up

**Supported Paths**:
- `/sdcard/` → User storage (read/write)
- `/data/` → App data (read-only, requires root for some)
- `/system/` → System files (read-only)
- `/cache/` → Cache partition (if accessible)
- `/Download/`, `/Pictures/`, `/Music/` → Standard directories

**Implementation**:
- Backend: `adb shell ls -la <path>`, `adb shell stat <file>`
- Recursive directory listings with pagination for large dirs

---

### 3.2 Download File from Device (Pull)

**What it does**: Copy files from device to PC.

**How to use**:
1. Right-click file in device browser → "Download" or "Save As"
2. Choose save location on PC
3. Progress bar shows transfer speed and ETA
4. Confirmation when complete

**Features**:
- Bulk download (select multiple files)
- Directory download (recursive)
- Resume interrupted transfers
- Speed throttling (optional, to prevent network saturation)

**Implementation**:
- Backend: `adb pull <remote> <local>` (with progress parsing)
- Progress: Bytes transferred / total size

---

### 3.3 Upload File to Device (Push)

**What it does**: Copy files from PC to device.

**How to use**:
1. In left (PC) pane, select file(s)
2. Drag-drop onto right (device) pane, or right-click → "Send to Device"
3. Choose destination folder on device
4. Progress bar shows transfer speed
5. Confirmation when complete

**Features**:
- Drag-drop for ease
- Bulk upload (multiple files)
- Directory upload (recursive)
- Overwrite confirmation if file exists

**Implementation**:
- Backend: `adb push <local> <remote>`
- Drag-drop IPC: File path validated for security (no traversal)

---

### 3.4 File Operations

**What it does**: Perform basic file operations on device.

**Available Operations**:
- **Delete**: Remove file or empty folder
- **Rename**: Change file name
- **Create Folder**: New directory
- **Copy**: Copy file (creates duplicate)

**Safety**:
- Confirmation before delete
- Cannot delete system files
- Cannot write to read-only paths

**Implementation**:
- Backend: `adb shell rm`, `adb shell mv`, `adb shell mkdir`

---

## 4. Logcat Viewer

### 4.1 Real-time Logs

**What it does**: Stream device system and app logs in real-time.

**How to use**:
1. Select a device
2. Navigate to **Logcat** tab
3. Logs stream automatically
4. Auto-scrolls to latest (toggle on/off)

**Log Entry Format**:
```
[12:34:56.789] I/Tag: Message (PID:1234 UID:1000)
```

**Columns**:
- Timestamp (HH:MM:SS.mmm)
- Log Level (V/D/I/W/E/F with color coding)
- Tag (usually package name or component)
- Message (log text)
- PID/UID (process and user ID)

**Implementation**:
- Backend: Persistent `adb logcat` process, streaming output
- Frontend: Ring buffer (10,000 lines max) to prevent memory bloat
- Real-time: IPC push (not polled) for low latency

---

### 4.2 Filtering

**What it does**: Filter logs to find relevant messages quickly.

**Available Filters**:

| Filter | Purpose | Example |
|--------|---------|---------|
| **Level** | Show only certain priority | Info, Warn, Error only |
| **Package** | Show logs from specific app | com.example.app |
| **Keyword** | Search log text | "Connection error" |
| **Time Range** | Logs from specific time | Last 5 minutes |
| **PID/UID** | Process/user filter | PID=1234 |

**Combining Filters**:
- Multiple filters work together (AND logic)
- Clear individual filters or reset all

**Implementation**:
- Frontend: Client-side filtering (fast, no server call)
- Regex support for advanced keyword search

---

### 4.3 Log Export

**What it does**: Save logs to file for analysis or sharing.

**How to use**:
1. Click **"Save Logs"** button
2. Choose save location and filename
3. Logs saved as `.txt` or `.csv` format
4. Option to include metadata (timestamps, PIDs, etc.)

**Formats**:
- **Plain text**: Human-readable, one log per line
- **CSV**: Excel-compatible, structured columns

**Implementation**:
- Export current buffer (10k lines) or full session
- Metadata: Device info, export timestamp, filters applied

---

### 4.4 Crash Log Analysis

**What it does**: Capture and display app crash logs.

**How to use**:
1. If app crashes on device, logcat shows error
2. **Crash Logs** tab shows recent crashes with stack traces
3. Click crash to expand full stack trace
4. Copy or save crash report

**Information**:
- App package name
- Exception type (NullPointerException, etc.)
- Stack trace (file, method, line number)
- Timestamp
- System info at time of crash

**Implementation**:
- Logcat parsing: Detect `FATAL EXCEPTION`, `AndroidRuntime`, keywords
- Stack trace extraction and formatting

---

## 5. Screenshots & Screen Recording

### 5.1 Screenshot

**What it does**: Capture device screen and save to PC.

**How to use**:
1. Navigate to **Screen** tab or click screenshot icon
2. Click **"Take Screenshot"** button
3. Image captured instantly
4. Automatically:
   - Saved to `~/adb-tools/screenshots/screenshot_<timestamp>.png`
   - Copied to clipboard
   - Shown in preview window

**Features**:
- One-click capture
- Auto-names by timestamp
- Quick share (copy to clipboard)
- Open in default image viewer

**Implementation**:
- Backend: `adb shell screencap -p /sdcard/screen.png` + `adb pull`
- Frontend: Display preview thumbnail

---

### 5.2 Screen Recording

**What it does**: Record device screen video.

**How to use**:
1. Click **"Start Recording"** button
2. Choose duration (10s, 30s, 60s, manual)
3. Click "Stop Recording" when done (or auto-stops at duration)
4. Video saved to `~/adb-tools/videos/video_<timestamp>.mp4`

**Features**:
- Configurable resolution (1080p, 720p, 480p)
- Bit rate control (10Mbps, 20Mbps, 40Mbps)
- Audio recording (if device supports)
- Auto-stop at duration or manual stop

**Implementation**:
- Backend: `adb shell screenrecord --time-limit=<duration> /sdcard/video.mp4`
- Pull video after recording completes

---

## 6. Shell Command Console

### 6.1 Command Execution

**What it does**: Execute arbitrary shell commands on the device.

**How to use**:
1. Navigate to **Shell** tab
2. Type command in input field (e.g., `ls /sdcard`)
3. Press Enter or click **Execute**
4. Output displays below

**Features**:
- Command history (arrow keys to navigate)
- Autocomplete suggestions (common ADB commands)
- Syntax highlighting for output
- Copy output to clipboard

**Examples**:
```bash
# List files
ls /sdcard

# Get device properties
getprop ro.build.version.release

# Kill an app
pkill -f com.example.app

# Clear app cache
pm clear com.example.app
```

**Implementation**:
- Backend: `adb shell <command>`
- Timeout: 10 seconds (user can cancel)
- Output line buffering for partial results

---

### 6.2 Command History

**What it does**: Keep history of executed commands.

**How to use**:
1. Click history icon or press Ctrl+H
2. View previous commands
3. Click to re-execute or edit

**Storage**:
- Last 50 commands stored in `~/.adb-tools/history.json`
- Per-device history (commands on Device A separate from Device B)

**Implementation**:
- Frontend: Local React state + file persistence

---

## 7. Advanced Features

### 7.1 System Properties

**What it does**: View and modify system properties.

**How to use**:
1. Navigate to **Advanced** → **Properties**
2. Search for property (e.g., `ro.build.version`)
3. View current value
4. Click to edit and apply (if writable)

**Safe Properties** (read-only by default):
- Build properties (`ro.build.*`)
- Device properties (`ro.product.*`)
- Android version properties

**Implementation**:
- Backend: `adb shell getprop`, `adb shell setprop`
- Write-protection on system properties

---

### 7.2 Process Management

**What it does**: View running processes and resource usage.

**How to use**:
1. **Advanced** → **Processes**
2. View all running processes with:
   - Process name and package
   - PID, UID, priority
   - Memory usage (RSS, VSS)
   - CPU usage (%)
3. Sort by memory or CPU
4. Right-click to kill process (dangerous, requires confirmation)

**Implementation**:
- Backend: `adb shell ps -aux`, `adb shell cat /proc/<pid>/stat`
- Real-time updates: Every 2 seconds (toggle on/off)

---

### 7.3 Network Info

**What it does**: Display device network configuration.

**How to use**:
1. **Advanced** → **Network**
2. View:
   - WiFi SSID and signal strength
   - IP address (IPv4, IPv6)
   - DNS servers
   - MAC address
   - Mobile network info (if applicable)

**Implementation**:
- Backend: `adb shell ifconfig`, `adb shell ip addr`, `adb shell getprop`

---

### 7.4 Memory Analysis

**What it does**: Detailed memory breakdown (RAM usage by app).

**How to use**:
1. **Advanced** → **Memory**
2. View:
   - Total / Used / Free RAM
   - Swap usage
   - Top memory consumers (apps)
   - Memory type breakdown (Native, Heap, Graphics, etc.)

**Implementation**:
- Backend: `adb shell dumpsys meminfo`, `/proc/meminfo`

---

## 8. Settings & Preferences

### 8.1 Preferences

**What it does**: Customize app behavior.

**Available Settings**:

| Setting | Options | Default |
|---------|---------|---------|
| **Theme** | Dark, Light | Dark |
| **Auto-refresh** | On/Off | On |
| **Refresh rate** | 3s, 5s, 10s, Manual | 5s |
| **Logcat buffer size** | 5k, 10k, 50k lines | 10k |
| **Auto-connect** | Last device on startup | Off |
| **Update notifications** | On/Off | On |

**Implementation**:
- Stored in `~/.adb-tools/config.json`
- Persisted across sessions

---

### 8.2 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Q` / `Cmd+Q` | Quit app |
| `Ctrl+,` / `Cmd+,` | Open Settings |
| `Ctrl+R` / `Cmd+R` | Refresh device list |
| `Ctrl+F` / `Cmd+F` | Search/Filter (context-aware) |
| `Ctrl+H` | Show command history |
| `Ctrl+L` | Clear console/logs |
| `Arrow Up/Down` | Navigate history |

---

## 9. Setup Wizard (First Run)

### 9.1 Dependency Check

**What it does**: Verify all required tools are available on first launch.

**How it works**:
1. App startup checks for ADB, scrcpy, Python libraries
2. If all OK → skip to main app
3. If missing → show wizard

**Wizard Screens**:
- Status: Shows what's missing
- Progress: Auto-installs missing components
- Complete: "Restart app" button
- App restarts, checks again, loads main UI

**Implementation**:
- Backend: Check binary availability and versions
- Frontend: React wizard component with progress

---

### 9.2 First-Time Setup

**What it does**: Guide new users through initial setup.

**Steps**:
1. Welcome screen
2. Check dependencies (automated)
3. Connection instructions (USB or WiFi)
4. Connect first device
5. Intro to main UI

**Implementation**:
- Conditional rendering in React (check if first-run flag exists)
- Skip button available (advanced users)

---

## 10. Update Checking

### 10.1 Auto Update Check

**What it does**: Check for newer versions of ADB/scrcpy.

**How it works**:
1. On app startup, async check against update server
2. If newer available, show notification: "Updates available"
3. User can click "Update Now" or "Later" or "Never" (per-version)
4. Download and install automatically
5. User prompted to restart app

**Update Server Response**:
```json
{
  "adb": { "version": "1.0.40", "url": "...", "checksum": "..." },
  "scrcpy": { "version": "2.4.1", "url": "...", "checksum": "..." }
}
```

**Implementation**:
- Async HTTP check (timeout: 3s)
- Fallback: Use bundled versions if server unreachable
- Checksum validation: SHA256 verification before install

---

## 11. Error Handling & Help

### 11.1 Error Messages

**What it does**: Clear, actionable error messages for common issues.

**Examples**:
- Device disconnected → "Device disconnected. Please reconnect."
- ADB timeout → "Operation timed out. Check device connection."
- File not found → "File not found on device. Check path."
- Storage full → "Device storage full (X GB needed). Free up space."

**Implementation**:
- All errors logged to `~/.adb-tools/logs/app.log`
- User can export logs for debugging

---

### 11.2 Help & Documentation

**What it does**: In-app help system.

**Features**:
- Help button on each feature panel
- Links to documentation
- Keyboard shortcut reference (F1)
- Tooltips on hover

**Implementation**:
- Markdown docs embedded or link to web docs

---

## Feature Matrix: Phases

| Feature | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|---------|---------|---------|---------|---------|
| Device List | ✓ | | | |
| WiFi Connection | ✓ | | | |
| Device Details | | ✓ | | |
| App List | | ✓ | | |
| App Install/Uninstall | | ✓ | | |
| File Manager | | ✓ | ✓ | |
| Logcat Viewer | | ✓ | | |
| Screenshots | | | ✓ | |
| Screen Recording | | | ✓ | |
| Shell Console | | | ✓ | |
| Advanced Features | | | ✓ | |
| Settings | ✓ | ✓ | ✓ | |
| Polish & Testing | | | | ✓ |

