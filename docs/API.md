# API Reference

## Overview

ADB-Tools Desktop communicates across three layers via two protocols:

1. **IPC Protocol**: React (renderer) ↔ Electron (main process)
2. **Python Protocol**: Electron (main) ↔ Python (backend)

This document specifies both.

---

## IPC Protocol (Electron)

### Overview

The IPC bridge uses Electron's `ipcRenderer` (frontend) and `ipcMain` (backend) for two-way communication.

**Convention**:
- Channel names: kebab-case (`list-devices`, `get-device-info`)
- Argument objects: snake_case fields (`device_id`, `local_path`)

### IPC Methods

#### `ipcRenderer.invoke(channel, args)`

Sends a request and waits for response. Use for one-off queries.

```typescript
const devices = await ipcRenderer.invoke('list-devices');
const info = await ipcRenderer.invoke('get-device-info', { device_id: '123abc' });
```

#### `ipcRenderer.send(channel, args)`

Sends a message (fire-and-forget, no response). Use for commands that don't return data.

```typescript
ipcRenderer.send('start-logcat', { device_id: '123abc' });
```

#### `ipcRenderer.on(channel, handler)`

Listens for messages from main process. Use for streams or notifications.

```typescript
ipcRenderer.on('logcat-line', (event, line) => {
  console.log(line);
});

ipcRenderer.on('update-available', (event, { version }) => {
  showNotification(`Update available: ${version}`);
});
```

#### `ipcRenderer.off(channel, handler)`

Unsubscribe from channel.

```typescript
ipcRenderer.off('logcat-line', handler);
```

---

## IPC Channels Reference

### Device Management

#### `list-devices`

**Type**: `invoke`  
**Args**: None  
**Returns**: Array of device objects

```typescript
const devices = await ipcRenderer.invoke('list-devices');
// [
//   {
//     id: '192.168.1.100:5555',
//     model: 'Pixel 6',
//     manufacturer: 'Google',
//     android_version: '13',
//     status: 'device', // 'device', 'offline', 'unauthorized'
//     connection_type: 'wifi' // 'usb' or 'wifi'
//   },
//   ...
// ]
```

---

#### `connect-wifi`

**Type**: `invoke`  
**Args**: `{ ip_address: string }`  
**Returns**: `{ success: boolean, message: string }`

```typescript
const result = await ipcRenderer.invoke('connect-wifi', { ip_address: '192.168.1.100' });
```

---

#### `disconnect-device`

**Type**: `invoke`  
**Args**: `{ device_id: string }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('disconnect-device', { device_id: '192.168.1.100:5555' });
```

---

#### `reboot-device`

**Type**: `invoke`  
**Args**: `{ device_id: string, mode?: 'normal' | 'bootloader' | 'recovery' }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('reboot-device', { device_id: '123abc', mode: 'normal' });
```

---

#### `get-device-info`

**Type**: `invoke`  
**Args**: `{ device_id: string }`  
**Returns**: Device info object

```typescript
const info = await ipcRenderer.invoke('get-device-info', { device_id: '123abc' });
// {
//   model: 'Pixel 6',
//   manufacturer: 'Google',
//   device_name: 'blueline',
//   android_version: '13',
//   sdk_version: '33',
//   build_id: 'TP1A.220624.014',
//   cpu: 'arm64-v8a',
//   board: 'blueline',
//   ...
// }
```

---

#### `get-device-status`

**Type**: `invoke`  
**Args**: `{ device_id: string }`  
**Returns**: Device status object

```typescript
const status = await ipcRenderer.invoke('get-device-status', { device_id: '123abc' });
// {
//   battery: { level: 85, temp: 32, health: 'good' },
//   ram: { total: 8000, used: 5000, free: 3000 },
//   storage: { total: 128000, used: 100000, free: 28000 },
//   cpu_usage: 45,
//   network: { ssid: 'MyWiFi', ip: '192.168.1.100', signal: -50 }
// }
```

---

### App Management

#### `list-apps`

**Type**: `invoke`  
**Args**: `{ device_id: string, filter?: 'all' | 'system' | 'user' }`  
**Returns**: Array of app objects

