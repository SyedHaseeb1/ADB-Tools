# Architecture Documentation

## System Overview

ADB-Tools Desktop is a modern Electron + React desktop application that provides a comprehensive Android device management interface. The system is designed with three distinct layers: presentation, orchestration, and execution.

```
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                      │
│  (React Components, UI State, User Interactions)         │
│  - Device Panel, App Manager, File Manager, etc.         │
└────────────────────┬────────────────────────────────────┘
                     │ IPC Messages
                     ↓
┌─────────────────────────────────────────────────────────┐
│               ORCHESTRATION LAYER                        │
│  (Electron Main, Dependency Management, Subprocess)      │
│  - Setup Wizard, Device Detection, Process Management    │
└────────────────────┬────────────────────────────────────┘
                     │ Subprocess Calls
                     ↓
┌─────────────────────────────────────────────────────────┐
│                EXECUTION LAYER                           │
│  (Python Backend, Bundled Tools, System Commands)        │
│  - ADB, scrcpy, Shell commands, File operations          │
└─────────────────────────────────────────────────────────┘
```

## Layer Details

### 1. Presentation Layer (React Frontend)

**Purpose**: User interface and state management

**Key Components**:
- `src/components/DevicePanel.tsx` — Device list, connection status
- `src/components/DeviceDetails.tsx` — Hardware info, real-time monitoring
- `src/components/AppManager.tsx` — Install, uninstall, launch apps
- `src/components/FileManager.tsx` — File transfer UI
- `src/components/LogcatViewer.tsx` — Real-time logs with filters
- `src/components/ScreenCapture.tsx` — Screenshots and recording
- `src/components/ShellConsole.tsx` — Command input and output
- `src/components/SetupWizard.tsx` — First-run dependency wizard

**State Management**:
- React Context API for global state (devices, settings, UI theme)
- Local component state for UI interactions
- Redux (optional future) if state complexity grows

**Communication**:
- IPC to main process via preload bridge
- Non-blocking async/await patterns
- Toast notifications for user feedback

---

### 2. Orchestration Layer (Electron Main)

**Purpose**: System interaction, dependency management, subprocess coordination

**Key Modules**:
- `src/main/index.ts` — Application entry point, window creation
- `src/main/ipc.ts` — IPC handler registration
- `src/main/dependencies.ts` — Dependency checking and installation
- `src/main/python-bridge.ts` — Python subprocess management
- `src/main/updates.ts` — Update checking and installation logic
- `src/main/device-monitor.ts` — Periodic device list polling
- `src/preload.ts` — Secure IPC bridge to renderer

**Key Responsibilities**:
- Launch and manage Electron windows
- Handle IPC messages from renderer → route to appropriate handler
- Spawn and manage Python subprocess
- Check/validate bundled dependencies on startup
- Monitor update server for newer versions
- Manage application lifecycle (quit, restart, minimize)

**Subprocess Management**:
- Single persistent Python process vs. spawn per-command (TBD during implementation)
- Communicate via stdin/stdout (line-delimited JSON)
- Timeout handling for long-running operations
- Resource cleanup on crash

---

### 3. Execution Layer (Python Backend)

**Purpose**: ADB command execution, file operations, data transformation

**Key Modules**:
- `backend/adb_wrapper.py` — Wrapper around ADB commands
- `backend/scrcpy_wrapper.py` — scrcpy integration
- `backend/device_manager.py` — Device detection and info retrieval
- `backend/app_manager.py` — App install/uninstall/list
- `backend/file_manager.py` — File transfer (push/pull)
- `backend/logcat_manager.py` — Logcat streaming
- `backend/command_executor.py` — Generic shell command runner
- `backend/utils.py` — Shared utilities (formatting, error handling)

**Command Protocol**:
```
Input (from main):  {"cmd": "list_devices", "args": {...}}
Output (to main):   {"status": "success", "data": {...}}
```

**Error Handling**:
- Subprocess return codes mapped to meaningful errors
- JSON response format ensures reliable parsing
- Timeout handling with graceful degradation

---

## Data Flow Examples

### Device List Update Flow
```
1. React: User opens Device Panel / clicks Refresh
2. React → IPC: {cmd: "list_devices"}
3. Main: Receives IPC, calls python_bridge.execute()
4. Main → Python: {cmd: "list_devices"}
5. Python → ADB: adb devices -l
6. Python → Main: {status: "success", data: [{id: "...", model: "..."}, ...]}
7. Main → React: {cmd: "device_list_updated", payload: [...]}
8. React: Updates device state, re-renders DevicePanel
```

### File Transfer Flow (Push)
```
1. React: User drag-drops file or browses and selects file
2. React → IPC: {cmd: "push_file", args: {local_path: "...", remote_path: "..."}}
3. Main: Validates paths, passes to Python with progress tracking
4. Main → Python: {cmd: "push_file", args: {...}}
5. Python → ADB: adb push <local> <remote> (with progress parsing)
6. Python → Main: {status: "success", progress: {...}}
7. Main → React: Progress updates (every 100KB or periodic)
8. React: Shows progress bar
9. When complete: React shows toast "File transferred successfully"
```

### Update Check Flow
```
1. Main: On startup, spawn async update check
2. Main → Update Server: GET https://api.adb-tools.com/releases/latest (timeout: 3s)
3. Update Server → Main: {adb: {version: "X", url: "...", checksum: "..."}, ...}
4. Main: Compare with bundled versions, store in memory
5. Main → React: {cmd: "update_available", payload: {adb: "1.0.40", ...}}
6. React: Show notification banner "Updates available"
7. User clicks "Update" → React → IPC → Main
8. Main: Download, verify checksum, backup old, replace, restart app
```

