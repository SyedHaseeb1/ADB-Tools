# Deployment & Release Guide

## Overview

This guide covers building, packaging, and releasing ADB-Tools Desktop for Windows and Linux.

---

## Pre-Release Checklist

Before any release, verify:

- [ ] All tests passing (`npm run test`, `npm run test:e2e`)
- [ ] No uncommitted changes
- [ ] Version bumped in `package.json` and `backend/version.py`
- [ ] CHANGELOG.md updated
- [ ] Code reviewed and approved
- [ ] Branch merged to `main`

---

## Build Process

### 1. Development Build

Used during active development with HMR (hot module reload).

```bash
npm run dev
```

This starts:
- Vite dev server on `http://localhost:5173`
- Electron app pointing to dev server
- Python backend (auto-started by Electron)

### 2. Production Build

Prepares optimized bundles for packaging.

```bash
npm run build
```

This:
- Builds Vite assets (minified, optimized)
- Builds Electron main process
- Builds Python backend
- Creates `dist/` directory with all artifacts

**Output**:
```
dist/
├── main.js                    # Electron main (compiled)
├── preload.js                 # Preload script
├── renderer/                  # React app (bundled + minified)
│   ├── index.html
│   ├── assets/
│   │   ├── app.js
│   │   └── styles.css
└── backend/                   # Python backend
    ├── main.py
    ├── adb_wrapper.py
    └── ...
```

---

## Packaging

### Build Configuration

**File**: `electron-builder.yml`

```yaml
appId: com.adbtools.desktop
productName: ADB Tools

directories:
  buildResources: public
  output: release

files:
  - from: dist/main.js
    to: resources/app/main.js
  - from: dist/preload.js
    to: resources/app/preload.js
  - from: dist/renderer
    to: resources/app/renderer
  - from: backend
    to: resources/app/backend
  - from: bin
    to: resources/bin

extraMetadata:
  name: adb-tools

# Platform-specific configs below
```

### Windows Packaging (NSIS Installer)

```bash
npm run package:win
```

**Output**: `release/ADB-Tools-Setup-X.Y.Z.exe`

**NSIS Config** (in `electron-builder.yml`):
```yaml
win:
  target:
    - nsis
    - portable
  certificateFile: path/to/cert.pfx
  certificatePassword: ${{ secrets.WIN_CERT_PASSWORD }}

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true
  createStartMenuShortcut: true
  shortcutName: ADB Tools

portable:
  artifactName: ${name}-${version}-portable.${ext}
```

**What NSIS Does**:
1. Displays installer wizard
2. Extracts to `C:\Program Files\ADB Tools\` (or user-chosen directory)
3. Creates Start Menu shortcuts
4. Creates Desktop shortcut (optional)
5. Registers in Add/Remove Programs
6. Runs setup wizard on first launch

**Signing** (optional, prevents Windows SmartScreen warnings):
```bash
# Generate self-signed cert (for testing)
New-SelfSignedCertificate -Type CodeSigning -CertStoreLocation "Cert:\CurrentUser\My" -Subject "CN=ADB Tools"

# For production: use code signing certificate from provider
```

### Linux Packaging (AppImage & deb)

```bash
npm run package:linux
```

**Output**: 
- `release/ADB-Tools-X.Y.Z.AppImage` (universal, single file)
- `release/adb-tools-X.Y.Z.deb` (Debian/Ubuntu)

**AppImage Config**:
```yaml
linux:
  target:
    - AppImage
    - deb
  category: Development
  icon: public/logo.png

appImage:
  artifactName: ${name}-${version}.${ext}

deb:
  depends:
    - python3.11
  category: Development
```

**What AppImage Does**:
1. Bundles app with runtime
2. Makes executable: `chmod +x ADB-Tools-X.Y.Z.AppImage`
3. Run directly: `./ADB-Tools-X.Y.Z.AppImage`
4. Optional: integrate into launcher (if desktop entry created)

**What deb Does**:
1. Install to `/opt/adb-tools/`
2. Create menu entry
3. Integrate with package manager
4. Easy uninstall via `apt remove adb-tools`

**Desktop Entry** (Linux integration):
```ini
[Desktop Entry]
Name=ADB Tools
Exec=/opt/adb-tools/bin/adb-tools
Icon=adb-tools
Type=Application
Categories=Development;Utility;
```

---

## Full Release Pipeline

### Step 1: Prepare Release

```bash
# Ensure clean main branch
git checkout main
git pull origin main

# Bump version
npm version minor  # or patch, major, prerelease

# This updates package.json + creates git tag
git log --oneline -5
# Should show: v1.2.0 (tag) and version bump commit
```

### Step 2: Build & Package

```bash
# Build production assets
npm run build

# Package for all platforms (Windows + Linux)
npm run package

