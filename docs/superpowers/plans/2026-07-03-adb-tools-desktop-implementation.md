# ADB-Tools Desktop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modern, cross-platform Electron + React desktop application for Android device management with zero-friction setup and comprehensive feature set.

**Architecture:** Three-layer system (React frontend → Electron main orchestration → Python backend execution). Bundled dependencies (ADB, scrcpy, Python runtime) eliminate external setup. Setup wizard on first launch auto-detects and validates dependencies. IPC bridges frontend/main; JSON-RPC bridges main/Python.

**Tech Stack:** Electron 28+, React 18, TypeScript, Vite, Python 3.11, pytest, Vitest, Playwright

## Global Constraints

- **Platforms:** Windows 10+ and Linux (Ubuntu 20.04+, Fedora 38+, Arch)
- **Target User:** Non-technical; should work on double-click
- **Bundled Tools:** ADB, scrcpy, Python runtime (included in installers)
- **Node.js:** v18+, npm 9+
- **Python:** 3.11+ (bundled or system)
- **UI Theme:** Dark mode default, light mode optional
- **Update Checking:** Optional, non-forced (fails gracefully if no internet)
- **Performance:** Device list refresh every 2s, real-time streams (logs) via IPC push
- **Testing:** Unit (80%+ coverage), Integration (60%+), E2E (critical user flows)
- **Release Format:** Windows (NSIS installer + portable), Linux (AppImage + deb)

---

# Phase 1: Core Foundation (Weeks 1-6)

## Phase 1 File Structure

```
src/
├── main/                          # Electron main process
│   ├── index.ts                   # App entry point, window creation
│   ├── ipc.ts                     # IPC handler registration
│   ├── dependencies.ts            # Dependency checking logic
│   ├── python-bridge.ts           # Python subprocess management
│   ├── updates.ts                 # Update checking (stub for Phase 3)
│   └── device-monitor.ts          # Device list polling (stub)
├── renderer/                      # React frontend
│   ├── App.tsx                    # Root component
│   ├── components/
│   │   ├── SetupWizard.tsx        # First-run dependency wizard
│   │   ├── DevicePanel.tsx        # Device list display
│   │   ├── MainLayout.tsx         # Overall layout shell
│   │   └── LoadingSpinner.tsx     # Loading indicator
│   ├── hooks/
│   │   ├── useDeviceList.ts       # Custom hook for device polling
│   │   └── useIpc.ts              # IPC communication helper
│   ├── types/
│   │   ├── device.ts              # Device type definitions
│   │   ├── ipc.ts                 # IPC message types
│   │   └── settings.ts            # App settings types
│   └── styles/
│       ├── global.css             # Global styles + dark theme
│       └── components.css         # Component-specific styles
├── preload.ts                     # Secure IPC bridge
├── vite.config.ts                 # Vite bundler config
├── tsconfig.json                  # TypeScript config
└── electron-builder.yml           # Electron installer config

backend/
├── main.py                        # Backend entry point (JSON-RPC loop)
├── adb_wrapper.py                 # ADB command wrapper
├── device_manager.py              # Device detection + info
├── command_executor.py            # Generic shell command runner
├── utils.py                       # Shared utilities
├── version.py                     # Version constant
└── requirements.txt               # Python dependencies

bin/
├── windows/
│   ├── adb.exe
│   └── scrcpy.exe
└── linux/
    ├── adb
    └── scrcpy

tests/
├── unit/
│   ├── components/
│   │   └── DevicePanel.test.tsx
│   ├── hooks/
│   │   └── useDeviceList.test.ts
│   └── main/
│       ├── ipc.test.ts
│       └── python-bridge.test.ts
└── integration/
    └── device-connection.test.ts

public/
├── icon.png                       # App icon
└── logo.png                       # Splash logo
```

---

## Phase 1 Tasks

### Task 1.1: Initialize Electron + React Project Scaffold

**Files:**
- Create: `package.json`
- Create: `src/main/index.ts`
- Create: `src/renderer/App.tsx`
- Create: `src/vite.config.ts`
- Create: `tsconfig.json`
- Create: `.gitignore`

**Interfaces:**
- Produces: Working Electron app window, Vite dev server integration, React component mount point

**Steps:**

- [ ] **Step 1: Initialize npm project**

```bash
cd /home/syedhaseeaio/git/ADB-Tools
npm init -y
```

- [ ] **Step 2: Install core dependencies**

```bash
npm install --save \
  electron \
  react \
  react-dom \
  typescript

npm install --save-dev \
  vite \
  @vitejs/plugin-react \
  ts-node \
  electron-builder \
  @types/react \
  @types/react-dom \
  @types/node
```

- [ ] **Step 3: Create package.json scripts**

```json
{
  "name": "adb-tools",
  "version": "1.0.0",
  "main": "dist/main.js",
  "scripts": {
    "dev": "vite && electron .",
    "build": "vite build && tsc src/main/index.ts --outDir dist",
    "type-check": "tsc --noEmit",
    "test": "vitest",
    "test:watch": "vitest --watch",
    "package": "electron-builder"
  },
  "dependencies": {
    "electron": "^28.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "electron-builder": "^24.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

- [ ] **Step 4: Create TypeScript config**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "resolveJsonModule": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "build"]
}
```

- [ ] **Step 5: Create Vite config**

```typescript
// src/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    open: false,
  },
  build: {
    outDir: 'dist/renderer',
    emptyOutDir: true,
  },
});
```

- [ ] **Step 6: Create Electron main entry point**

```typescript
// src/main/index.ts
import { app, BrowserWindow } from 'electron';
import path from 'path';
import isDev from 'electron-is-dev';

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  const isDevelopment = process.env.NODE_ENV === 'development';
  const startUrl = isDevelopment
    ? 'http://localhost:5173'
    : `file://${path.join(__dirname, '../renderer/index.html')}`;

  mainWindow.loadURL(startUrl);

  if (isDevelopment) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
```

- [ ] **Step 7: Create React root component**

```typescript
// src/renderer/App.tsx
import React from 'react';
import './App.css';

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>ADB Tools</h1>
      </header>
      <main className="app-main">
        <p>Initializing...</p>
      </main>
    </div>
  );
}
```

- [ ] **Step 8: Create index.html**

```html
<!-- src/renderer/index.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ADB Tools</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/renderer/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 9: Create React entry point**

```typescript
// src/renderer/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 10: Create .gitignore**

```
node_modules/
dist/
build/
*.log
.DS_Store
.env.local
.vscode/
.idea/
venv/
__pycache__/
*.pyc
```

- [ ] **Step 11: Verify scaffold builds**

```bash
npm run type-check
# Expected: No errors

npm run build
# Expected: dist/ directory created with main.js and renderer files
```

- [ ] **Step 12: Commit**

```bash
git add package.json src/ tsconfig.json .gitignore
git commit -m "feat: initialize Electron + React scaffold