```typescript
const apps = await ipcRenderer.invoke('list-apps', { device_id: '123abc' });
// [
//   {
//     name: 'Chrome',
//     package: 'com.android.chrome',
//     version: '120.0.6099.43',
//     size: 150000000,
//     is_system: false,
//     install_date: '2024-01-15'
//   },
//   ...
// ]
```

---

#### `install-app`

**Type**: `invoke`  
**Args**: `{ device_id: string, apk_path: string }`  
**Returns**: `{ success: boolean, message?: string }`

```typescript
const result = await ipcRenderer.invoke('install-app', {
  device_id: '123abc',
  apk_path: '/Users/user/Downloads/app.apk'
});
```

**Progress**: Listen to `install-progress` events

```typescript
ipcRenderer.on('install-progress', (event, { progress, speed, eta }) => {
  console.log(`${progress}% - ${speed} MB/s - ETA: ${eta}s`);
});
```

---

#### `uninstall-app`

**Type**: `invoke`  
**Args**: `{ device_id: string, package: string }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('uninstall-app', { device_id: '123abc', package: 'com.example.app' });
```

---

#### `launch-app`

**Type**: `invoke`  
**Args**: `{ device_id: string, package: string }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('launch-app', { device_id: '123abc', package: 'com.android.chrome' });
```

---

#### `clear-app-data`

**Type**: `invoke`  
**Args**: `{ device_id: string, package: string, clear_cache?: boolean }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('clear-app-data', {
  device_id: '123abc',
  package: 'com.example.app',
  clear_cache: true
});
```

---

### File Transfer

#### `push-file`

**Type**: `invoke`  
**Args**: `{ device_id: string, local_path: string, remote_path: string }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('push-file', {
  device_id: '123abc',
  local_path: '/Users/user/file.txt',
  remote_path: '/sdcard/Download/file.txt'
});
```

**Progress**: Listen to `transfer-progress` events

```typescript
ipcRenderer.on('transfer-progress', (event, { bytes, total, speed }) => {
  const percent = (bytes / total) * 100;
  console.log(`${percent}% - ${speed} MB/s`);
});
```

---

#### `pull-file`

**Type**: `invoke`  
**Args**: `{ device_id: string, remote_path: string, local_path: string }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('pull-file', {
  device_id: '123abc',
  remote_path: '/sdcard/Download/file.txt',
  local_path: '/Users/user/Downloads/file.txt'
});
```

---

#### `list-directory`

**Type**: `invoke`  
**Args**: `{ device_id: string, path: string }`  
**Returns**: Array of file objects

```typescript
const files = await ipcRenderer.invoke('list-directory', {
  device_id: '123abc',
  path: '/sdcard/Download'
});
// [
//   { name: 'file.txt', size: 1024, modified: '2024-01-20', is_dir: false },
//   { name: 'folder', size: 0, modified: '2024-01-19', is_dir: true },
//   ...
// ]
```

---

#### `delete-file`

**Type**: `invoke`  
**Args**: `{ device_id: string, path: string }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('delete-file', {
  device_id: '123abc',
  path: '/sdcard/Download/old_file.txt'
});
```

---

### Logcat

#### `start-logcat`

**Type**: `send`  
**Args**: `{ device_id: string, filter?: string }`

```typescript
ipcRenderer.send('start-logcat', { device_id: '123abc' });
```

**Stream**: Listen to `logcat-line` events

```typescript
ipcRenderer.on('logcat-line', (event, line) => {
  console.log(line);
  // "[12:34:56.789] I/MyApp: Hello world (PID:1234)"
});
```

---

#### `stop-logcat`

**Type**: `send`  
**Args**: `{ device_id: string }`

```typescript
ipcRenderer.send('stop-logcat', { device_id: '123abc' });
```

---

#### `clear-logcat`

**Type**: `invoke`  
**Args**: `{ device_id: string }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('clear-logcat', { device_id: '123abc' });
```

---

### Screenshots & Recording

#### `take-screenshot`

**Type**: `invoke`  
**Args**: `{ device_id: string }`  
**Returns**: `{ success: boolean, path: string }`

```typescript
const result = await ipcRenderer.invoke('take-screenshot', { device_id: '123abc' });
// result.path = '/home/user/.adb-tools/screenshots/screenshot_20240120_123456.png'
```

---

#### `start-screen-record`

