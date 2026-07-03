# Testing Guide

## Overview

ADB-Tools Desktop uses a multi-layered testing strategy covering unit tests, integration tests, and end-to-end tests.

**Testing Pyramid**:
```
        E2E Tests (10-20%)
       Integration Tests (30-40%)
        Unit Tests (50-60%)
```

---

## Test Setup

### Unit Testing Framework

**Frontend**: Vitest + React Testing Library  
**Backend**: pytest

**Installation**:
```bash
npm install --save-dev vitest @vitest/ui react-testing-library @testing-library/jest-dom
pip install pytest pytest-asyncio pytest-mock
```

### File Structure

```
tests/
├── unit/
│   ├── components/               # React component unit tests
│   │   ├── DevicePanel.test.tsx
│   │   └── AppManager.test.tsx
│   ├── hooks/                    # Custom React hook tests
│   │   └── useDeviceList.test.ts
│   ├── main/                     # Electron main process tests
│   │   ├── ipc.test.ts
│   │   └── python-bridge.test.ts
│   └── backend/                  # Python backend tests
│       ├── test_adb_wrapper.py
│       └── test_device_manager.py
├── integration/
│   ├── device-connection.test.ts # Device list → connection
│   ├── file-transfer.test.ts     # Push/pull operations
│   ├── app-install.test.ts       # App installation flow
│   └── logcat-streaming.test.ts  # Logcat real-time updates
└── e2e/
    ├── full-workflow.spec.ts     # Complete user journey
    └── error-recovery.spec.ts    # Error handling paths
```

---

## Unit Tests

### React Components

**Framework**: Vitest + React Testing Library

**Pattern**:
```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DevicePanel from '@/components/DevicePanel';

describe('DevicePanel', () => {
  it('renders device list', async () => {
    const mockDevices = [
      { id: '123', model: 'Pixel 6', status: 'device' }
    ];
    
    // Mock IPC
    vi.mock('electron', () => ({
      ipcRenderer: {
        invoke: vi.fn().mockResolvedValue(mockDevices)
      }
    }));
    
    render(<DevicePanel />);
    
    const deviceName = await screen.findByText('Pixel 6');
    expect(deviceName).toBeInTheDocument();
  });

  it('handles device selection', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    
    render(<DevicePanel onSelect={onSelect} />);
    const device = await screen.findByText('Pixel 6');
    
    await user.click(device);
    expect(onSelect).toHaveBeenCalled();
  });

  it('shows error when list fails', async () => {
    vi.mock('electron', () => ({
      ipcRenderer: {
        invoke: vi.fn().mockRejectedValue(new Error('ADB error'))
      }
    }));
    
    render(<DevicePanel />);
    const error = await screen.findByText(/error/i);
    expect(error).toBeInTheDocument();
  });
});
```

**Guidelines**:
- Test behavior, not implementation
- Mock IPC calls
- Test error states
- Test user interactions (click, type, etc.)

---

### Electron Main Process

**Framework**: Vitest (mocking Node.js modules)

**Pattern**:
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { registerIpcHandlers } from '@/main/ipc';

describe('IPC Handlers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('lists devices via IPC', async () => {
    const mockPythonBridge = {
      execute: vi.fn().mockResolvedValue({
        status: 'success',
        data: [{ id: '123', model: 'Pixel 6' }]
      })
    };
    
    const handler = await registerIpcHandlers(mockPythonBridge);
    const result = await handler.invoke('list-devices');
    
    expect(mockPythonBridge.execute).toHaveBeenCalledWith({
      cmd: 'list_devices'
    });
    expect(result).toHaveLength(1);
  });

  it('handles IPC errors gracefully', async () => {
    const mockPythonBridge = {
      execute: vi.fn().mockRejectedValue(new Error('Device offline'))
    };
    
    const handler = await registerIpcHandlers(mockPythonBridge);
    
    await expect(handler.invoke('list-devices')).rejects.toThrow('Device offline');
  });
});
```

---

### Python Backend

**Framework**: pytest

**Pattern**:
```python
import pytest
from backend.adb_wrapper import AdbWrapper
from unittest.mock import patch, MagicMock

class TestAdbWrapper:
    @pytest.fixture
    def adb(self):
        return AdbWrapper()
    
    @patch('subprocess.run')
    def test_list_devices(self, mock_run, adb):
        # Mock ADB output
        mock_run.return_value.stdout = "List of attached devices\n123abc  device\n"
        
        devices = adb.list_devices()
        
        assert len(devices) == 1
        assert devices[0]['id'] == '123abc'
        mock_run.assert_called_with(['adb', 'devices'], capture_output=True, text=True)
    
    @patch('subprocess.run')
    def test_device_not_found(self, mock_run, adb):
        mock_run.return_value.stdout = "List of attached devices\n"
        
        devices = adb.list_devices()
        
        assert len(devices) == 0
    
    @patch('subprocess.run')
    def test_adb_command_timeout(self, mock_run, adb):
        mock_run.side_effect = TimeoutError("ADB timeout")
        
        with pytest.raises(TimeoutError):
            adb.get_device_info('123abc')
