# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.3.x   | :white_check_mark: |
| 1.2.x   | :white_check_mark: |
| 1.1.x   | :x:                |
| 1.0.x   | :x:                |

## Security Features

Duplicate File Remover is designed with security and data safety as top priorities:

### Data Protection

- **Local-Only Processing**: All file operations happen locally on your machine. No data is transmitted over the network.
- **Read-Only Scanning**: The scanning process only reads files to calculate content hashes. Files are never modified during scanning.
- **Recycle Bin Integration**: By default, deleted files are moved to the Windows Recycle Bin, allowing recovery if needed.
- **No Administrator Required**: The application runs with standard user privileges. No elevation is required for normal operation.

### File Handling Security

- **Special Character Support**: Properly handles filenames with special characters (parentheses, spaces, Unicode characters, etc.)
- **Long Path Support**: Uses Windows extended path syntax (`\\?\`) for paths exceeding 260 characters
- **Permission Handling**: Gracefully handles files without delete permissions by showing appropriate error messages
- **Locked File Detection**: Skips files that are currently in use by other applications

### Code Security

- **No External Network Calls**: The application does not make any network requests
- **No Telemetry**: No usage data or crash reports are collected
- **Open Source**: Full source code is available for audit and review
- **Minimal Dependencies**: Only uses well-established, audited libraries

## Reporting a Vulnerability

If you discover a security vulnerability in Duplicate File Remover, please follow these steps:

### Do NOT

- **Do NOT** open a public issue on GitHub
- **Do NOT** disclose the vulnerability publicly until it has been addressed
- **Do NOT** include exploit code in public communications

### DO

1. **Email the maintainer directly** at: security@yourdomain.com (replace with actual email)
2. **Include the following information**:
   - Clear description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact and severity assessment
   - Affected version(s)
   - Suggested fix or mitigation (if available)
   - Your contact information for follow-up questions

### Response Timeline

| Timeframe | Action |
|-----------|--------|
| Within 48 hours | Acknowledgment of receipt |
| Within 7 days | Initial assessment and response |
| Within 30 days | Fix released or timeline provided |

### Disclosure Policy

- We follow a **responsible disclosure** policy
- Once a fix is released, we will publicly acknowledge the reporter (with their permission)
- CVE numbers will be requested for serious vulnerabilities

## Security Best Practices for Users

### Before Using

1. **Backup Important Data**: Always maintain backups of critical files before using any file deletion tool
2. **Test First**: Run the application on a small test folder to understand its behavior
3. **Verify Results**: Use the "Open Location" feature to verify files before deletion

### During Use

1. **Enable Recycle Bin**: Keep "Move to Recycle Bin" enabled for an extra safety net
2. **Review Selections**: Carefully review selected files before confirming deletion
3. **Use Size Filters**: Set appropriate minimum file size to avoid scanning system files
4. **Exclude System Directories**: Do not scan Windows system directories

### Recommended Exclusions

Add these patterns to the Excluded Patterns list for safer operation:

```
*.tmp
*.log
Thumbs.db
desktop.ini
.DS_Store
$RECYCLE.BIN
System Volume Information
```

## Security Checklist

Before running Duplicate File Remover on important data:

- [ ] I have backups of my important files
- [ ] I understand how the application works
- [ ] I have tested it on non-critical files first
- [ ] "Move to Recycle Bin" is enabled in settings
- [ ] I have reviewed the files selected for deletion
- [ ] I have verified files using "Open Location" before deleting

## Known Limitations

The following are known limitations that are not considered security vulnerabilities:

1. **File Permissions**: The application cannot delete files for which the user does not have delete permissions
2. **In-Use Files**: Files currently open by other applications cannot be deleted
3. **Network Paths**: Performance on slow network drives may be reduced
4. **Very Large Files**: Hashing multi-GB files will take proportionally longer

## Security Updates

Security updates will be released as patch versions (e.g., 1.3.1). Users are encouraged to:

- Enable GitHub notifications for this repository
- Check the Releases page regularly
- Update to the latest version promptly

## Contact

For security-related inquiries:

- **Email**: security@yourdomain.com (replace with actual email)
- **GitHub**: [@MAliXCS](https://github.com/MAliXCS)
- **Instagram**: [@x404ctl](https://instagram.com/x404ctl)

---

Last updated: 2024
