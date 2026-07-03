# ADB-Tools Desktop: Comprehensive Design Spec

**Date:** July 3, 2026  
**Status:** Design Phase  
**Author:** Claude Code + User  

## 1. Overview & Goals

### Vision
Transform ADB-Tools from a text-based CLI into a **modern, feature-rich desktop application** that brings comprehensive Android device management to both Windows and Linux users—with zero technical friction.

### Design Principles
1. **Non-technical user first** — Runs on double-click, zero setup hassle
2. **Bundled & isolated** — No external dependency hunting; everything included
3. **Smart but simple** — Optional updates available, but works offline
4. **Modern & beautiful** — Dark theme, icons, smooth UX; not clunky
5. **Comprehensive ADB** — Supports the full breadth of ADB capabilities

### Success Criteria
- User downloads app → double-clicks → works (within 2 clicks)
- All current features work + major new ones (file transfer, logs, screenshots)
- Cross-platform Windows & Linux with identical UX
- Non-technical users report easy/intuitive experience
- No dependency crashes or cryptic errors

---

## 2. Architecture

### Technology Stack
- **Desktop Shell:** Electron (v28+)
- **UI Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Package Manager:** npm
- **Backend:** Python 3.11+ (bundled)
- **IPC:** Electron main ↔ renderer via preload bridge

### High-Level Architecture

```
┌─────────────────────────────────────────────┐
│        Electron Main Process                 │
│ (Dependency checks, Python subprocess,       │
│  OS interaction, file system)                │
└────────────────┬────────────────────────────┘
                 │ IPC Bridge
                 ↓
┌─────────────────────────────────────────────┐
│      React Frontend (UI)                     │
│ (Setup wizard, device panel, logs viewer,    │
│  app manager, file manager, etc.)            │
└─────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────┐
│    Python Backend (ADB Orchestrator)         │
│ (Subprocess calls to bundled ADB/scrcpy)     │
└─────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────┐
│ Bundled Tools (ADB, scrcpy, Python libs)     │
└─────────────────────────────────────────────┘
```

### Data Flow
1. User interacts with React UI (e.g., "List Devices")
2. React sends IPC message to Electron main
3. Electron main spawns Python subprocess with command
4. Python subprocess calls bundled ADB/scrcpy
5. Output returns to Electron → React UI displays result
6. Real-time streams (logs, screen) use persistent IPC channels

---

## 3. Bundled Dependencies

### Windows Bundle
- **ADB**: Latest stable (bundled in `bin/windows/adb.exe`)
- **scrcpy**: Latest stable (bundled in `bin/windows/scrcpy.exe`)
- **Python 3.11**: Embedded runtime (in `runtime/windows/python/`)
- **Python packages**: colored, pyfiglet, requests (pre-installed)

### Linux Bundle
- **ADB**: Pre-compiled binary (bundled in `bin/linux/adb`)
- **scrcpy**: Pre-compiled binary (bundled in `bin/linux/scrcpy`)
- **Python 3.11**: System detection + fallback to bundled (in `runtime/linux/python/`)
- **Python packages**: Same as Windows

### Directory Structure (Post-Extract)
```
adb-tools/
├── app/                    # Electron + React app
├── bin/
│   ├── windows/           # Windows executables
│   └── linux/             # Linux binaries
├── runtime/
│   ├── windows/           # Embedded Python (Windows)
│   └── linux/             # Embedded Python (Linux)
├── resources/             # Icons, fonts
└── launcher.exe/.sh       # Entry points
```

---

## 4. Installation & Setup Flow

### Installer Strategy
**Windows**: NSIS installer (`adb-tools-setup.exe`)  
**Linux**: AppImage + deb package options

### Post-Install: First Run Checklist
1. **Extract/Copy** bundled resources to user app directory
2. **Create shortcuts** (Start Menu, Desktop, Application Launcher)
3. **Set permissions** (Linux: make binaries executable)
4. **Create config directories** (`~/.adb-tools/`, `~/.adb-tools/devices/`, etc.)

### Startup Sequence (Every Launch)
```
1. Main window opens → shows splash screen
2. Dependency check:
   - Is ADB bundled? ✓
   - Is scrcpy bundled? ✓
   - Python runtime available? (system or bundled)
   - Required Python packages installed?
3. If all OK → skip to step 5
4. If missing → Show setup wizard
   a. List what's missing
   b. Auto-install/verify
   c. Show progress bar
   d. "Restart app" button
   e. (User clicks → app restarts, re-checks)
5. Internet check: Try to reach update server
6. If reachable → check for library updates (async, non-blocking)
7. If updates available → show subtle notification in UI
8. Load main app

```

---

## 5. Setup Wizard (First-Run)

### Triggered When
- First app launch
- Dependencies detected as missing/corrupt
- User explicitly requests "Repair Installation"

