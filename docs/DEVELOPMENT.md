# Development Guide

## Prerequisites

### System Requirements
- **Node.js**: v18+ (npm 9+)
- **Python**: 3.11+ (for backend scripts)
- **Git**: v2.0+
- **OS**: Windows 10+ or Linux (Ubuntu 20.04+, Fedora 38+, Arch)

### Optional
- **Android Device** or **Android Emulator** (for testing)
- **VS Code** with extensions: ESLint, Prettier, Python, TypeScript Vue Intellisense

---

## Project Structure

```
adb-tools/
├── src/
│   ├── main/                    # Electron main process
│   │   ├── index.ts             # App entry point
│   │   ├── ipc.ts               # IPC handler registration
│   │   ├── dependencies.ts       # Dependency checking
│   │   ├── python-bridge.ts      # Python subprocess management
│   │   └── updates.ts            # Update check logic
│   ├── renderer/                 # React frontend (Vite)
│   │   ├── App.tsx               # Root component
│   │   ├── components/           # React components
│   │   │   ├── DevicePanel.tsx
│   │   │   ├── AppManager.tsx
│   │   │   ├── FileManager.tsx
│   │   │   ├── LogcatViewer.tsx
│   │   │   └── ...
│   │   ├── pages/                # Page-level components
│   │   ├── hooks/                # Custom React hooks
│   │   ├── types/                # TypeScript type definitions
│   │   └── styles/               # Global and component styles (CSS-in-JS or Tailwind)
│   └── preload.ts                # Preload script (IPC bridge)
├── backend/
│   ├── adb_wrapper.py            # ADB command wrapper
│   ├── device_manager.py         # Device detection
│   ├── app_manager.py            # App management
│   ├── file_manager.py           # File transfer
│   ├── logcat_manager.py         # Logcat streaming
│   ├── main.py                   # Backend entry point
│   └── utils.py                  # Shared utilities
├── bin/
│   ├── windows/
│   │   ├── adb.exe
│   │   └── scrcpy.exe
│   └── linux/
│       ├── adb
│       └── scrcpy
├── docs/
│   ├── ARCHITECTURE.md           # System design
│   ├── DEVELOPMENT.md            # This file
│   ├── FEATURES.md               # Feature documentation
│   ├── API.md                    # IPC & Python API
│   ├── TESTING.md                # Testing guide
│   ├── DEPLOYMENT.md             # Build & release
│   └── superpowers/
│       └── specs/
│           └── 2026-07-03-adb-tools-desktop-modernization-design.md
├── tests/
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── public/                       # Static assets (icons, fonts)
├── package.json                  # Node dependencies and scripts
├── tsconfig.json                 # TypeScript config
├── vite.config.ts                # Vite config
├── electron-builder.yml          # Electron builder config
├── CLAUDE.md                     # Claude Code context
└── README.md                     # Project overview
```

---

## Getting Started

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/adb-tools.git
cd adb-tools
npm install
```

### 2. Setup Python Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 3. Run Development Build

```bash
# Terminal 1: Start Vite dev server + Electron
npm run dev

# Terminal 2 (if needed): Start Python backend manually
# (Usually auto-started by Electron main)
cd backend && python3 main.py
```

**Vite HMR**: When you edit React components, the app reloads automatically.

### 4. Connect a Device

```bash
# USB: Connect Android device, enable USB debugging
adb devices

# WiFi: After USB connection, run:
adb tcpip 5555
adb connect <device-ip>:5555
```

---

## Development Workflow

### Making Changes

#### Frontend (React)
1. Edit files in `src/renderer/components/`
2. Save → Vite hot-reloads the app
3. Test in running Electron window

#### Main Process (Electron)
1. Edit files in `src/main/`
2. Save → Webpack rebuilds, Electron auto-reloads main process
3. Renderer still runs (may need to refresh manually: Cmd+R or F5)

#### Backend (Python)
1. Edit files in `backend/`
2. Python subprocess reloads automatically on next IPC call (TBD: add file watch if needed)
3. Test in running app

#### Types (TypeScript)
1. Define types in `src/types/` or alongside components
2. Run `npm run type-check` to verify no errors
3. IDE provides real-time feedback

---

## Scripts

### Development

```bash
npm run dev           # Start dev server + Electron
npm run dev:main     # Dev server only (no Electron)
npm run dev:build    # Build for dev (no HMR)
```

### Testing

```bash
npm run test          # Run all tests
npm run test:watch    # Watch mode
npm run test:ui       # Vitest UI
npm run e2e           # Run E2E tests (requires Playwright)
```

### Type Checking & Linting

```bash
npm run type-check    # TypeScript validation
npm run lint          # ESLint + Prettier check
npm run lint:fix      # Auto-fix lint issues
```

### Building

```bash
npm run build         # Build dist (Electron + Python packaged)
npm run build:app     # Build Electron app only
npm run build:backend # Build Python dist (pip freezing, etc.)
```

### Packaging

```bash
npm run package       # Create installers (Windows .exe, Linux .AppImage)
npm run package:win   # Windows only
npm run package:linux # Linux only
```

---

## IPC Communication (Frontend ↔ Main)

### From React Component

```typescript
import { ipcRenderer } from 'electron';

// Simple command
const devices = await ipcRenderer.invoke('list-devices');

// With arguments
const info = await ipcRenderer.invoke('get-device-info', { deviceId: '...' });

