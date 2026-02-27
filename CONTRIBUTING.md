# Contributing to Duplicate File Remover

Thank you for your interest in contributing to Duplicate File Remover! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept responsibility for our mistakes

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please:

1. Check the [existing issues](https://github.com/MAliXCS/DuplicateFileRemover/issues) to avoid duplicates
2. Use the latest version to verify the bug still exists

When reporting a bug, include:

- **Clear title** - Summarize the issue
- **Description** - Explain what happened vs what you expected
- **Steps to reproduce** - Numbered list of actions
- **Environment** - Windows version, Python version
- **Screenshots** - If applicable
- **Error messages** - Copy-paste any error text

**Template:**
```markdown
**Bug Description:**
[Clear description]

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
[What you expected]

**Actual Behavior:**
[What actually happened]

**Environment:**
- OS: [e.g., Windows 10 22H2]
- Python: [e.g., 3.10.4]
- App Version: [e.g., 1.3.0]

**Screenshots:**
[If applicable]
```

### Suggesting Features

Feature requests are welcome! Please:

1. Check if the feature has already been requested
2. Provide a clear use case
3. Explain why it would benefit users

**Template:**
```markdown
**Feature Request:**
[Clear description]

**Use Case:**
[How would you use this?]

**Proposed Solution:**
[Your idea for implementation]

**Alternatives:**
[Other approaches you've considered]
```

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/DuplicateFileRemover.git
   cd DuplicateFileRemover
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

3. **Make your changes**
   - Follow the code style (see below)
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   - Run the application and verify it works
   - Test on different file types and sizes
   - Test edge cases

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   **Commit message format:**
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting)
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Windows 7 SP1 or higher
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/DuplicateFileRemover.git
cd DuplicateFileRemover

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python duplicate_file_remover.py
```

## Code Style

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters max
- **Imports**: Group by standard library, third-party, local
- **Docstrings**: Use triple quotes for classes and functions

**Example:**
```python
def calculate_hash(self, filepath):
    """
    Calculate the hash of a file.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        str: Hex digest of the hash, or None if error
    """
    try:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            while chunk := f.read(self.CHUNK_SIZE):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `DuplicateFinder` |
| Functions | snake_case | `calculate_hash` |
| Variables | snake_case | `file_size` |
| Constants | UPPER_CASE | `CHUNK_SIZE` |
| Private | _leading_underscore | `_internal_method` |

## Testing

### Manual Testing Checklist

Before submitting a PR, verify:

- [ ] Application starts without errors
- [ ] Browse button opens folder dialog
- [ ] Scan completes successfully
- [ ] Duplicate files are correctly identified
- [ ] Select All / Deselect All work
- [ ] Select Duplicates works correctly
- [ ] Delete Selected moves files to Recycle Bin
- [ ] Open Location opens correct folder
- [ ] Settings save and load correctly
- [ ] File size limits work (e.g., 100MB)
- [ ] Extension filters work
- [ ] Pattern exclusions work
- [ ] Hidden/system file options work
- [ ] Long paths (>260 chars) work
- [ ] Files with special characters work

### Test Files

Create test data for verification:

```python
# test_data/create_test_files.py
import os
import hashlib

# Create duplicate files
test_dir = "test_data"
os.makedirs(test_dir, exist_ok=True)

# Create original
with open(f"{test_dir}/original.txt", "w") as f:
    f.write("This is test content")

# Create duplicate
with open(f"{test_dir}/duplicate.txt", "w") as f:
    f.write("This is test content")

# Create different file
with open(f"{test_dir}/different.txt", "w") as f:
    f.write("Different content")

print("Test files created!")
```

## Documentation

Update documentation when:

- Adding new features
- Changing existing behavior
- Fixing bugs that affect user workflow

Update these files as needed:
- `README.md` - User-facing documentation
- `CHANGELOG.md` - Version history
- Code comments - For complex logic

## Release Process

1. Update version number in:
   - `duplicate_file_remover.py` (title and log messages)
   - `README.md` (changelog)

2. Update `CHANGELOG.md` with new features/fixes

3. Create a GitHub Release with:
   - Version tag (e.g., `v1.4.0`)
   - Release notes
   - Binary attachment (if applicable)

## Questions?

- Open a [GitHub Discussion](https://github.com/MAliXCS/DuplicateFileRemover/discussions)
- Contact: [@x404ctl on Instagram](https://instagram.com/x404ctl)

Thank you for contributing! 🎉