### Flow
```
Screen 1: Welcome
  "ADB Tools Desktop is checking your system..."
  (Progress spinner)

Screen 2: Dependency Status
  ✓ ADB: Bundled version X.Y.Z
  ✓ scrcpy: Bundled version X.Y.Z
  ✓ Python: System version 3.11.x / Bundled 3.11.x
  ✓ Libraries: colored, pyfiglet, requests
  
Screen 3: Missing Dependencies (if any)
  "The following are needed:"
  - [ ] Install ADB update?
  - [ ] Install scrcpy update?
  - [ ] Install Python libraries?
  
  [Cancel] [Install All] buttons

Screen 4: Installation Progress
  Installing ADB...    [████████░░] 80%
  Installing scrcpy... [██░░░░░░░░] 20%
  Installing libs...   [██████████] 100%
  
  (Non-blocking; shows real-time progress)

Screen 5: Complete
  "All set! Ready to go."
  [Restart App] button
  
After restart → dependency check passes → Main app loads
```

---

## 6. Update Check Mechanism

### How It Works
1. **On startup** (async, non-blocking):
   - Ping update server (http-request with 3-second timeout)
   - Compare bundled versions (ADB, scrcpy) against latest
   - If newer available → store in app state

2. **Notification** (in UI):
   - Subtle banner in top-right: "Updates available"
   - User can click "Check for Updates" anytime from menu
   - Never forced; user fully controls timing

3. **Download & Install**:
   - User clicks "Update" → Progress window
   - Downloads new versions to temp dir
   - Verifies checksums (security)
   - Backs up old versions
   - Replaces binaries
   - Restarts app

4. **Fallback (No Internet)**:
   - Update check times out silently
   - App works with bundled versions (no warnings)
   - User never sees a failure

### Update Server Endpoint
```
GET https://api.adb-tools.com/releases/latest
Response: {
  "adb": { "version": "1.0.40", "url": "...", "checksum": "..." },
  "scrcpy": { "version": "2.4.1", "url": "...", "checksum": "..." }
}
```

---

## 7. Main Application Features

### 7.1 Device Panel
- **Real-time list** of connected devices (USB + WiFi)
- **Device cards** showing:
  - Device name / model
  - Connection type (USB icon / WiFi icon)
  - Battery percentage + icon
  - Connection status (connected, disconnected, offline)
- **Actions** (right-click or button):
  - Select device (highlights, shows details)
  - Disconnect WiFi device
  - Reboot
  - Reboot to bootloader/recovery

### 7.2 Device Details Panel
- **Hardware Info** (read-only):
  - Model, manufacturer, device name
  - Android version, SDK, build ID
  - CPU, RAM, storage
  - Codename, build tags
- **Real-time monitoring**:
  - Battery: % + temp + health
  - RAM: used/total + graph
  - Storage: used/total + graph
  - CPU usage (%)
  - Network info (WiFi SSID, IP)

### 7.3 App Manager
- **Installed Apps List**:
  - App name + icon + package name
  - App size, version, install date
  - System app badge
  - Search/filter by name or package
- **Actions**:
  - Launch app
  - Uninstall app
  - Clear app cache/data
  - View app info (permissions, storage, etc.)
- **Install App**:
  - Drag-drop .apk onto panel
  - Or browse file dialog
  - Shows install progress
  - Confirmation when done

### 7.4 File Manager
- **Two-pane view**: PC files (left) | Device storage (right)
- **Device side**:
  - Browse `/sdcard/`, `/data/`, `/system/` (with permissions)
  - View file details (size, date modified)
  - Download file (pull) to PC
  - Delete file
- **PC side**:
  - Browse local folders
  - Drag-drop to send files to device
  - Batch upload support

### 7.5 Logcat Viewer
- **Real-time log stream** from device
- **Filters**:
  - Log level (Verbose, Debug, Info, Warn, Error)
  - Package name / keyword search
  - Time range
- **Display options**:
  - Timestamp, process ID, priority, tag, message
  - Copy log text
  - Save log to file
  - Clear log
- **Auto-scroll** toggle

### 7.6 Screenshots & Recording
- **Screenshot button**: Captures device screen, saves to PC + clipboard
- **Screen Record button**: Records video (.mp4)
  - Specify duration
  - Auto-stop or manual stop
  - Save location

### 7.7 Shell Command Console
- **Command input** with autocomplete suggestions
- **Execute arbitrary shell commands** on device
- **Output display** with line numbers
- **History** (arrow keys to navigate)
- **Save output** to file

### 7.8 Advanced Features
- **System Properties**: View/search ro.* properties
- **Crash Logs**: View system crash logs
- **Memory Info**: Detailed memory breakdown
- **Process List**: Running processes + memory/CPU usage
- **Network**: Network stats, packet info
- **Settings**: Device settings viewer

---

## 8. UI/UX Design System