```

**Guidelines**:
- Mock subprocess calls (don't require real ADB)
- Test error cases (timeout, device offline, etc.)
- Use fixtures for setup
- Test command parsing (output from ADB is often unstructured)

---

## Integration Tests

### Device Connection Flow

**Test**: USB device → wifi setup → device list shows wifi connection

```typescript
describe('Device Connection Integration', () => {
  it('connects device via WiFi after USB setup', async () => {
    // 1. Mock initial USB device detected
    vi.mock('electron', () => ({
      ipcRenderer: {
        invoke: vi
          .fn()
          .mockResolvedValueOnce([
            { id: '123abc', connection_type: 'usb', status: 'device' }
          ])
          .mockResolvedValueOnce({ success: true })  // TCP setup
          .mockResolvedValueOnce([
            { id: '192.168.1.100:5555', connection_type: 'wifi', status: 'device' }
          ])
      }
    }));
    
    // 2. Start TCP on USB device
    await ipcRenderer.invoke('start-tcp', { device_id: '123abc' });
    
    // 3. Connect via WiFi
    await ipcRenderer.invoke('connect-wifi', { ip_address: '192.168.1.100' });
    
    // 4. Verify WiFi device in list
    const devices = await ipcRenderer.invoke('list-devices');
    expect(devices).toContainEqual({
      id: '192.168.1.100:5555',
      connection_type: 'wifi'
    });
  });
});
```

---

### File Transfer Flow

**Test**: Select file → upload to device → verify file exists

```typescript
describe('File Transfer Integration', () => {
  it('uploads file and verifies on device', async () => {
    const localPath = '/Users/user/test.txt';
    const remotePath = '/sdcard/Download/test.txt';
    
    // 1. Push file
    const pushResult = await ipcRenderer.invoke('push-file', {
      device_id: '123abc',
      local_path: localPath,
      remote_path: remotePath
    });
    expect(pushResult.success).toBe(true);
    
    // 2. List directory to verify
    const files = await ipcRenderer.invoke('list-directory', {
      device_id: '123abc',
      path: '/sdcard/Download'
    });
    
    // 3. Confirm file exists
    const transferred = files.find(f => f.name === 'test.txt');
    expect(transferred).toBeDefined();
    expect(transferred.size).toBeGreaterThan(0);
  });
  
  it('resumes interrupted transfer', async () => {
    // Simulate network interruption
    let attempts = 0;
    vi.mock('electron', () => ({
      ipcRenderer: {
        invoke: vi.fn().mockImplementation((channel, args) => {
          if (channel === 'push-file' && attempts++ === 0) {
            throw new Error('Network timeout');
          }
          return Promise.resolve({ success: true });
        })
      }
    }));
    
    // First attempt fails
    await expect(ipcRenderer.invoke('push-file', {...})).rejects.toThrow();
    
    // Retry succeeds
    const result = await ipcRenderer.invoke('push-file', {...});
    expect(result.success).toBe(true);
  });
});
```

---

### App Installation Flow

**Test**: Install APK → verify in app list

```typescript
describe('App Installation Integration', () => {
  it('installs app and verifies in list', async () => {
    const apkPath = '/path/to/app.apk';
    
    // 1. Install app
    const installResult = await ipcRenderer.invoke('install-app', {
      device_id: '123abc',
      apk_path: apkPath
    });
    expect(installResult.success).toBe(true);
    
    // 2. List apps
    const apps = await ipcRenderer.invoke('list-apps', {
      device_id: '123abc',
      filter: 'user'
    });
    
    // 3. Verify installed
    const installed = apps.find(a => a.package === 'com.example.app');
    expect(installed).toBeDefined();
  });
});
```

---

## End-to-End Tests

### Framework: Playwright

**Installation**:
```bash
npm install --save-dev @playwright/test
```

**Pattern**:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Full Workflow', () => {
  test.beforeEach(async ({ app }) => {
    // Start app
    await app.start();
    // Wait for device list to load
    await app.waitForSelector('[data-testid="device-list"]');
  });

  test('user connects device and manages apps', async ({ app, page }) => {
    // 1. Connect device via WiFi
    await page.click('button:has-text("Add WiFi Device")');
    await page.fill('input[placeholder="IP Address"]', '192.168.1.100');
    await page.click('button:has-text("Connect")');
    
    // Wait for device to appear
    await page.waitForSelector('text=Pixel 6');
    
    // 2. Select device
    await page.click('text=Pixel 6');
    
    // 3. Navigate to App Manager
    await page.click('text=Apps');
    await page.waitForSelector('[data-testid="app-list"]');
    
    // 4. Install app
    const apkPath = './test-fixtures/test-app.apk';
    await page.setInputFiles('input[type="file"]', apkPath);
    await page.click('button:has-text("Install")');
    
    // Wait for installation
    await page.waitForSelector('text=Installation complete');
    
    // 5. Verify app in list
    const appName = await page.locator('text=TestApp');
    await expect(appName).toBeVisible();
  });

  test('user views device info and monitoring', async ({ page }) => {
    // Select device
    await page.click('[data-testid="device-card"]');
    
    // Navigate to details
    await page.click('text=Details');
    
    // Verify hardware info displayed
    await expect(page.locator('text=Android')).toBeVisible();
    await expect(page.locator('text=Pixel')).toBeVisible();
    
    // Monitor battery (real-time)
    const battery = page.locator('[data-testid="battery-percent"]');
    const initialValue = await battery.textContent();
    
    // Wait a bit and check update
    await page.waitForTimeout(3000);
    // Battery might update (or stay same), just verify element still present
    await expect(battery).toBeVisible();
  });

  test('error recovery on device disconnect', async ({ page }) => {
    // Device is connected
    await page.click('[data-testid="device-card"]');
    
    // Simulate disconnect (mock)
    await page.evaluate(() => {
      window.testMockDeviceDisconnect = true;
    });
    
    // Trigger device list refresh
    await page.click('button[title="Refresh"]');
    
    // Expect error message
    await expect(page.locator('text=Device disconnected')).toBeVisible();
    
    // Verify UI recovers (not frozen)
    await expect(page.click('button[title="Refresh"]')).resolves.toBeDefined();
  });
});
```