# Or platform-specific:
npm run package:win
npm run package:linux
```

**Output** in `release/`:
```
release/
├── ADB-Tools-Setup-1.2.0.exe      # Windows installer
├── ADB-Tools-1.2.0-portable.exe   # Windows portable
├── ADB-Tools-1.2.0.AppImage       # Linux universal
└── adb-tools-1.2.0.deb            # Linux deb package
```

### Step 3: Test Installers

**Windows**:
```bash
# Run installer
release/ADB-Tools-Setup-1.2.0.exe

# Or portable (no install)
release/ADB-Tools-1.2.0-portable.exe

# Verify:
# - App launches
# - Device list works
# - Can install/uninstall apps
```

**Linux**:
```bash
# Test AppImage
chmod +x release/ADB-Tools-1.2.0.AppImage
./release/ADB-Tools-1.2.0.AppImage

# Or test deb
sudo apt install ./release/adb-tools-1.2.0.deb
adb-tools  # Run from command line

# Verify same as Windows
```

### Step 4: Sign & Upload (Optional)

**Sign Windows Installer** (Code Signing Certificate):
```bash
signtool sign /f cert.pfx /p password /t http://timestamp.server release/ADB-Tools-Setup-1.2.0.exe
```

**Upload to Release Server**:
```bash
# Copy to CDN or web server
scp release/* user@releases.adb-tools.com:/downloads/v1.2.0/

# Or upload to GitHub Releases
gh release create v1.2.0 release/*
```

### Step 5: Create GitHub Release

```bash
# Tag already created by npm version
# Create release notes
gh release create v1.2.0 \
  --title "ADB Tools v1.2.0" \
  --notes-file RELEASE_NOTES.md \
  release/*
```

**Release Notes Template** (`RELEASE_NOTES.md`):
```markdown
# ADB Tools v1.2.0

## New Features
- Real-time device monitoring (battery, RAM, storage)
- App installation via drag-and-drop
- Logcat filtering with regex support

## Bug Fixes
- Fixed device disconnection handling (#123)
- Fixed file transfer progress bar (#124)

## Improvements
- Faster device list refresh (now 1s instead of 2s)
- Better error messages for network issues
- Dark theme improved for OLED displays

## Downloads
- [Windows Installer](https://github.com/user/adb-tools/releases/download/v1.2.0/ADB-Tools-Setup-1.2.0.exe)
- [Windows Portable](https://github.com/user/adb-tools/releases/download/v1.2.0/ADB-Tools-1.2.0-portable.exe)
- [Linux AppImage](https://github.com/user/adb-tools/releases/download/v1.2.0/ADB-Tools-1.2.0.AppImage)
- [Linux deb](https://github.com/user/adb-tools/releases/download/v1.2.0/adb-tools-1.2.0.deb)
```

### Step 6: Announce Release

- Post on GitHub Releases page
- Send release email to users (if email list exists)
- Update website download page
- Social media announcement (optional)

---

## Dependency Bundling

### ADB Binary Bundling

**Windows**:
```bash
# Download ADB from Android SDK
# or use pre-built: adb.exe
cp /path/to/adb.exe bin/windows/adb.exe
```

**Linux**:
```bash
# Download or build from source
cp /path/to/adb bin/linux/adb
chmod +x bin/linux/adb
```

**Verify**:
```bash
# Windows
bin/windows/adb.exe version

# Linux
bin/linux/adb version
```

### scrcpy Binary Bundling

**Windows**:
```bash
# Download from: https://github.com/Genymobile/scrcpy/releases
unzip scrcpy-win64-v*.zip -d bin/windows/
```

**Linux**:
```bash
# Download or build
cp /path/to/scrcpy bin/linux/scrcpy
chmod +x bin/linux/scrcpy
```

### Python Runtime Bundling

**Option 1: Embedded Python (Windows)**
```bash
# Download from: https://github.com/indygreg/python-build-standalone
wget https://github.com/indygreg/python-build-standalone/releases/download/*/cpython-*/...
unzip -d runtime/windows/python/
```

**Option 2: System Python + pip freeze (Linux)**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip freeze > frozen.txt
# Bundle venv (large) or use system python requirement
```

### Updating Bundled Versions

**When ADB updates**:
1. Download latest from https://developer.android.com/studio/releases/platform-tools
2. Test with ADB wrapper
3. Update version in `bin/windows/version.txt` and `bin/linux/version.txt`
4. Commit to git
5. Bump app version and release new build

**When scrcpy updates**:
1. Download latest from https://github.com/Genymobile/scrcpy/releases
2. Test screen mirroring
3. Update version numbers
4. Release new build

---

## CI/CD Integration (GitHub Actions)

### Build & Package on Every Push

**File**: `.github/workflows/build.yml`