- Electron 28 with React 18 and TypeScript
- Vite dev server with HMR
- Basic app window with React component mount
- Ready for IPC and backend integration"
```

---

### Task 1.2: Create Secure IPC Bridge (Preload + Types)

**Files:**
- Create: `src/preload.ts`
- Create: `src/types/ipc.ts`
- Create: `src/renderer/hooks/useIpc.ts`

**Interfaces:**
- Consumes: Electron app from Task 1.1
- Produces: `ipcRenderer.invoke()` and `ipcRenderer.on()` helpers; `IpcChannels` type definitions

**Steps:**

- [ ] **Step 1: Create IPC type definitions**

```typescript
// src/types/ipc.ts
export type IpcChannel = 
  | 'list-devices'
  | 'connect-wifi'
  | 'get-device-info'
  | 'start-logcat'
  | 'stop-logcat'
  | 'check-dependencies'
  | 'update-available'
  | 'device-connected'
  | 'device-disconnected';

export interface IpcRequest {
  cmd: string;
  args?: Record<string, any>;
}

export interface IpcResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  error?: string;
}

export interface Device {
  id: string;
  model: string;
  manufacturer: string;
  status: 'device' | 'offline' | 'unauthorized';
  connection_type: 'usb' | 'wifi';
  battery?: number;
}
```

- [ ] **Step 2: Create preload script**

```typescript
// src/preload.ts
import { contextBridge, ipcRenderer } from 'electron';

// Whitelist allowed IPC channels
const ALLOWED_CHANNELS = {
  invoke: [
    'list-devices',
    'connect-wifi',
    'get-device-info',
    'check-dependencies',
  ],
  on: [
    'update-available',
    'device-connected',
    'device-disconnected',
  ],
};

const ipc = {
  invoke: (channel: string, ...args: any[]) => {
    if (!ALLOWED_CHANNELS.invoke.includes(channel)) {
      throw new Error(`Unauthorized IPC channel: ${channel}`);
    }
    return ipcRenderer.invoke(channel, ...args);
  },
  on: (channel: string, listener: (event: any, ...args: any[]) => void) => {
    if (!ALLOWED_CHANNELS.on.includes(channel)) {
      throw new Error(`Unauthorized IPC channel: ${channel}`);
    }
    return ipcRenderer.on(channel, listener);
  },
  off: (channel: string, listener: (event: any, ...args: any[]) => void) => {
    return ipcRenderer.off(channel, listener);
  },
};

contextBridge.exposeInMainWorld('electron', { ipc });

declare global {
  interface Window {
    electron: typeof ipc;
  }
}
```

- [ ] **Step 3: Create useIpc hook**

```typescript
// src/renderer/hooks/useIpc.ts
import { useCallback } from 'react';

export function useIpc() {
  const invoke = useCallback(async (channel: string, args?: any) => {
    return window.electron.ipc.invoke(channel, args);
  }, []);

  const on = useCallback((channel: string, handler: (data: any) => void) => {
    const listener = (_event: any, data: any) => handler(data);
    window.electron.ipc.on(channel, listener);
    return () => window.electron.ipc.off(channel, listener);
  }, []);

  return { invoke, on };
}
```

- [ ] **Step 4: Update preload import in main/index.ts**

```typescript
// src/main/index.ts (update webPreferences)
webPreferences: {
  preload: path.join(__dirname, '../preload.js'),
  nodeIntegration: false,
  contextIsolation: true,
}
```

- [ ] **Step 5: Type-check**

```bash
npm run type-check
# Expected: No errors
```

- [ ] **Step 6: Commit**

```bash
git add src/preload.ts src/types/ipc.ts src/renderer/hooks/useIpc.ts
git commit -m "feat: add secure IPC bridge with type safety

- Preload script with whitelist of allowed channels
- TypeScript definitions for IPC requests/responses
- useIpc custom hook for React components
- Context isolation prevents unauthorized access"
```

---

### Task 1.3: Initialize Python Backend with JSON-RPC Protocol

**Files:**
- Create: `backend/main.py`
- Create: `backend/command_executor.py`
- Create: `backend/utils.py`
- Create: `backend/version.py`
- Create: `backend/requirements.txt`

**Interfaces:**
- Produces: Python subprocess responding to JSON-RPC commands; `execute_command(cmd, args)` entry point

**Steps:**

- [ ] **Step 1: Create Python requirements**

```
# backend/requirements.txt
colored==2.1.1
pyfiglet==0.8.0
requests==2.31.0
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-mock==3.11.0
```

- [ ] **Step 2: Create backend version file**

```python
# backend/version.py
VERSION = "1.0.0"
```

- [ ] **Step 3: Create utility functions**

```python
# backend/utils.py
import json
import sys
import logging
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_response(request_id: int, status: str, data: Any = None, error: Optional[str] = None) -> None:
    """Send JSON-RPC response to main process via stdout"""
    response = {
        "id": request_id,
        "status": status,
    }
    if data is not None:
        response["data"] = data
    if error is not None:
        response["error"] = error
    
    print(json.dumps(response), flush=True)

def send_progress(request_id: int, progress: int, message: str) -> None:
    """Send progress update during long-running operation"""
    response = {
        "id": request_id,
        "status": "progress",
        "progress": progress,
        "message": message,
    }
    print(json.dumps(response), flush=True)

def read_request() -> Optional[Dict[str, Any]]:
    """Read JSON-RPC request from stdin"""
    try:
        line = sys.stdin.readline().strip()
        if not line:
            return None
        return json.loads(line)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return None
```

- [ ] **Step 4: Create generic command executor**

```python
# backend/command_executor.py
import subprocess
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def execute_shell_command(command: str, device_id: Optional[str] = None, timeout: int = 10) -> Tuple[str, str, int]:
    """
    Execute shell command via adb (if device_id) or directly
    
    Returns: (stdout, stderr, exit_code)
    """
    try:
        if device_id:
            cmd = ['adb', '-s', device_id, 'shell', command]
        else:
            cmd = command.split()
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Command timeout after {timeout}s", 1
    except Exception as e:
        return "", str(e), 1
```

- [ ] **Step 5: Create main backend entry point**

```python
# backend/main.py
import json
import sys
import logging
from typing import Any, Dict, Optional
from command_executor import execute_shell_command
from utils import send_response, send_progress, read_request, logger

def handle_list_devices() -> Dict[str, Any]:
    """List all connected devices"""
    stdout, stderr, code = execute_shell_command("adb devices -l")
    
    if code != 0:
        return {"error": f"adb error: {stderr}"}
    
    devices = []
    for line in stdout.strip().split('\n')[1:]:  # Skip header
        if line.strip() and 'device' in line:
            parts = line.split()
            device_id = parts[0]
            status = parts[1]
            
            devices.append({
                "id": device_id,
                "status": status,
                "connection_type": "usb" if ":" not in device_id else "wifi",
                "model": "Unknown",  # Will be fetched in Phase 2
            })
    
    return {"devices": devices}