---

## Component Interaction Map

```
SetupWizard
  ├→ DependencyChecker (Python)
  ├→ ProgressMonitor
  └→ RestartPrompt

DevicePanel
  ├→ DeviceList (refreshed every 2s)
  ├→ DeviceCard (clickable → selects device)
  └→ ContextMenu (disconnect, reboot, etc.)

DeviceDetails (depends on selected device)
  ├→ HardwareInfo (fetched once on select)
  ├→ BatteryMonitor (refreshed every 3s)
  ├→ RAMMonitor (refreshed every 5s)
  ├→ StorageMonitor (refreshed every 5s)
  └→ NetworkInfo (refreshed on-demand)

AppManager (depends on selected device)
  ├→ AppList (fetched once, cached)
  ├→ AppCard (draggable, filterable)
  ├→ InstallDialog (drag-drop or file picker)
  └→ UninstallConfirm

FileManager (depends on selected device)
  ├→ PCBrowser (left pane, local files)
  ├→ DeviceBrowser (right pane, device storage)
  └→ TransferMonitor (progress, history)

LogcatViewer (depends on selected device)
  ├→ FilterBar (level, keyword, package)
  ├→ LogStream (real-time updates)
  └→ ExportDialog (save to file)

ScreenCapture
  ├→ ScreenshotButton (one-click, saves locally + clipboard)
  └→ RecordingDialog (start/stop, duration, save path)

ShellConsole
  ├→ CommandInput (with history, autocomplete)
  ├→ OutputDisplay (with copy, clear)
  └→ HistoryPanel (previous commands)

Settings/Menu
  ├→ Theme (dark/light toggle)
  ├→ DeviceHistory (list of connected devices)
  ├→ UpdateCheck (manual trigger)
  ├→ LogExport (download app logs)
  └→ About (version, license, links)
```

---

## Technology Choices & Rationale

| Component | Choice | Why |
|-----------|--------|-----|
| Desktop Framework | Electron | Cross-platform, mature ecosystem |
| UI Framework | React 18 | Component reusability, performance, large community |
| Language (Frontend) | TypeScript | Type safety, IDE support, fewer runtime errors |
| Backend | Python | Strong subprocess/OS integration, existing ADB tooling |
| IPC | Electron's built-in | Native, secure, no additional deps |
| State Management | Context API → Redux (if needed) | Start simple, upgrade if complex |
| Build Tool | Vite | Fast bundling, HMR support |
| Package Manager | npm | Standard, large ecosystem |
| Icons | Feather or Material Design Icons | Open-source, consistent |
| Theme | Dark (default) + Light option | Modern, reduces eye strain, aligns with design brief |

---

## Bundled Dependencies Rationale

**Why bundle instead of requiring system install?**
- **Zero friction onboarding**: User downloads app and clicks once
- **Version consistency**: Guarantees specific ADB version works as tested
- **Cross-platform simplicity**: No `apt install` / `brew install` commands
- **Offline capability**: Works without internet (except update checks)

**Trade-off**: Larger download size (~200-300MB), mitigated by:
- UPX compression of binaries
- OS-specific installers (Windows users don't get Linux binaries)
- Lazy-loading non-essential tools

---

## Concurrency & Performance

### Device List Polling
- Background thread/timer refreshes every 2 seconds
- Non-blocking: doesn't freeze UI
- Only updates UI if device list changed

### Real-time Monitoring (Battery, RAM, Storage)
- Separate polling threads per metric
- Configurable refresh rate (user preference: 3s, 5s, 10s, manual)
- Debounced updates to prevent UI thrashing

### Logcat Streaming
- Persistent Python subprocess with open logcat pipe
- Non-blocking IPC: new log lines pushed to UI (not polled)
- Ring buffer (last 10,000 lines) to prevent memory bloat

### File Transfer
- Progress updates sent from Python every 100KB or 500ms (whichever comes first)
- Non-blocking main thread
- Cancelable via IPC

---

## Error Handling & Resilience

### ADB Command Failures
- **Timeout (>10s)**: Show spinner, allow user to cancel
- **Device disconnected**: Toast "Device disconnected"; retry or reset
- **ADB binary missing**: Trigger setup wizard to repair
- **Invalid command**: Show stderr in UI, suggest fix

### Network Issues
- **Update check timeout**: Silently use bundled versions (no error shown)
- **File transfer interrupted**: Keep partial file, offer resume option
- **Logcat stream interrupted**: Show "connection lost"; auto-reconnect with exponential backoff

### Application Crashes
- **Python subprocess crash**: Log to file, show error modal, offer restart
- **Electron main crash**: Electron auto-relaunch (built-in)
- **React component error**: Error boundary catches, shows fallback UI

---

## Security Boundaries

1. **IPC Bridge**: Preload script whitelist allowed IPC channels
2. **File Operations**: Validate all file paths (prevent directory traversal)
3. **Subprocess Execution**: Always use `shell=False`, never pass user input unsanitized
4. **Network**: TLS for update checks, checksum verification for downloaded binaries
5. **No telemetry**: App doesn't phone home except update server

---

## Future Scalability Considerations

- **Horizontal scaling**: If app grows, split into modules (device mgmt, app mgmt, etc.)
- **Plugin system**: Allow user-defined ADB command helpers (future)
- **Web interface**: Python backend could be exposed as REST API for web dashboard
- **Mobile companion app**: Python backend + React Native frontend