---

## Running Tests

### Unit Tests

```bash
# Run all unit tests
npm run test

# Watch mode (re-run on file change)
npm run test:watch

# Coverage report
npm run test:coverage

# Vitest UI (visual dashboard)
npm run test:ui

# Backend tests only
cd backend && pytest -v
```

### Integration Tests

```bash
# Run integration tests
npm run test:integration

# With device attached (real device tests)
npm run test:integration -- --with-device
```

### E2E Tests

```bash
# Run E2E tests
npm run test:e2e

# Headed mode (see browser)
npm run test:e2e -- --headed

# Debug mode
npm run test:e2e -- --debug

# Single test file
npm run test:e2e -- full-workflow.spec.ts
```

---

## Test Data & Fixtures

### Mock Device Data

```typescript
// tests/fixtures/devices.ts
export const mockDevices = [
  {
    id: '192168a100:5555',
    model: 'Pixel 6',
    manufacturer: 'Google',
    android_version: '13',
    status: 'device',
    connection_type: 'wifi'
  },
  {
    id: '123abc456def',
    model: 'Samsung Galaxy S21',
    manufacturer: 'Samsung',
    android_version: '12',
    status: 'device',
    connection_type: 'usb'
  }
];

export const mockApps = [
  {
    name: 'Chrome',
    package: 'com.android.chrome',
    version: '120.0',
    size: 150000000,
    is_system: false
  },
  // ...
];
```

### Mock ADB Commands

```python
# backend/tests/fixtures.py
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_adb_devices():
    """Mock adb devices output"""
    return """List of attached devices
192.168.1.100:5555  device
123abc456def        device
"""

@pytest.fixture
def mock_adb_shell():
    """Mock adb shell output"""
    @patch('subprocess.run')
    def _mock(mock_run):
        def run_side_effect(*args, **kwargs):
            if 'getprop' in args[0]:
                return MagicMock(stdout='13')  # Android version
            elif 'pm list packages' in args[0]:
                return MagicMock(stdout='package:com.example.app\n')
            return MagicMock(stdout='')
        mock_run.side_effect = run_side_effect
        return mock_run
    return _mock()
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [18, 20]

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node }}
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          npm install
          cd backend && pip install -r requirements.txt
      
      - name: Run unit tests
        run: npm run test
      
      - name: Run integration tests
        run: npm run test:integration
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Test Coverage Goals

| Layer | Target | Current |
|-------|--------|---------|
| Unit Tests | 80%+ | TBD |
| Integration Tests | 60%+ | TBD |
| E2E Tests | Key user flows | TBD |

---

## Debugging Failed Tests

### Common Issues

**"Module not found" error**:
```bash
npm install
npm run build
```

**IPC mock not working**:
```typescript
// Ensure mock is registered BEFORE component import
vi.mock('electron', () => ({...}));
import { MyComponent } from './Component';
```

**Subprocess timeout in tests**:
```python
# Use timeout parameter
result = run_command_with_timeout(cmd, timeout=5)
```

**Device not found in E2E test**:
```bash
# Ensure real device or emulator running
adb devices
```

---

## Adding New Tests

1. **Identify layer**: Is this unit/integration/E2E?
2. **Create file**: `tests/<layer>/<feature>.test.ts(x)`
3. **Write test**: Follow patterns above
4. **Run locally**: `npm run test:watch`
5. **Commit**: Include test in same PR as feature
6. **CI passes**: Verify all tests pass on GitHub Actions