def handle_check_dependencies() -> Dict[str, Any]:
    """Check if required binaries (adb, scrcpy) are available"""
    import os
    import platform
    
    # For Phase 1, just check if we can run adb
    stdout, stderr, code = execute_shell_command("adb version")
    adb_available = code == 0
    
    return {
        "adb_available": adb_available,
        "platform": platform.system(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

def process_command(request: Dict[str, Any]) -> None:
    """Process a single IPC request"""
    request_id = request.get("id", -1)
    cmd = request.get("cmd")
    args = request.get("args", {})
    
    try:
        if cmd == "list_devices":
            result = handle_list_devices()
            send_response(request_id, "success", result)
        
        elif cmd == "check_dependencies":
            result = handle_check_dependencies()
            send_response(request_id, "success", result)
        
        else:
            send_response(request_id, "error", error=f"Unknown command: {cmd}")
    
    except Exception as e:
        logger.exception("Command error")
        send_response(request_id, "error", error=str(e))

def main():
    """Main event loop: read requests, process, send responses"""
    logger.info("ADB Tools backend starting")
    
    while True:
        try:
            request = read_request()
            if request is None:
                continue
            
            process_command(request)
        
        except KeyboardInterrupt:
            logger.info("Backend shutting down")
            break
        except Exception as e:
            logger.exception("Unexpected error")

if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Install Python dependencies**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

- [ ] **Step 7: Test backend manually (quick smoke test)**

```bash
cd backend
python3 main.py << 'EOF'
{"id": 1, "cmd": "list_devices", "args": {}}
{"id": 2, "cmd": "check_dependencies", "args": {}}
EOF
# Expected output:
# {"id": 1, "status": "success", "data": {"devices": [...]}}
# {"id": 2, "status": "success", "data": {"adb_available": true, ...}}
```

- [ ] **Step 8: Commit**

```bash
git add backend/main.py backend/command_executor.py backend/utils.py backend/version.py backend/requirements.txt
git commit -m "feat: initialize Python backend with JSON-RPC

- Main event loop reads JSON-RPC requests from stdin
- Command executor runs adb shell commands
- Utility functions for request/response serialization
- Initial commands: list_devices, check_dependencies
- Ready for Electron main process bridge"
```

---

### Task 1.4: Create Python Bridge in Electron Main Process

**Files:**
- Create: `src/main/python-bridge.ts`
- Modify: `src/main/index.ts`

**Interfaces:**
- Consumes: Python backend from Task 1.3
- Produces: `PythonBridge` class with `execute(cmd, args)` method

**Steps:**

- [ ] **Step 1: Create Python bridge class**

```typescript
// src/main/python-bridge.ts
import { spawn, ChildProcess } from 'child_process';
import { app } from 'electron';
import path from 'path';
import { EventEmitter } from 'events';

interface PendingRequest {
  resolve: (value: any) => void;
  reject: (reason?: any) => void;
  timeout: NodeJS.Timeout;
}

export class PythonBridge extends EventEmitter {
  private pythonProcess: ChildProcess | null = null;
  private requestId = 0;
  private pendingRequests: Map<number, PendingRequest> = new Map();
  private responseBuffer = '';

  async start(): Promise<void> {
    // Get Python executable path (bundled or system)
    const pythonExe = this.getPythonPath();
    const backendPath = path.join(app.getAppPath(), 'backend', 'main.py');

    this.pythonProcess = spawn(pythonExe, [backendPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: path.join(app.getAppPath(), 'backend'),
    });

    this.pythonProcess.stdout!.on('data', (data) => this.handleData(data));
    this.pythonProcess.stderr!.on('data', (data) => console.error(`[Python stderr] ${data}`));
    this.pythonProcess.on('error', (error) => console.error('Python process error:', error));
    this.pythonProcess.on('exit', (code) => {
      console.log(`Python process exited with code ${code}`);
      this.pythonProcess = null;
    });
  }

  async execute(cmd: string, args: Record<string, any> = {}): Promise<any> {
    if (!this.pythonProcess) {
      throw new Error('Python backend not running');
    }

    const requestId = ++this.requestId;
    const request = JSON.stringify({ id: requestId, cmd, args });

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pendingRequests.delete(requestId);
        reject(new Error(`Request ${requestId} timeout`));
      }, 30000); // 30 second timeout

      this.pendingRequests.set(requestId, { resolve, reject, timeout });
      this.pythonProcess!.stdin!.write(request + '\n');
    });
  }

  private handleData(data: Buffer): void {
    this.responseBuffer += data.toString();

    // Process complete lines (newline-delimited JSON)
    const lines = this.responseBuffer.split('\n');
    this.responseBuffer = lines.pop() || ''; // Keep incomplete line

    for (const line of lines) {
      if (line.trim()) {
        try {
          const response = JSON.parse(line);
          this.handleResponse(response);
        } catch (error) {
          console.error('Failed to parse Python response:', line, error);
        }
      }
    }
  }

  private handleResponse(response: any): void {
    const { id, status, data, error } = response;
    const pending = this.pendingRequests.get(id);

    if (!pending) {
      console.warn(`Received response for unknown request ${id}`);
      return;
    }

    if (status === 'progress') {
      // Emit progress event but don't resolve yet
      this.emit(`progress-${id}`, data);
      return;
    }

    clearTimeout(pending.timeout);
    this.pendingRequests.delete(id);

    if (status === 'success') {
      pending.resolve(data);
    } else {
      pending.reject(new Error(error || 'Unknown error'));
    }
  }

  private getPythonPath(): string {
    // TODO: Implement bundled Python detection
    // For now, use system python
    return process.platform === 'win32' ? 'python' : 'python3';
  }

  stop(): void {
    if (this.pythonProcess) {
      this.pythonProcess.kill();
      this.pythonProcess = null;
    }
  }
}

export const pythonBridge = new PythonBridge();
```

- [ ] **Step 2: Update main/index.ts to start Python bridge**

```typescript
// src/main/index.ts (add imports)
import { pythonBridge } from './python-bridge';

// src/main/index.ts (update app.on('ready'))
app.on('ready', async () => {
  await pythonBridge.start();
  createWindow();
});

// src/main/index.ts (update window-all-closed)
app.on('window-all-closed', () => {
  pythonBridge.stop();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
```

- [ ] **Step 3: Create unit test for Python bridge**

```typescript
// tests/unit/main/python-bridge.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { PythonBridge } from '@/main/python-bridge';
import { spawn } from 'child_process';

vi.mock('child_process');

describe('PythonBridge', () => {
  let bridge: PythonBridge;

  beforeEach(() => {
    bridge = new PythonBridge();
  });

  afterEach(() => {
    bridge.stop();
  });

  it('sends command and receives response', async () => {
    const mockProcess = {
      stdin: { write: vi.fn() },
      stdout: { on: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn(),
      kill: vi.fn(),
    };

    vi.mocked(spawn).mockReturnValue(mockProcess as any);

    await bridge.start();

    // Simulate async execute
    const promise = bridge.execute('list_devices', {});

    // Simulate response from Python
    const responseHandler = vi.mocked(mockProcess.stdout.on).mock.calls.find(
      (call) => call[0] === 'data'
    )?.[1] as any;

    setTimeout(() => {
      responseHandler(Buffer.from('{"id": 1, "status": "success", "data": {"devices": []}}\n'));
    }, 10);

    const result = await promise;
    expect(result).toEqual({ devices: [] });
  });

  it('rejects on timeout', async () => {
    const mockProcess = {
      stdin: { write: vi.fn() },
      stdout: { on: vi.fn() },
      stderr: { on: vi.fn() },
      on: vi.fn(),
      kill: vi.fn(),
    };

    vi.mocked(spawn).mockReturnValue(mockProcess as any);
    await bridge.start();

    const promise = bridge.execute('list_devices', {});

    // Don't send response, should timeout
    await expect(promise).rejects.toThrow('timeout');
  });
});
```

- [ ] **Step 4: Run test**

```bash
npm run test -- python-bridge.test.ts
# Expected: PASS
```

- [ ] **Step 5: Commit**

```bash
git add src/main/python-bridge.ts tests/unit/main/python-bridge.test.ts
git commit -m "feat: create Python bridge for Electron main process

- Spawns Python subprocess on app startup
- Sends JSON-RPC requests via stdin
- Handles streaming responses via stdout
- Request/response pairing with timeout handling
- Stops Python process on app quit"
```

---

### Task 1.5: Create Dependency Checking Logic

**Files:**
- Create: `src/main/dependencies.ts`
- Modify: `src/main/index.ts`

**Interfaces:**
- Consumes: `pythonBridge.execute()` from Task 1.4
- Produces: `DependencyChecker` class with `check()` and `repair()` methods

**Steps:**

- [ ] **Step 1: Create dependency checker**

```typescript
// src/main/dependencies.ts
import { pythonBridge } from './python-bridge';
import fs from 'fs';
import path from 'path';
import { app } from 'electron';

export interface DependencyStatus {
  python_available: boolean;
  adb_available: boolean;
  scrcpy_available: boolean;
  all_available: boolean;
}

export class DependencyChecker {
  async check(): Promise<DependencyStatus> {
    try {
      const result = await pythonBridge.execute('check_dependencies', {});
      
      return {
        python_available: true, // If we get a response, Python is working
        adb_available: result.adb_available ?? false,
        scrcpy_available: result.scrcpy_available ?? false,
        all_available: result.adb_available && result.scrcpy_available,
      };
    } catch (error) {
      console.error('Dependency check failed:', error);
      return {
        python_available: false,
        adb_available: false,
        scrcpy_available: false,
        all_available: false,
      };
    }
  }

  async repair(): Promise<{ success: boolean; message: string }> {
    // TODO: Implement actual repair logic (download/install binaries)
    // For Phase 1, just check what's needed
    const status = await this.check();
    
    if (status.all_available) {
      return { success: true, message: 'All dependencies available' };
    }

    return {
      success: false,
      message: `Missing: ${!status.adb_available ? 'ADB ' : ''}${!status.scrcpy_available ? 'scrcpy' : ''}`,
    };
  }

  isFirstRun(): boolean {
    // Check if config file exists
    const configPath = this.getConfigPath();
    return !fs.existsSync(configPath);
  }

  markSetupComplete(): void {
    const configPath = this.getConfigPath();
    const configDir = path.dirname(configPath);
    
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }

    fs.writeFileSync(configPath, JSON.stringify({ setupVersion: 1 }));
  }

  private getConfigPath(): string {
    const userDataPath = app.getPath('userData');
    return path.join(userDataPath, 'setup.json');
  }
}

export const dependencyChecker = new DependencyChecker();
```

- [ ] **Step 2: Create unit test**

```typescript
// tests/unit/main/dependencies.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DependencyChecker } from '@/main/dependencies';
import { pythonBridge } from '@/main/python-bridge';

vi.mock('@/main/python-bridge', () => ({
  pythonBridge: {
    execute: vi.fn(),
  },
}));

describe('DependencyChecker', () => {
  let checker: DependencyChecker;

  beforeEach(() => {
    checker = new DependencyChecker();
  });

  it('reports all dependencies available', async () => {
    vi.mocked(pythonBridge.execute).mockResolvedValue({
      adb_available: true,
      scrcpy_available: true,
    });

    const status = await checker.check();

    expect(status.adb_available).toBe(true);
    expect(status.scrcpy_available).toBe(true);
    expect(status.all_available).toBe(true);
  });

  it('reports missing dependencies', async () => {
    vi.mocked(pythonBridge.execute).mockResolvedValue({
      adb_available: false,
      scrcpy_available: true,
    });

    const status = await checker.check();

    expect(status.adb_available).toBe(false);
    expect(status.all_available).toBe(false);
  });

  it('handles check failure gracefully', async () => {
    vi.mocked(pythonBridge.execute).mockRejectedValue(new Error('Backend offline'));

    const status = await checker.check();

    expect(status.python_available).toBe(false);
    expect(status.all_available).toBe(false);
  });
});
```

- [ ] **Step 3: Run test**

```bash
npm run test -- dependencies.test.ts
# Expected: PASS
```

- [ ] **Step 4: Commit**

```bash
git add src/main/dependencies.ts tests/unit/main/dependencies.test.ts
git commit -m "feat: add dependency checking logic

- Check adb, scrcpy, Python availability via backend
- Mark first-run setup completion in config
- Graceful failure if backend offline
- Ready for setup wizard in next task"
```

---

### Task 1.6: Create Setup Wizard Component

**Files:**
- Create: `src/renderer/components/SetupWizard.tsx`
- Create: `src/renderer/hooks/useDependencies.ts`
- Modify: `src/renderer/App.tsx`

**Interfaces:**
- Consumes: IPC channel `check-dependencies`
- Produces: `<SetupWizard />` component; `useDependencies()` hook

**Steps:**

- [ ] **Step 1: Create dependency checking hook**

```typescript
// src/renderer/hooks/useDependencies.ts
import { useState, useCallback } from 'react';
import { useIpc } from './useIpc';

export interface DependencyStatus {
  python_available: boolean;
  adb_available: boolean;
  scrcpy_available: boolean;
  all_available: boolean;
}

export function useDependencies() {
  const { invoke } = useIpc();
  const [status, setStatus] = useState<DependencyStatus | null>(null);
  const [checking, setChecking] = useState(false);

  const check = useCallback(async () => {
    setChecking(true);
    try {
      const result = await invoke('check-dependencies', {});
      setStatus(result);
      return result;
    } finally {
      setChecking(false);
    }
  }, [invoke]);

  return { status, checking, check };
}
```

- [ ] **Step 2: Create Setup Wizard component**

```typescript
// src/renderer/components/SetupWizard.tsx
import React, { useEffect, useState } from 'react';
import { useDependencies } from '../hooks/useDependencies';
import './SetupWizard.css';

interface SetupWizardProps {
  onComplete: () => void;
}

export function SetupWizard({ onComplete }: SetupWizardProps) {
  const { status, checking, check } = useDependencies();
  const [screen, setScreen] = useState<'welcome' | 'checking' | 'status' | 'ready'>('welcome');

  useEffect(() => {
    if (screen === 'checking') {
      check().then(() => {
        setScreen('status');
      });
    }
  }, [screen, check]);

  const handleStartCheck = () => {
    setScreen('checking');
  };

  const handleRetry = () => {
    setScreen('checking');
  };

  const handleComplete = () => {
    onComplete();
  };

  return (
    <div className="setup-wizard">
      {screen === 'welcome' && (
        <div className="setup-screen">
          <div className="setup-icon">🔧</div>
          <h1>Welcome to ADB Tools</h1>
          <p>Setting up your system...</p>
          <button onClick={handleStartCheck} className="btn-primary">
            Check System
          </button>
        </div>
      )}

      {screen === 'checking' && (
        <div className="setup-screen">
          <div className="spinner">⟳</div>
          <p>Checking dependencies...</p>
        </div>
      )}

      {screen === 'status' && status && (
        <div className="setup-screen">
          <h2>Dependency Status</h2>
          <div className="status-list">
            <div className={`status-item ${status.python_available ? 'available' : 'missing'}`}>
              <span className="status-icon">{status.python_available ? '✓' : '✗'}</span>
              <span>Python</span>
            </div>
            <div className={`status-item ${status.adb_available ? 'available' : 'missing'}`}>
              <span className="status-icon">{status.adb_available ? '✓' : '✗'}</span>
              <span>ADB</span>
            </div>
            <div className={`status-item ${status.scrcpy_available ? 'available' : 'missing'}`}>
              <span className="status-icon">{status.scrcpy_available ? '✓' : '✗'}</span>
              <span>scrcpy</span>
            </div>
          </div>

          {status.all_available ? (
            <>
              <p className="success-message">All systems ready!</p>
              <button onClick={handleComplete} className="btn-primary">
                Let's Go
              </button>
            </>
          ) : (
            <>
              <p className="warning-message">Some dependencies are missing</p>
              <button onClick={handleRetry} className="btn-secondary">
                Retry
              </button>
              <button onClick={handleComplete} className="btn-primary">
                Continue Anyway
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Create SetupWizard styles**

```css
/* src/renderer/components/SetupWizard.css */
.setup-wizard {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0f1419 0%, #1a1f26 100%);
}

.setup-screen {
  background: #1a1f26;
  padding: 60px 40px;
  border-radius: 12px;
  text-align: center;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.setup-icon,
.spinner {
  font-size: 64px;
  margin-bottom: 24px;
  display: block;
}

.spinner {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.setup-wizard h1,
.setup-wizard h2 {
  color: #00d9ff;
  margin: 0 0 16px 0;
  font-size: 28px;
}

.setup-wizard p {
  color: #a0aabf;
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.status-list {
  margin: 24px 0;
  text-align: left;
}

.status-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin: 8px 0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #a0aabf;
}

.status-item.available {
  background: rgba(0, 255, 65, 0.1);
  color: #00ff41;
}

.status-item.missing {
  background: rgba(255, 68, 68, 0.1);
  color: #ff4444;
}

.status-icon {
  display: inline-block;
  width: 24px;
  margin-right: 12px;
  text-align: center;
  font-weight: bold;
}

.success-message {
  color: #00ff41 !important;
}

.warning-message {
  color: #ffb700 !important;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  margin: 8px 4px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary {
  background: #00d9ff;
  color: #0f1419;
}

.btn-primary:hover {
  background: #00e6ff;
  transform: translateY(-2px);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #a0aabf;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}
```

- [ ] **Step 4: Register IPC handler for check-dependencies**

```typescript
// src/main/ipc.ts (create new file)
import { ipcMain } from 'electron';
import { pythonBridge } from './python-bridge';

export function registerIpcHandlers() {
  ipcMain.handle('check-dependencies', async () => {
    try {
      const result = await pythonBridge.execute('check_dependencies', {});
      return {
        python_available: true,
        adb_available: result.adb_available ?? false,
        scrcpy_available: result.scrcpy_available ?? false,
        all_available: (result.adb_available ?? false) && (result.scrcpy_available ?? false),
      };
    } catch (error) {
      console.error('check-dependencies failed:', error);
      return {
        python_available: false,
        adb_available: false,
        scrcpy_available: false,
        all_available: false,
      };
    }
  });
}
```

- [ ] **Step 5: Update App.tsx to show setup wizard**

```typescript
// src/renderer/App.tsx
import React, { useState, useEffect } from 'react';
import { SetupWizard } from './components/SetupWizard';
import './App.css';

export default function App() {
  const [setupComplete, setSetupComplete] = useState(false);

  useEffect(() => {
    // TODO: Check if setup was completed before
    // For now, always show on first run
  }, []);

  if (!setupComplete) {
    return <SetupWizard onComplete={() => setSetupComplete(true)} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>ADB Tools</h1>
      </header>
      <main className="app-main">
        <p>Main app content coming in Phase 2...</p>
      </main>
    </div>
  );
}
```

- [ ] **Step 6: Update main/index.ts to register IPC handlers**

```typescript
// src/main/index.ts (add import and call)
import { registerIpcHandlers } from './ipc';

app.on('ready', async () => {
  await pythonBridge.start();
  registerIpcHandlers();
  createWindow();
});
```

- [ ] **Step 7: Create component test**

```typescript
// tests/unit/components/SetupWizard.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SetupWizard } from '@/renderer/components/SetupWizard';

vi.mock('@/renderer/hooks/useIpc', () => ({
  useIpc: () => ({
    invoke: vi.fn().mockResolvedValue({
      python_available: true,
      adb_available: true,
      scrcpy_available: true,
      all_available: true,
    }),
  }),
}));

describe('SetupWizard', () => {
  it('shows welcome screen on mount', () => {
    const onComplete = vi.fn();
    render(<SetupWizard onComplete={onComplete} />);

    expect(screen.getByText(/Welcome to ADB Tools/i)).toBeInTheDocument();
  });

  it('calls onComplete when setup done', async () => {
    const user = userEvent.setup();
    const onComplete = vi.fn();
    
    render(<SetupWizard onComplete={onComplete} />);

    const checkBtn = screen.getByText(/Check System/i);
    await user.click(checkBtn);

    // Wait for check to complete
    await screen.findByText(/All systems ready/i);

    const completeBtn = screen.getByText(/Let's Go/i);
    await user.click(completeBtn);

    expect(onComplete).toHaveBeenCalled();
  });
});
```

- [ ] **Step 8: Run tests**

```bash
npm run test -- SetupWizard.test.tsx
# Expected: PASS
```

- [ ] **Step 9: Commit**

```bash
git add src/renderer/components/SetupWizard.tsx \
        src/renderer/components/SetupWizard.css \
        src/renderer/hooks/useDependencies.ts \
        src/main/ipc.ts \
        tests/unit/components/SetupWizard.test.tsx
git commit -m "feat: create setup wizard for first-run experience

- Welcome screen → dependency check → status display
- Shows available/missing dependencies with icons
- Option to continue anyway if missing deps
- Beautiful dark theme with animations
- Non-technical users can understand status at a glance"
```

---

### Task 1.7: Create Device List & IPC Handler

**Files:**
- Create: `src/renderer/components/DevicePanel.tsx`
- Create: `src/renderer/hooks/useDeviceList.ts`
- Create: `src/renderer/types/device.ts`
- Modify: `src/main/ipc.ts`

**Interfaces:**
- Consumes: `pythonBridge.execute('list_devices')` from Task 1.4
- Produces: `<DevicePanel />` component; `useDeviceList()` hook

**Steps:**

- [ ] **Step 1: Create device types**

```typescript
// src/renderer/types/device.ts
export interface Device {
  id: string;
  model?: string;
  manufacturer?: string;
  status: 'device' | 'offline' | 'unauthorized';
  connection_type: 'usb' | 'wifi';
  battery?: number;
}
```

- [ ] **Step 2: Create useDeviceList hook**

```typescript
// src/renderer/hooks/useDeviceList.ts
import { useState, useEffect, useCallback } from 'react';
import { useIpc } from './useIpc';
import type { Device } from '../types/device';

export function useDeviceList() {
  const { invoke } = useIpc();
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await invoke('list-devices', {});
      setDevices(result.devices || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to list devices');
    } finally {
      setLoading(false);
    }
  }, [invoke]);

  useEffect(() => {
    refresh();
    // Poll every 2 seconds
    const interval = setInterval(refresh, 2000);
    return () => clearInterval(interval);
  }, [refresh]);

  return { devices, loading, error, refresh };
}
```

- [ ] **Step 3: Create DevicePanel component**

```typescript
// src/renderer/components/DevicePanel.tsx
import React from 'react';
import { useDeviceList } from '../hooks/useDeviceList';
import type { Device } from '../types/device';
import './DevicePanel.css';

export interface DevicePanelProps {
  onSelectDevice?: (device: Device) => void;
}

export function DevicePanel({ onSelectDevice }: DevicePanelProps) {
  const { devices, loading, error, refresh } = useDeviceList();
  const [selectedId, setSelectedId] = React.useState<string | null>(null);

  const handleDeviceClick = (device: Device) => {
    setSelectedId(device.id);
    onSelectDevice?.(device);
  };

  return (
    <div className="device-panel">
      <div className="panel-header">
        <h2>Connected Devices</h2>
        <button onClick={refresh} className="btn-refresh" title="Refresh">
          ↻
        </button>
      </div>

      {loading && devices.length === 0 && (
        <div className="loading">
          <span className="spinner">⟳</span>
          <p>Finding devices...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <span>⚠ {error}</span>
          <button onClick={refresh}>Retry</button>
        </div>
      )}

      {devices.length === 0 && !loading && !error && (
        <div className="empty-state">
          <span className="icon">📱</span>
          <p>No devices found</p>
          <small>Connect via USB or WiFi to get started</small>
        </div>
      )}

      <div className="device-list">
        {devices.map((device) => (
          <div
            key={device.id}
            className={`device-card ${selectedId === device.id ? 'selected' : ''}`}
            onClick={() => handleDeviceClick(device)}
          >
            <div className="device-header">
              <span className="device-icon">
                {device.connection_type === 'usb' ? '🔌' : '📡'}
              </span>
              <div className="device-title">
                <h3>{device.model || 'Unknown Device'}</h3>
                <p className="device-id">{device.id}</p>
              </div>
            </div>
            <div className="device-status">
              <span
                className={`status-badge ${device.status}`}
              >
                {device.status === 'device' ? '✓ Connected' : device.status}
              </span>
              {device.battery !== undefined && (
                <span className="battery">🔋 {device.battery}%</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create DevicePanel styles**

```css
/* src/renderer/components/DevicePanel.css */
.device-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a1f26;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  width: 300px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header h2 {
  margin: 0;
  color: #00d9ff;
  font-size: 16px;
}

.btn-refresh {
  background: none;
  border: none;
  color: #a0aabf;
  cursor: pointer;
  font-size: 18px;
  transition: transform 0.3s, color 0.2s;
}

.btn-refresh:hover {
  color: #00d9ff;
  transform: rotate(180deg);
}

.device-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.device-card {
  background: rgba(0, 217, 255, 0.05);
  border: 1px solid rgba(0, 217, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.device-card:hover {
  background: rgba(0, 217, 255, 0.1);
  border-color: rgba(0, 217, 255, 0.4);
}

.device-card.selected {
  background: rgba(0, 217, 255, 0.15);
  border-color: #00d9ff;
  box-shadow: 0 0 12px rgba(0, 217, 255, 0.2);
}

.device-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.device-icon {
  font-size: 24px;
}

.device-title h3 {
  margin: 0;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
}

.device-id {
  margin: 4px 0 0 0;
  color: #6a7080;
  font-size: 12px;
  font-family: monospace;
}

.device-status {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: #a0aabf;
}

.status-badge.device {
  background: rgba(0, 255, 65, 0.1);
  color: #00ff41;
}

.status-badge.offline {
  background: rgba(255, 100, 100, 0.1);
  color: #ff6464;
}

.battery {
  color: #a0aabf;
}

.loading,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6a7080;
  text-align: center;
}

.spinner {
  font-size: 32px;
  display: block;
  margin-bottom: 12px;
  animation: spin 2s linear infinite;
}

.empty-state .icon {
  font-size: 48px;
  margin-bottom: 12px;
  display: block;
}

.empty-state small {
  color: #6a7080;
  display: block;
  margin-top: 8px;
  font-size: 12px;
}

.error-message {
  padding: 16px;
  background: rgba(255, 68, 68, 0.1);
  color: #ff4444;
  border-radius: 8px;
  margin: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-message button {
  background: #ff4444;
  color: white;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
```

- [ ] **Step 5: Register IPC handler**

```typescript
// src/main/ipc.ts (add handler)
ipcMain.handle('list-devices', async () => {
  try {
    const result = await pythonBridge.execute('list_devices', {});
    return result;
  } catch (error) {
    console.error('list-devices failed:', error);
    return { devices: [] };
  }
});
```

- [ ] **Step 6: Update backend to return device info**

```python
# backend/main.py (update handle_list_devices)
def handle_list_devices() -> Dict[str, Any]:
    """List all connected devices"""
    stdout, stderr, code = execute_shell_command("adb devices -l")
    
    if code != 0:
        return {"error": f"adb error: {stderr}"} 
    
    devices = []
    for line in stdout.strip().split('\n')[1:]:
        if line.strip() and 'device' in line:
            parts = line.split()
            device_id = parts[0]
            status = parts[1] if len(parts) > 1 else 'offline'
            
            # Parse model and other info from device list
            model = 'Unknown'
            for part in parts[2:]:
                if part.startswith('model:'):
                    model = part.split(':')[1]
                    break
            
            devices.append({
                "id": device_id,
                "status": status,
                "connection_type": "usb" if ":" not in device_id else "wifi",
                "model": model,
            })
    
    return {"devices": devices}
```

- [ ] **Step 7: Create component test**

```typescript
// tests/unit/components/DevicePanel.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DevicePanel } from '@/renderer/components/DevicePanel';

vi.mock('@/renderer/hooks/useIpc', () => ({
  useIpc: () => ({
    invoke: vi.fn().mockResolvedValue({
      devices: [
        { id: '123abc', model: 'Pixel 6', status: 'device', connection_type: 'usb' },
      ],
    }),
  }),
}));

describe('DevicePanel', () => {
  it('renders device list', async () => {
    render(<DevicePanel />);

    const deviceName = await screen.findByText(/Pixel 6/);
    expect(deviceName).toBeInTheDocument();
  });

  it('calls onSelectDevice when device clicked', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();

    render(<DevicePanel onSelectDevice={onSelect} />);

    const device = await screen.findByText(/Pixel 6/);
    await user.click(device);

    expect(onSelect).toHaveBeenCalled();
  });

  it('shows empty state when no devices', async () => {
    vi.mock('@/renderer/hooks/useIpc', () => ({
      useIpc: () => ({
        invoke: vi.fn().mockResolvedValue({ devices: [] }),
      }),
    }));

    render(<DevicePanel />);

    const empty = await screen.findByText(/No devices found/);
    expect(empty).toBeInTheDocument();
  });
});
```

- [ ] **Step 8: Run tests**

```bash
npm run test -- DevicePanel.test.tsx useDeviceList.test.ts
# Expected: PASS
```

- [ ] **Step 9: Commit**

```bash
git add src/renderer/components/DevicePanel.tsx \
        src/renderer/components/DevicePanel.css \
        src/renderer/hooks/useDeviceList.ts \
        src/renderer/types/device.ts \
        tests/unit/components/DevicePanel.test.tsx \
        tests/unit/hooks/useDeviceList.test.ts
git commit -m "feat: implement device list panel with polling

- Device list refreshes every 2 seconds via IPC
- Shows connection type (USB/WiFi), status, model
- Click to select device (prepared for Phase 2)
- Empty state when no devices connected
- Beautiful card-based layout with status indicators"
```

---

### Task 1.8: Create Main Layout & App Shell

**Files:**
- Create: `src/renderer/components/MainLayout.tsx`
- Modify: `src/renderer/App.tsx`
- Create: `src/renderer/styles/global.css`

**Interfaces:**
- Consumes: `<DevicePanel />` and `<SetupWizard />` components
- Produces: Main app layout with sidebar navigation

**Steps:**

- [ ] **Step 1: Create main layout component**

```typescript
// src/renderer/components/MainLayout.tsx
import React from 'react';
import { DevicePanel } from './DevicePanel';
import type { Device } from '../types/device';

export interface MainLayoutProps {
  selectedDevice?: Device | null;
  onSelectDevice?: (device: Device) => void;
  children?: React.ReactNode;
}

export function MainLayout({ selectedDevice, onSelectDevice, children }: MainLayoutProps) {
  return (
    <div className="main-layout">
      <header className="app-header">
        <div className="header-title">
          <h1>ADB Tools</h1>
          <span className="subtitle">Device Management</span>
        </div>
        <div className="header-status">
          {selectedDevice ? (
            <div className="selected-device">
              <span className="icon">📱</span>
              <span>{selectedDevice.model || selectedDevice.id}</span>
            </div>
          ) : (
            <span className="placeholder">Select a device</span>
          )}
        </div>
      </header>

      <div className="main-content">
        <aside className="sidebar">
          <DevicePanel onSelectDevice={onSelectDevice} />
        </aside>

        <main className="content-area">
          {selectedDevice ? (
            children || <div className="placeholder-content">Select an action from the menu</div>
          ) : (
            <div className="empty-main">
              <span className="icon">📱</span>
              <h2>No Device Selected</h2>
              <p>Connect a device via USB or WiFi to get started</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create global styles**

```css
/* src/renderer/styles/global.css */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --color-primary: #00d9ff;
  --color-primary-dark: #0099cc;
  --color-bg-dark: #0f1419;
  --color-bg-surface: #1a1f26;
  --color-bg-surface-alt: #252b33;
  --color-text: #ffffff;
  --color-text-secondary: #a0aabf;
  --color-text-muted: #6a7080;
  --color-border: rgba(255, 255, 255, 0.1);
  --color-success: #00ff41;
  --color-warning: #ffb700;
  --color-error: #ff4444;
}

body {
  background: var(--color-bg-dark);
  color: var(--color-text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow: hidden;
}

#root {
  width: 100vw;
  height: 100vh;
}

.app,
.main-layout {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: var(--color-bg-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-primary);
}

.header-title .subtitle {
  color: var(--color-text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.header-status {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.selected-device {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-primary);
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  flex: 0 0 auto;
  overflow: hidden;
}

.content-area {
  flex: 1;
  background: var(--color-bg-dark);
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-main,
.placeholder-content {
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-main .icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}

.empty-main h2 {
  color: var(--color-text);
  font-size: 20px;
  margin-bottom: 8px;
}

.empty-main p {
  color: var(--color-text-muted);
}

/* Scrollbars */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* Animations */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Focus styles */
button:focus,
input:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Selection */
::selection {
  background: var(--color-primary);
  color: var(--color-bg-dark);
}
```

- [ ] **Step 3: Update App.tsx**

```typescript
// src/renderer/App.tsx
import React, { useState } from 'react';
import { SetupWizard } from './components/SetupWizard';
import { MainLayout } from './components/MainLayout';
import type { Device } from './types/device';
import './styles/global.css';

export default function App() {
  const [setupComplete, setSetupComplete] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);

  if (!setupComplete) {
    return <SetupWizard onComplete={() => setSetupComplete(true)} />;
  }

  return (
    <MainLayout selectedDevice={selectedDevice} onSelectDevice={setSelectedDevice} />
  );
}
```

- [ ] **Step 4: Update styles in existing CSS files**

```css
/* Update App.css to be minimal */
/* Most styles moved to global.css */
```

- [ ] **Step 5: Type-check**

```bash
npm run type-check
# Expected: No errors
```

- [ ] **Step 6: Test the full flow**

```bash
npm run dev
# Expected: App launches, shows setup wizard, then main layout after complete
```

- [ ] **Step 7: Commit**

```bash
git add src/renderer/components/MainLayout.tsx \
        src/renderer/styles/global.css \
        src/renderer/App.tsx
git commit -m "feat: create main app layout and global styles

- Main layout with header, sidebar, content area
- Dark theme with consistent color palette
- Responsive design ready for component additions
- Setup wizard → main app flow complete"
```

---

### Task 1.9: Integration Test - Device List → Selection Flow

**Files:**
- Create: `tests/integration/device-connection.test.ts`

**Interfaces:**
- Consumes: All Phase 1 components and IPC handlers
- Produces: Working integration test of full device list flow

**Steps:**

- [ ] **Step 1: Create integration test**

```typescript
// tests/integration/device-connection.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '@/renderer/App';

describe('Device Connection Integration', () => {
  beforeEach(() => {
    // Mock Python bridge to return devices
    vi.mock('@/main/python-bridge', () => ({
      pythonBridge: {
        execute: vi.fn().mockResolvedValue({
          devices: [
            {
              id: '192.168.1.100:5555',
              model: 'Pixel 6',
              manufacturer: 'Google',
              status: 'device',
              connection_type: 'wifi',
              battery: 85,
            },
            {
              id: 'emulator-5554',
              model: 'Android Emulator',
              status: 'device',
              connection_type: 'usb',
            },
          ],
        }),
      },
    }));
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('shows setup wizard then device list', async () => {
    render(<App />);

    // Should show setup wizard initially
    expect(screen.getByText(/Welcome to ADB Tools/i)).toBeInTheDocument();

    // Complete setup
    const checkBtn = screen.getByText(/Check System/i);
    await userEvent.click(checkBtn);

    await waitFor(() => {
      expect(screen.getByText(/All systems ready/i)).toBeInTheDocument();
    });

    const completeBtn = screen.getByText(/Let's Go/i);
    await userEvent.click(completeBtn);

    // Should show main layout
    await waitFor(() => {
      expect(screen.getByText(/ADB Tools/i)).toBeInTheDocument();
    });

    // Should show device list
    await waitFor(() => {
      expect(screen.getByText(/Pixel 6/i)).toBeInTheDocument();
    });
  });

  it('selects device when clicked', async () => {
    render(<App />);

    // Skip setup
    await userEvent.click(screen.getByText(/Check System/i));
    await waitFor(() => {
      expect(screen.getByText(/All systems ready/i)).toBeInTheDocument();
    });
    await userEvent.click(screen.getByText(/Let's Go/i));

    // Wait for device list
    await waitFor(() => {
      expect(screen.getByText(/Pixel 6/i)).toBeInTheDocument();
    });

    // Click device
    const deviceCard = screen.getByText(/Pixel 6/i).closest('.device-card');
    await userEvent.click(deviceCard!);

    // Should update header
    await waitFor(() => {
      expect(screen.getByText(/Pixel 6/)).toBeInTheDocument();
    });
  });
});
```

- [ ] **Step 2: Run integration test**

```bash
npm run test:integration -- device-connection.test.ts
# Expected: PASS
```

- [ ] **Step 3: Commit**

```bash
git add tests/integration/device-connection.test.ts
git commit -m "test: add integration test for device list flow

- Tests setup wizard → main app → device selection
- Verifies IPC communication end-to-end
- Validates UI state transitions"
```

---

### Task 1.10: Build Configuration & First Build

**Files:**
- Create: `electron-builder.yml`
- Modify: `package.json`

**Steps:**

- [ ] **Step 1: Create electron-builder config**

```yaml
# electron-builder.yml
appId: com.adbtools.desktop
productName: ADB Tools
directories:
  buildResources: public
  output: release

files:
  - from: dist
    to: resources/app
    filter: '!**/*.map'
  - from: bin
    to: resources/bin
  - from: backend
    to: resources/app/backend

extraMetadata:
  name: adb-tools

win:
  target:
    - nsis
    - portable
  certificateFile: null
  certificatePassword: null

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true
  createStartMenuShortcut: true
  shortcutName: ADB Tools

portable:
  artifactName: '${name}-${version}-portable.${ext}'

linux:
  target:
    - AppImage
    - deb
  category: Development
  icon: public/logo.png

appImage:
  artifactName: '${name}-${version}.${ext}'

deb:
  depends:
    - python3.11
  category: Development
```

- [ ] **Step 2: Update package.json with build scripts**

```json
{
  "scripts": {
    "build": "vite build && tsc src/main --outDir dist --declaration false",
    "build:all": "npm run build",
    "package": "electron-builder",
    "package:win": "electron-builder --win",
    "package:linux": "electron-builder --linux"
  }
}
```

- [ ] **Step 3: Build the project**

```bash
npm run build
# Expected: dist/ directory created with all assets
```

- [ ] **Step 4: Verify build artifacts**

```bash
ls -la dist/
# Expected: main.js, preload.js, renderer/ with index.html and assets
```

- [ ] **Step 5: Test production build**

```bash
npm run dev
# Even in dev mode, should use built assets
```

- [ ] **Step 6: Commit**

```bash
git add electron-builder.yml package.json
git commit -m "feat: add build and packaging configuration

- Electron builder config for Win/Linux installers
- Build scripts for production bundling
- Output to release/ directory
- Ready for Phase 1 release"
```

---

## Phase 1 Summary

At the end of Phase 1, you'll have:

✅ **Core Infrastructure**
- Electron + React + TypeScript scaffold
- Secure IPC bridge with type safety
- Python backend with JSON-RPC protocol
- Bundled dependency checking

✅ **First-Run Experience**
- Setup wizard with dependency status display
- Auto-detection of Python, ADB, scrcpy
- Config file marking setup completion

✅ **Device Management (Basic)**
- Real-time device list (2s polling)
- USB and WiFi device detection
- Device selection with header feedback
- Beautiful dark theme UI

✅ **Testing Foundation**
- Unit tests for components and utilities
- Integration test for device list flow
- IPC mocking patterns established

✅ **Release Ready**
- Vite build pipeline
- Electron builder configuration
- Production build tested

---

## Execution Handoff

**Plan complete!** The Phase 1 plan contains 10 tasks covering core foundation. Each task is self-contained and testable.

**Two execution options:**

**1. Subagent-Driven (Recommended)** — I dispatch a fresh subagent per task, review results between tasks, fast iteration. Best for multi-person teams or when you want async progress.

**2. Inline Execution** — Execute tasks sequentially in this session using `superpowers:executing-plans`, batch execution with checkpoints. Best for single developer or when you want continuous feedback.

**Which approach would you prefer?**

If you choose subagent-driven, I'll use `superpowers:subagent-driven-development` to orchestrate the work.

If you choose inline, I'll use `superpowers:executing-plans` to guide you through each step.

Or, you can **pause here** and start Phase 1 whenever you're ready. The full plan document is saved to `docs/superpowers/plans/2026-07-03-adb-tools-desktop-implementation.md` and can be picked up anytime.

(Phases 2-4 plan document will be created after Phase 1 is complete, so requirements become clearer with working code.)

What would you like to do?

