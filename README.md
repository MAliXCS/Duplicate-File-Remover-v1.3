# Duplicate File Remover v1.3

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A clean, efficient, and user-friendly duplicate file finder and remover application built for Windows. Scan directories, identify duplicate files by content hash, and safely remove them with an intuitive graphical interface.

![Application Screenshot](screenshot.png)

---

## Table of Contents

- [About This App](#about-this-app)
- [Why It Was Created](#why-it-was-created)
- [Why Windows-Only](#why-windows-only)
- [Features](#features)
- [Specifications](#specifications)
- [Requirements](#requirements)
- [Installation](#installation)
- [How to Use](#how-to-use)
- [Screenshots](#screenshots)
- [Security Policy](#security-policy)
- [Contributing](#contributing)
- [License](#license)
- [Tags & Keywords](#tags--keywords)
- [Acknowledgments](#acknowledgments)

---

## About This App

**Duplicate File Remover** is a powerful desktop application designed to help users reclaim disk space by identifying and removing duplicate files. Unlike simple filename-based duplicate finders, this tool uses cryptographic hash algorithms (MD5, SHA1, SHA256) to compare actual file contents, ensuring 100% accuracy in duplicate detection.

### Key Highlights

- **Content-Based Detection**: Uses file hashing to find true duplicates, not just files with the same name
- **Safe Deletion**: Option to move files to Recycle Bin instead of permanent deletion
- **Smart Selection**: Automatically select duplicates while keeping the original file
- **Real-Time Progress**: Visual progress bar with time estimation during scans
- **Customizable Filters**: Exclude patterns, file extensions, hidden/system files
- **Human-Readable Sizes**: Enter sizes as "100MB", "1.5GB" instead of raw bytes

---

## Why It Was Created

This application was born out of a common frustration: managing storage space filled with duplicate files accumulated over years of backups, downloads, and file transfers. Existing solutions were either:

1. **Too expensive** - Many professional duplicate finders require paid licenses
2. **Too complicated** - Command-line tools with steep learning curves
3. **Too limited** - Basic tools that only compare filenames
4. **Too risky** - Tools that permanently delete files without Recycle Bin option

**Duplicate File Remover** bridges this gap by providing a **free, open-source, user-friendly** solution that balances power with simplicity. It's designed for everyday users who want to clean up their drives without risking accidental data loss.

### Use Cases

- Cleaning up photo libraries with duplicate images
- Organizing music collections with duplicate tracks
- Freeing space on external drives and USB sticks
- Consolidating backup folders
- Preparing drives for migration or archival

---

## Why Windows-Only

This application is specifically designed for **Windows** for the following reasons:

### Platform-Specific Features

1. **Windows Explorer Integration**
   - Uses `explorer /select,` command to open folders with files highlighted
   - Native Windows file operations for best compatibility

2. **Windows API Integration**
   - Uses `ctypes` and `ctypes.windll.kernel32` for:
     - Detecting hidden files (FILE_ATTRIBUTE_HIDDEN)
     - Detecting system files (FILE_ATTRIBUTE_SYSTEM)
     - Extended path support (\\?\ prefix for long paths)
     - Direct file deletion via Windows API for special characters

3. **Recycle Bin Support**
   - Integrates with Windows Recycle Bin via `send2trash` library
   - Uses Windows-specific APIs for safe file removal

4. **Path Handling**
   - Handles Windows path conventions (backslashes, drive letters)
   - Supports UNC paths (\\server\share)
   - Extended path support for paths > 260 characters

5. **High DPI Awareness**
   - Uses `SetProcessDpiAwareness` for crisp display on modern displays

### Future Considerations

While the current version is Windows-only, the core duplicate-finding logic is platform-agnostic. A cross-platform version could be developed by abstracting the Windows-specific components.

---

## Features

### Core Features

- [x] **Fast Scanning** - Two-phase scanning (size grouping → hash comparison)
- [x] **Multiple Hash Algorithms** - MD5, SHA1, SHA256 support
- [x] **Safe Deletion** - Move to Recycle Bin or permanent delete
- [x] **Batch Operations** - Delete multiple files at once
- [x] **Smart Selection** - Auto-select duplicates, keep originals

### Advanced Features

- [x] **File Size Limits** - Set minimum/maximum file size filters
- [x] **Extension Filters** - Include only specific file types
- [x] **Pattern Exclusion** - Exclude files matching patterns (e.g., `*.tmp`)
- [x] **Hidden/System File Handling** - Option to skip hidden/system files
- [x] **Time Estimation** - Realistic ETA based on moving average
- [x] **Detailed Logging** - Timestamped operation log

### UI Features

- [x] **Modern Interface** - Clean, intuitive tkinter GUI
- [x] **Progress Tracking** - Visual progress bar with time remaining
- [x] **Sortable Results** - Treeview with sortable columns
- [x] **Open Location** - Jump directly to file location in Explorer
- [x] **Settings Persistence** - Save preferences between sessions

---

## Specifications

### Technical Specifications

| Specification | Details |
|---------------|---------|
| **Language** | Python 3.7+ |
| **GUI Framework** | tkinter (built-in) |
| **Hash Algorithms** | MD5, SHA1, SHA256 |
| **Chunk Size** | 64 KB (65,536 bytes) for hash calculation |
| **Supported File Sizes** | Unlimited (tested up to several GB) |
| **Settings Storage** | JSON file (`duplicate_remover_settings.json`) |
| **Log Format** | In-app timestamped log |

### Performance Specifications

| Metric | Performance |
|--------|-------------|
| **Scan Speed** | ~100-500 files/second (depends on file size) |
| **Hash Speed** | ~50-200 MB/second (depends on storage speed) |
| **Memory Usage** | Low - uses streaming hash calculation |
| **CPU Usage** | Minimal - single-threaded with batch processing |

### File Support

| Feature | Support |
|---------|---------|
| **Long Paths** | Yes (>260 characters with `\\?\` prefix) |
| **Special Characters** | Yes (parentheses, spaces, Unicode) |
| **Network Drives** | Yes (UNC paths supported) |
| **External Drives** | Yes (USB, external HDD/SSD) |
| **Hidden Files** | Optional (configurable) |
| **System Files** | Optional (configurable, default: skip) |

---

## Requirements

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Windows 7 SP1 | Windows 10/11 |
| **Python** | 3.7 | 3.10+ |
| **RAM** | 512 MB | 2 GB |
| **Disk Space** | 50 MB | 100 MB |
| **Display** | 1024x768 | 1920x1080 |

### Python Dependencies

```
tkinter (built-in)
threading (built-in)
hashlib (built-in)
os, sys (built-in)
json (built-in)
fnmatch (built-in)
subprocess (built-in)
ctypes (built-in)
send2trash (optional, for Recycle Bin support)
```

### Optional Dependencies

| Package | Purpose | Install Command |
|---------|---------|-----------------|
| `send2trash` | Move files to Recycle Bin | `pip install send2trash` |

---

## Installation

### Method 1: Run from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/MAliXCS/DuplicateFileRemover.git
   cd DuplicateFileRemover
   ```

2. **Install optional dependency**
   ```bash
   pip install send2trash
   ```

3. **Run the application**
   ```bash
   python DuplicateFileRemover_v1.3.py
   ```

### Method 2: Standalone Executable (Coming Soon)

A standalone `.exe` file will be available in the Releases section for users who don't have Python installed.

---

## How to Use

### Quick Start Guide

#### 1. Select Directory
- Click **"Browse"** to select the folder you want to scan
- Or type/paste the path directly in the text field

#### 2. Start Scan
- Click **"Scan"** to begin the duplicate detection process
- The progress bar will show scan progress with estimated time remaining
- You can click **"Stop"** at any time to cancel the scan

#### 3. Review Results
- Duplicate files are displayed in the results table
- Files marked in **red** are duplicates (keeping one per group)
- The **Group** column shows which files belong together

#### 4. Select Files to Delete
- **"Select All"** - Select all files
- **"Deselect All"** - Clear selection
- **"Duplicates"** - Auto-select only duplicate files (recommended)
- Or manually select files by clicking them (Ctrl+Click for multiple)

#### 5. Delete or Open Location
- **"Delete Selected"** - Move selected files to Recycle Bin or permanently delete
- **"Open Location"** - Open the folder containing the selected file in Explorer

### Settings Configuration

Click **"Settings"** to customize the application:

#### Hash Algorithm
- **MD5** (default) - Fast, good for most use cases
- **SHA1** - More secure, slightly slower
- **SHA256** - Most secure, slowest

#### File Size Limits
- Enter sizes like `100MB`, `1.5GB`, or raw bytes
- **Min Size** - Skip files smaller than this
- **Max Size** - Skip files larger than this (0 = unlimited)

#### When Selecting Duplicates
- **Keep oldest file** (default) - Keeps the original file
- **Keep newest file** - Keeps the most recent version

#### File Extensions Filter
- Enter extensions like `.jpg,.png,.mp3`
- Leave empty to include all file types

#### Excluded Patterns
- Enter patterns to exclude (one per line)
- Examples: `*.tmp`, `*.log`, `Thumbs.db`

#### Skip Options
- **Skip hidden files** - Ignore files with hidden attribute
- **Skip system files** - Ignore Windows system files (recommended)

#### Other Options
- **Move deleted files to Recycle Bin** - Safer deletion method
- **Auto-select duplicates after scan** - Automatically select duplicates when scan completes

### Tips & Best Practices

1. **Start with a test folder** - Try the app on a small folder first to understand how it works
2. **Use "Open Location"** - Always verify files before deleting by opening their location
3. **Enable Recycle Bin** - Keep "Move to Recycle Bin" enabled for safety
4. **Scan external drives** - Great for cleaning up USB drives and external storage
5. **Use size limits** - For large drives, set min size (e.g., 1MB) to skip small files

---

## Screenshots

### Main Interface
![Main Window](docs/screenshots/main_window.png)

### Settings Panel
![Settings](docs/screenshots/settings.png)

### Scan Results
![Results](docs/screenshots/results.png)

---

## Security Policy

### Data Safety

Duplicate File Remover is designed with safety as a priority:

1. **Read-Only Scanning** - The scanning process only reads files to calculate hashes
2. **No Data Transmission** - All operations are local; no data is sent to any server
3. **Recycle Bin Default** - Files are moved to Recycle Bin by default, not permanently deleted
4. **Preview Before Delete** - You can review all files before deletion
5. **Open Location Feature** - Verify files in Explorer before deleting

### File Handling Security

- **Special Character Support** - Properly handles files with special characters in names
- **Long Path Support** - Uses Windows extended path syntax for paths > 260 characters
- **Permission Handling** - Gracefully handles files without delete permissions
- **Locked File Detection** - Skips files that are in use by other applications

### Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue
2. Email: `security@yourdomain.com` (replace with actual contact)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work to resolve the issue promptly.

### Best Practices for Users

1. **Always backup important data** before using any file deletion tool
2. **Verify results** using "Open Location" before deleting
3. **Use Recycle Bin** option for an extra safety net
4. **Run as regular user** - No administrator privileges required for normal use

---

## Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check if the issue already exists
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Windows version and Python version
   - Screenshots (if applicable)

### Suggesting Features

1. Open a new issue with the "Feature Request" label
2. Describe the feature and its use case
3. Explain why it would be valuable

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/DuplicateFileRemover.git
cd DuplicateFileRemover

# Install dependencies
pip install send2trash

# Run tests
python -m pytest tests/
```

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 MAliXCS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Tags & Keywords

`duplicate-files` `file-manager` `disk-cleanup` `storage-management` `duplicate-finder` `file-organizer` `windows-app` `python` `tkinter` `hash-based` `md5` `sha256` `recycle-bin` `file-deletion` `disk-space` `cleanup-tool` `utility` `desktop-application` `gui` `open-source`

---

## Acknowledgments

- **send2trash** - For safe Recycle Bin integration
- **Python tkinter team** - For the excellent GUI framework
- **Contributors** - Thank you to everyone who has contributed to this project
- **Users** - Thank you for using and providing feedback on this tool

---

## Contact

- **Author**: MAliXCS
- **Instagram**: [@x404ctl](https://instagram.com/x404ctl)
- **GitHub**: [@MAliXCS](https://github.com/MAliXCS)
- **Issues**: [GitHub Issues](https://github.com/MAliXCS/DuplicateFileRemover/issues)

---

## Changelog

### v1.3 (Current)
- Fixed "Open File Location" opening folders twice bug
- Added human-readable file size input support (B, KB, MB, GB, TB, PB)

### v1.2
- Fixed Select Duplicates to work reliably on all duplicate files
- Fixed Open Location opening multiple folders when files from same directory are selected
- Now opens each unique directory only once

### v1.1
- Fixed Settings window scrolling and layout glitches
- Improved Open Location to accurately open selected file's folder
- Enhanced real-time time estimation with moving average
- Optimized scanning performance with batch processing
- Fixed all edge cases for special character file handling
- Zero GUI glitches with proper widget management

### v1.0
- Initial release
- Basic duplicate file detection
- MD5 hash comparison
- Delete and Recycle Bin support

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/MAliXCS">MAliXCS</a>
</p>