**Type**: `send`  
**Args**: `{ device_id: string, duration?: number, resolution?: string, bitrate?: string }`

```typescript
ipcRenderer.send('start-screen-record', {
  device_id: '123abc',
  duration: 30, // seconds
  resolution: '1080x1920',
  bitrate: '20M'
});
```

**Progress**: Listen to `record-progress` events

```typescript
ipcRenderer.on('record-progress', (event, { elapsed, duration }) => {
  console.log(`Recording: ${elapsed}s / ${duration}s`);
});
```

---

#### `stop-screen-record`

**Type**: `send`  
**Args**: `{ device_id: string }`

```typescript
ipcRenderer.send('stop-screen-record', { device_id: '123abc' });
```

**Completion**: Listen to `record-complete` event

```typescript
ipcRenderer.on('record-complete', (event, { path }) => {
  console.log(`Video saved: ${path}`);
});
```

---

### Shell Commands

#### `execute-shell-command`

**Type**: `invoke`  
**Args**: `{ device_id: string, command: string, timeout?: number }`  
**Returns**: `{ stdout: string, stderr: string, exit_code: number }`

```typescript
const result = await ipcRenderer.invoke('execute-shell-command', {
  device_id: '123abc',
  command: 'ls -la /sdcard',
  timeout: 10
});
console.log(result.stdout);
```

---

### Settings & Updates

#### `get-settings`

**Type**: `invoke`  
**Args**: None  
**Returns**: Settings object

```typescript
const settings = await ipcRenderer.invoke('get-settings');
// {
//   theme: 'dark',
//   auto_refresh: true,
//   refresh_rate: 5,
//   logcat_buffer: 10000,
//   ...
// }
```

---

#### `set-settings`