// Stream (e.g., logcat)
ipcRenderer.on('logcat-line', (event, line) => {
  console.log(line);
});
ipcRenderer.send('start-logcat', { deviceId: '...' });
```

### From Main Process (IPC Handler)

```typescript
// In src/main/ipc.ts
ipcMain.handle('list-devices', async () => {
  const result = await pythonBridge.execute({
    cmd: 'list_devices'
  });
  return result.data;
});

ipcMain.on('start-logcat', (event, { deviceId }) => {
  pythonBridge.startLogcatStream(deviceId, (line) => {
    event.reply('logcat-line', line);
  });
});
```

**Convention**: Use kebab-case for channel names (`list-devices`), snake_case for Python commands (`list_devices`).

---

## Python Backend Commands

### Communication Protocol

Main ↔ Python: Line-delimited JSON

```json
{"cmd": "list_devices", "args": {}}
{"status": "success", "data": [...]}
```

### Examples

```python
# In backend/adb_wrapper.py
def list_devices():
    result = subprocess.run(['adb', 'devices', '-l'], ...)
    # Parse output, return list of device objects
    return [{'id': '...', 'model': '...', 'status': 'device'}, ...]

def push_file(local_path, remote_path, device_id):
    # Send file to device
    # Track progress: 10%, 20%, ... 100%
    # Return success status

def get_device_info(device_id):
    # Fetch hardware properties via adb shell getprop
    return {
        'model': '...',
        'android_version': '...',
        'ram': '...',
        ...
    }
```

See `docs/API.md` for full command reference.

---

## Debugging

### Electron DevTools

- **Main Process**: `Ctrl+Shift+I` (or `Cmd+Option+I` on Mac)
- **Renderer Process**: Right-click → Inspect (or F12)

### Debugging Python

```python
# In backend code
import logging
logging.debug(f"Device list: {devices}")
```

Logs appear in main terminal where you ran `npm run dev`.

### Logcat From Device

```bash
adb logcat -s ADB-Tools
```

---

## Common Development Tasks

### Adding a New Feature

1. **Design**: Sketch the component/data flow
2. **Create React component**: `src/renderer/components/NewFeature.tsx`
3. **Add IPC handler**: `src/main/ipc.ts` → `ipcMain.handle(...)`
4. **Add Python command**: `backend/new_feature.py`
5. **Test**: Connect device, test in app
6. **Commit**: `git commit -m "feat: add new feature"`

### Testing Device Interaction

```typescript
// In component test
import { ipcRenderer } from 'electron';

jest.mock('electron', () => ({
  ipcRenderer: {
    invoke: jest.fn()
  }
}));

test('loads device list', async () => {
  (ipcRenderer.invoke as jest.Mock).mockResolvedValue([
    { id: 'test123', model: 'TestDevice' }
  ]);
  
  // Test component...
});
```

### Adding a Python Dependency

```bash
cd backend
pip install <package>
pip freeze > requirements.txt
cd ..
git add backend/requirements.txt
```

---

## Environment Variables

Create `.env` (not committed) for local development:

```bash
VITE_API_URL=http://localhost:3000
DEBUG=adb-tools:*
PYTHON_PATH=/usr/bin/python3
```

In code:

```typescript
const apiUrl = import.meta.env.VITE_API_URL;
```

---

## Version Management

- **App Version**: `package.json` → `version` field
- **Backend Version**: `backend/version.py` or constant
- Update both when releasing

---

## Git Workflow

### Branching

```bash
git checkout -b feature/device-monitoring  # Feature
git checkout -b fix/logcat-crash           # Bug fix
git checkout -b docs/update-readme         # Docs
```

### Committing

```bash
git add src/renderer/components/NewFeature.tsx
git commit -m "feat: add device monitoring dashboard

- Real-time battery, RAM, storage monitoring
- Configurable refresh rates
- Performance optimized with debouncing"
```

### Pushing & PR

```bash
git push origin feature/device-monitoring
# Create PR on GitHub
# Request review
# Merge after approval
```

---

## Troubleshooting

### "Module not found" errors

```bash
npm install
npm run build  # Rebuild
```

### Python subprocess not starting

```bash
# Check Python path
which python3
# Or in code: print(sys.executable)
```

### Device not detected

```bash
adb kill-server
adb start-server
adb devices
```

### Vite HMR not working

```bash
# Kill Electron
# npm run dev
# May need to clear node_modules cache
rm -rf node_modules/.vite
npm install
```

### Port already in use (Dev server)

```bash
# Find process on port 5173
lsof -i :5173  # macOS/Linux
netstat -ano | findstr :5173  # Windows
# Kill it or change port in vite.config.ts
```

---

## Performance Considerations

- **Device list**: Cached, refreshed every 2 seconds (configurable)
- **Real-time monitoring**: Separate polling threads, don't block main
- **Logcat stream**: Ring buffer (10k lines max) to prevent memory leaks
- **File transfers**: Chunked I/O (not loaded into memory)
- **React rendering**: Memoize expensive components, use `useMemo` for derived state

---

## Code Style

- **TypeScript**: Strict mode enabled
- **Formatting**: Prettier (run `npm run lint:fix` to auto-format)
- **Naming**: camelCase for variables/functions, PascalCase for components/classes
- **Comments**: Only for non-obvious logic; most code should be self-documenting

---

## Resources

- **Electron Docs**: https://www.electronjs.org/docs
- **React Docs**: https://react.dev
- **TypeScript Docs**: https://www.typescriptlang.org/docs
- **Python ADB**: https://developer.android.com/studio/command-line/adb
- **scrcpy**: https://github.com/Genymobile/scrcpy