### Visual Language
- **Theme**: Dark mode (default), light mode (optional)
- **Color Palette**:
  - Primary: Accent color (e.g., electric blue #00D9FF)
  - Secondary: Softer tone (e.g., #6A7080)
  - Success: #00FF41
  - Warning: #FFB700
  - Error: #FF4444
  - Background: #0F1419
  - Surface: #1A1F26
- **Typography**: Clean sans-serif (system font: -apple-system, Segoe UI, sans-serif)
- **Icons**: Feather icons or Material Design Icons (open-source)
- **Spacing**: 8px base grid
- **Animations**: Smooth transitions (200-400ms), no jank

### Component Patterns
- **Device Cards**: Flat, subtle shadow on hover, click to select
- **Lists**: Virtual scrolling for 1000+ items
- **Buttons**: Primary (accent color), Secondary (ghost), Danger (red)
- **Modals**: Center-screen overlay with backdrop, close button
- **Notifications**: Toast in corner (auto-dismiss in 3s)
- **Progress**: Indeterminate spinner + % bar

### Navigation
- **Sidebar**: Main sections (Devices, Apps, Files, Logs, etc.)
- **Breadcrumb**: Current location in hierarchy (e.g., Device > Apps > Camera)
- **Context menu**: Right-click actions for items
- **Keyboard shortcuts**: Ctrl+Q (quit), Ctrl+, (settings), etc.

---

## 9. Data & State Management

### Local State
- **Device list**: Cached, refreshed every 2 seconds
- **Device details**: Refreshed on-demand or every 5 seconds (user toggle)
- **App list**: Cached per device, refreshed on-demand
- **Settings**: Saved to `~/.adb-tools/config.json`
  - Last selected device
  - Theme (dark/light)
  - Log filters
  - UI layout preferences

### Persistent Data
- **Device history**: `~/.adb-tools/devices.json` (connected devices + WiFi IPs)
- **File transfer history**: `~/.adb-tools/transfers.json`
- **Crash logs archive**: `~/.adb-tools/logs/` (for troubleshooting)

---

## 10. Error Handling & Recovery

### Common Failure Scenarios
| Scenario | Behavior |
|----------|----------|
| Device disconnected mid-operation | Toast: "Device disconnected"; retry button |
| ADB command timeout (>10s) | Show spinneR, allow cancel |
| File transfer interrupted | Partial file kept locally; offer resume |
| Update download fails | Show error; let user retry or skip |
| Python subprocess crash | Log to crash dir; show error; offer "Restart app" |
| Insufficient disk space | Toast warning; prevent large file transfers |

### Logging
- All operations logged to `~/.adb-tools/logs/app.log`
- ADB command output captured (for debugging)
- Crash dumps saved with timestamp
- User can export logs from Settings → Debug

---

## 11. Security Considerations

- **No credential storage**: ADB connection is stateless; credentials not persisted
- **File permissions**: Verify file paths to prevent directory traversal
- **Subprocess safety**: Use `subprocess.run()` with shell=False, validated args
- **Update verification**: SHA256 checksum validation before installing new binaries
- **No telemetry**: App doesn't phone home (except optional update check)

---

## 12. Testing Strategy

### Unit Tests
- Python ADB wrapper (mock subprocess)
- React components (React Testing Library)
- IPC message handlers

### Integration Tests
- Setup wizard flow with missing dependencies
- Device connection/disconnection
- File transfer (mock ADB)
- Logcat streaming

### E2E Tests
- Full app launch → device list → device details
- App installation (with real or emulated device)
- File transfer roundtrip

### Cross-Platform Tests
- Windows: Windows 10/11, Python 3.11+
- Linux: Ubuntu 20.04+, Fedora 38+, Arch

---

## 13. Implementation Phases

### Phase 1: Core Foundation (4-6 weeks)
- Electron + React scaffold
- Bundled dependencies (ADB, scrcpy)
- Setup wizard
- Dependency checking logic
- Device list & connection
- IPC bridge

### Phase 2: Essential Features (3-4 weeks)
- Device details panel (hardware info, monitoring)
- App manager (list, install, uninstall)
- Logcat viewer
- Basic file manager (pull files)

### Phase 3: Advanced Features (3-4 weeks)
- File transfer (push files)
- Screenshots & recording
- Shell command console
- Update check mechanism

### Phase 4: Polish & Release (2-3 weeks)
- UI refinement, accessibility audit
- Cross-platform testing
- Installer creation (NSIS, AppImage, deb)
- Documentation, help system

---

## 14. Success Metrics

- ✓ App launches on Windows/Linux without setup hassle
- ✓ Non-technical users rate UX as "intuitive" in testing
- ✓ All core features work (device list, app management, file transfer)
- ✓ Zero dependency-related crashes or errors
- ✓ App handles network failures gracefully (no crashes)
- ✓ Update mechanism works without user friction

---

## 15. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Bundle size too large (500MB+) | Compress with UPX, split for diff OS, lazy-load scrcpy |
| Python subprocess overhead | Use subprocess pooling, cache results where safe |
| Update logic breaks bundled versions | Backup old before install, verify checksums |
| Linux distro incompatibility | Test on Ubuntu, Fedora, Arch; provide AppImage |
| Electron startup slow | Use native modules for perf-critical paths |

---

## 16. Open Questions / TBD

- (None at this time; design is complete)