```yaml
name: Build & Package

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          npm install
          cd backend && pip install -r requirements.txt
      
      - name: Build
        run: npm run build
      
      - name: Package
        run: npm run package
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: adb-tools-${{ matrix.os }}
          path: release/

  release:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - uses: actions/download-artifact@v3
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: release/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Troubleshooting Deployment

### Issue: "Cannot find module" during build

```bash
# Clear and rebuild
rm -rf node_modules dist
npm install
npm run build
```

### Issue: Windows installer fails signature verification

```bash
# Disable SmartScreen check (for testing)
# Or sign with proper certificate (production)
signtool sign /f cert.pfx /p password /t http://timestamp.server release/*.exe
```

### Issue: Linux AppImage won't run

```bash
# Make executable
chmod +x ADB-Tools-*.AppImage

# Check dependencies
ldd ADB-Tools-*.AppImage | grep "not found"

# May need to install: libfuse2
sudo apt install libfuse2
```

### Issue: ADB binary not found at runtime

```bash
# Verify binary path
# Windows: app.exe is in C:\Program Files\ADB Tools\resources\bin\windows\adb.exe
# Linux: /opt/adb-tools/resources/bin/linux/adb

# Check Python backend path resolution
# In python-bridge.ts: getAppPath() returns bundle directory
```

---

## Version Management

### Versioning Scheme

**Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (major UI redesign, incompatible settings)
- **MINOR**: New features (app install, file transfer, etc.)
- **PATCH**: Bug fixes

### Files to Update

1. **package.json**: `"version": "1.2.3"`
2. **backend/version.py**: `VERSION = "1.2.3"`
3. **CHANGELOG.md**: New entry at top
4. Commit & tag: `git tag v1.2.3`

### Changelog Format

```markdown
# Changelog

All notable changes to ADB Tools are documented here.

## [1.2.0] - 2024-01-20

### Added
- Device real-time monitoring (battery, RAM, storage)
- App installation via drag-and-drop
- Logcat filtering with regex support

### Fixed
- Device disconnection handling (#123)
- File transfer progress bar not updating (#124)

### Changed
- Device list refresh optimized (1s vs 2s)

## [1.1.0] - 2024-01-10

### Added
- WiFi device connection
- File manager (push/pull)

### Fixed
- ADB timeout errors on slow network
```

---

## Update Mechanism (In-App)

### Update Server Setup

**Endpoint**: `https://api.adb-tools.com/releases/latest`

**Response**:
```json
{
  "adb": {
    "version": "1.0.40",
    "url": "https://cdn.adb-tools.com/adb-1.0.40.zip",
    "checksum": "sha256:abc123..."
  },
  "scrcpy": {
    "version": "2.4.1",
    "url": "https://cdn.adb-tools.com/scrcpy-2.4.1.zip",
    "checksum": "sha256:def456..."
  }
}
```

### Implementation

**Backend** (`src/main/updates.ts`):
```typescript
async checkForUpdates() {
  try {
    const response = await fetch('https://api.adb-tools.com/releases/latest', {
      timeout: 3000
    });
    const data = await response.json();
    
    // Compare versions, emit 'update-available' if newer
    if (this.compareVersions(data.adb.version, this.bundledAdbVersion) > 0) {
      this.emitUpdateAvailable(data);
    }
  } catch (error) {
    // Timeout or network error: silently ignore
    console.log('Update check failed (using bundled versions)');
  }
}
```

**Frontend** (`src/renderer/hooks/useUpdateCheck.ts`):
```typescript
ipcRenderer.on('update-available', ({ adb, scrcpy }) => {
  setUpdateNotification({
    visible: true,
    message: `Updates available: ADB ${adb.version}, scrcpy ${scrcpy.version}`,
    action: () => ipcRenderer.invoke('install-updates', { components: ['adb'] })
  });
});
```

---

## Post-Release Tasks

1. **Monitor for crashes**: Check error logs/crash reports
2. **User feedback**: Respond to GitHub issues
3. **Plan next release**: Triage feature requests
4. **Deprecation notices**: If dropping support for old Windows/Linux versions
5. **Security updates**: If vulnerabilities found, release patch immediately

---

## Release Checklist Template

```markdown
## Release v1.2.0 Checklist

- [ ] Create release branch: `git checkout -b release/v1.2.0`
- [ ] Update package.json version
- [ ] Update backend/version.py version
- [ ] Update CHANGELOG.md
- [ ] Run full test suite: `npm run test && npm run test:e2e`
- [ ] Create build artifacts: `npm run package`
- [ ] Test Windows installer on Windows 10/11
- [ ] Test Linux AppImage on Ubuntu 20.04+
- [ ] Test Linux deb on Debian
- [ ] Code review (request peer review)
- [ ] Merge to main: `git merge --no-ff release/v1.2.0`
- [ ] Tag release: `git tag v1.2.0`
- [ ] Push: `git push origin main --tags`
- [ ] Create GitHub Release with notes
- [ ] Announce on social media / email
- [ ] Monitor for issues in first 24h
```

