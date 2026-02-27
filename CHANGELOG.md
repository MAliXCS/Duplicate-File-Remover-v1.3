# Changelog

All notable changes to Duplicate File Remover will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Standalone executable (.exe) release
- Export scan results to CSV/JSON
- Dark mode theme
- Multi-language support
- Command-line interface (CLI) mode

## [1.3.0] - 2024-XX-XX

### Added
- Human-readable file size input support (B, KB, MB, GB, TB, PB)
- Real-time byte conversion display in settings
- Better error messages for invalid size formats

### Fixed
- Fixed "Open File Location" opening folders twice bug
- Changed from `subprocess.run(check=True)` to `subprocess.Popen` to prevent fallback triggering on Windows Explorer's non-zero exit codes

## [1.2.0] - 2024-XX-XX

### Added
- Smart duplicate selection that keeps one file per group
- Settings persistence using JSON file
- Auto-select duplicates option after scan
- File extension filter support
- Pattern exclusion support
- Hidden and system file skip options
- Real-time time estimation with moving average

### Fixed
- Fixed Select Duplicates to work reliably on all duplicate files
- Fixed Open Location opening multiple folders when files from same directory are selected
- Now opens each unique directory only once
- Fixed Settings window scrolling and layout glitches
- Improved Open Location to accurately open selected file's folder
- Optimized scanning performance with batch processing
- Fixed all edge cases for special character file handling
- Zero GUI glitches with proper widget management

## [1.1.0] - 2024-XX-XX

### Added
- Multiple hash algorithm support (MD5, SHA1, SHA256)
- File size limits (min/max)
- Progress bar with time estimation
- Detailed logging with timestamps
- Settings window with multiple options
- Recycle Bin integration (optional)

### Fixed
- Improved scanning performance
- Better error handling for locked files
- Fixed UI responsiveness during long scans

## [1.0.0] - 2024-XX-XX

### Added
- Initial release
- Basic duplicate file detection using MD5 hash
- Graphical user interface with tkinter
- Directory browsing and scanning
- Results display in treeview
- Delete selected files (permanent or Recycle Bin)
- Open file location in Explorer
- Select All / Deselect All functionality

---

## Version History Summary

| Version | Key Features |
|---------|-------------|
| 1.3.0 | Human-readable sizes, fixed double-open bug |
| 1.2.0 | Smart selection, settings persistence, filters |
| 1.1.0 | Multiple hash algorithms, size limits, progress bar |
| 1.0.0 | Initial release with basic functionality |

---

## Release Notes Format

Each release includes:

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security-related changes