**Type**: `invoke`  
**Args**: `{ key: string, value: any }`  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('set-settings', { key: 'theme', value: 'light' });
```

---

#### `check-updates`

**Type**: `invoke`  
**Args**: None  
**Returns**: `{ available: boolean, updates: { adb?: {...}, scrcpy?: {...} } }`

```typescript
const result = await ipcRenderer.invoke('check-updates');
if (result.available) {
  console.log('Updates available:', result.updates);
}
```

---

#### `install-updates`

**Type**: `invoke`  
**Args**: `{ components: string[] }` (e.g., `['adb', 'scrcpy']`)  
**Returns**: `{ success: boolean }`

```typescript
await ipcRenderer.invoke('install-updates', { components: ['adb'] });
```

**Progress**: Listen to `update-progress` events

```typescript
ipcRenderer.on('update-progress', (event, { component, progress }) => {
  console.log(`Updating ${component}: ${progress}%`);
});
```

---

### Events (Server → Client)

#### `update-available`

Fired when update check completes and updates are found.

```typescript
ipcRenderer.on('update-available', (event, { adb, scrcpy }) => {
  console.log('Updates found:', { adb, scrcpy });
});
```

---

#### `device-connected`

Fired when new device connected.

```typescript
ipcRenderer.on('device-connected', (event, device) => {
  console.log('Device connected:', device.id);
});
```

---

#### `device-disconnected`

Fired when device disconnected.

```typescript
ipcRenderer.on('device-disconnected', (event, device_id) => {
  console.log('Device disconnected:', device_id);
});
```

---

## Python Backend Protocol

### Overview

Electron main process spawns a Python subprocess. Communication via JSON-RPC over stdin/stdout.

**Format**: Line-delimited JSON (each message ends with `\n`)

```
Request:  {"id": 1, "cmd": "list_devices", "args": {}}
Response: {"id": 1, "status": "success", "data": [...]}
```

### Command Format

```json
{
  "id": 123,
  "cmd": "command_name",
  "args": { "arg1": "value1", "arg2": "value2" }
}
```

### Response Format

**Success**:
```json
{
  "id": 123,
  "status": "success",
  "data": { ... }
}
```

**Error**:
```json
{
  "id": 123,
  "status": "error",
  "error": "Device not found",
  "details": { "device_id": "..." }
}
```

**Progress**:
```json
{
  "id": 123,
  "status": "progress",
  "progress": 50,
  "message": "Transferring file..."
}
```

### Python Commands Reference

#### Device Commands

**`list_devices`**
```python
cmd = "list_devices"
# Response: [{"id": "...", "model": "...", ...}, ...]
```

**`get_device_info`**
```python
cmd = "get_device_info"
args = {"device_id": "123abc"}
# Response: {"model": "...", "android_version": "...", ...}
```

**`connect_wifi`**
```python
cmd = "connect_wifi"
args = {"ip_address": "192.168.1.100"}
# Response: {"success": true}
```

**`reboot_device`**
```python
cmd = "reboot_device"
args = {"device_id": "123abc", "mode": "normal"}  # normal, bootloader, recovery
```

---

#### App Commands

**`list_apps`**
```python
cmd = "list_apps"
args = {"device_id": "123abc", "filter": "all"}  # all, system, user
```

**`install_app`**
```python
cmd = "install_app"
args = {"device_id": "123abc", "apk_path": "/path/to/app.apk"}
# Emits progress responses
```

**`uninstall_app`**
```python
cmd = "uninstall_app"
args = {"device_id": "123abc", "package": "com.example.app"}
```

**`launch_app`**
```python
cmd = "launch_app"
args = {"device_id": "123abc", "package": "com.example.app"}
```

**`clear_app_data`**
```python
cmd = "clear_app_data"
args = {"device_id": "123abc", "package": "com.example.app", "clear_cache": true}
```

---

#### File Commands

**`push_file`**
```python
cmd = "push_file"
args = {
  "device_id": "123abc",
  "local_path": "/Users/user/file.txt",
  "remote_path": "/sdcard/Download/file.txt"
}
# Emits progress responses
```

**`pull_file`**
```python
cmd = "pull_file"
args = {
  "device_id": "123abc",
  "remote_path": "/sdcard/Download/file.txt",
  "local_path": "/Users/user/Downloads/file.txt"
}
```

**`list_directory`**
```python
cmd = "list_directory"
args = {"device_id": "123abc", "path": "/sdcard"}
# Response: [{"name": "...", "size": ..., "is_dir": false}, ...]
```

**`delete_file`**
```python
cmd = "delete_file"
args = {"device_id": "123abc", "path": "/sdcard/file.txt"}
```

---

#### Logcat Commands

**`start_logcat`** (stream mode)
```python
cmd = "start_logcat"
args = {"device_id": "123abc", "filter": ""}
# Emits multiple "logcat_line" responses (streaming)
```

**`stop_logcat`**
```python
cmd = "stop_logcat"
args = {"device_id": "123abc"}
```

**`clear_logcat`**
```python
cmd = "clear_logcat"
args = {"device_id": "123abc"}
```

---

#### Screen Commands

**`take_screenshot`**
```python
cmd = "take_screenshot"
args = {"device_id": "123abc"}
# Response: {"path": "/home/user/.adb-tools/screenshots/..."}
```

**`start_screen_record`**
```python
cmd = "start_screen_record"
args = {
  "device_id": "123abc",
  "duration": 30,
  "resolution": "1080x1920",
  "bitrate": "20M"
}
```

**`stop_screen_record`**
```python
cmd = "stop_screen_record"
args = {"device_id": "123abc"}
# Response: {"path": "/home/user/.adb-tools/videos/..."}
```

---

#### Shell Commands

**`execute_shell_command`**
```python
cmd = "execute_shell_command"
args = {
  "device_id": "123abc",
  "command": "ls -la /sdcard",
  "timeout": 10
}
# Response: {"stdout": "...", "stderr": "...", "exit_code": 0}
```

---

### Error Codes

| Code | Meaning |
|------|---------|
| `DEVICE_NOT_FOUND` | Device ID not in `adb devices` list |
| `DEVICE_OFFLINE` | Device present but offline |
| `DEVICE_UNAUTHORIZED` | USB debugging not authorized on device |
| `ADB_ERROR` | Generic ADB command failure |
| `FILE_NOT_FOUND` | File doesn't exist at path |
| `PERMISSION_DENIED` | No permission to access file/command |
| `TIMEOUT` | Command exceeded timeout |
| `INVALID_ARGS` | Invalid arguments provided |

---

## Version

- **IPC Protocol**: v1.0
- **Python Protocol**: v1.0
- **Last Updated**: 2024-07-03

