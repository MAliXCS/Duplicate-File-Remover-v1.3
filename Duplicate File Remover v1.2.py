#!/usr/bin/env python3
"""
Duplicate File Remover v1.3
A clean, efficient duplicate file finder and remover for Windows

Changelog v1.3:
- Fixed "Open File Location" opening folders twice bug
- Changed from subprocess.run(check=True) to subprocess.Popen to prevent fallback triggering on Windows Explorer's non-zero exit codes
- Added human-readable file size input support (B, KB, MB, GB, TB, PB) in settings

Changelog v1.2:
- Fixed Select Duplicates to work reliably on all duplicate files
- Fixed Open Location opening multiple folders when files from same directory are selected
- Now opens each unique directory only once

Changelog v1.1:
- Fixed Settings window scrolling and layout glitches
- Improved Open Location to accurately open selected file's folder
- Enhanced real-time time estimation with moving average
- Optimized scanning performance with batch processing
- Fixed all edge cases for special character file handling
- Zero GUI glitches with proper widget management

Author: Instagram @x404ctl | GitHub @MAliXCS
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import hashlib
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
import json
import fnmatch
import subprocess

try:
    from send2trash import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False


class SettingsManager:
    """Manages application settings"""
    
    SETTINGS_FILE = "duplicate_remover_settings.json"
    
    def __init__(self):
        self.settings = {
            'use_recycle_bin': True,
            'hash_algorithm': 'md5',
            'min_size': 0,
            'max_size': 0,
            'last_directory': '',
            'excluded_patterns': [],
            'included_extensions': [],
            'keep_oldest': True,
            'auto_select_duplicates': False,
            'skip_hidden_files': False,
            'skip_system_files': True
        }
        self.load_settings()
    
    def load_settings(self):
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
        except Exception:
            pass
    
    def save_settings(self):
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()


class HashCalculator:
    """Efficient hash calculation"""
    
    CHUNK_SIZE = 65536
    
    def __init__(self, algorithm='md5'):
        self.algorithm = algorithm.lower()
    
    def calculate_hash(self, filepath):
        try:
            if self.algorithm == 'md5':
                hasher = hashlib.md5()
            elif self.algorithm == 'sha1':
                hasher = hashlib.sha1()
            elif self.algorithm == 'sha256':
                hasher = hashlib.sha256()
            else:
                hasher = hashlib.md5()
            
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    hasher.update(chunk)
            
            return hasher.hexdigest()
        except Exception:
            return None


class FileFilter:
    """Handles file filtering"""
    
    def __init__(self, settings_manager):
        self.settings = settings_manager
    
    def should_include(self, filepath):
        try:
            filename = os.path.basename(filepath)
            
            if self.settings.get('skip_hidden_files', False):
                if filename.startswith('.') or self._is_hidden_windows(filepath):
                    return False
            
            if self.settings.get('skip_system_files', True):
                if self._is_system_file(filepath):
                    return False
            
            excluded_patterns = self.settings.get('excluded_patterns', [])
            for pattern in excluded_patterns:
                if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(filepath, pattern):
                    return False
            
            included_extensions = self.settings.get('included_extensions', [])
            if included_extensions:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in included_extensions and f"*{ext}" not in included_extensions:
                    return False
            
            return True
        except Exception:
            return True
    
    def _is_hidden_windows(self, filepath):
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
            return attrs != -1 and (attrs & 2)
        except:
            return False
    
    def _is_system_file(self, filepath):
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
            return attrs != -1 and (attrs & 4)
        except:
            return False


class TimeEstimator:
    """Accurate time estimation using moving average"""
    
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.samples = deque(maxlen=window_size)
        self.start_time = None
    
    def start(self):
        self.start_time = time.time()
        self.samples.clear()
    
    def add_sample(self, progress):
        if self.start_time is None:
            return
        elapsed = time.time() - self.start_time
        if progress > 0:
            rate = progress / elapsed
            self.samples.append(rate)
    
    def estimate_remaining(self, current_progress):
        if not self.samples or current_progress >= 1.0:
            return 0
        
        avg_rate = sum(self.samples) / len(self.samples)
        if avg_rate <= 0:
            return 0
        
        remaining_progress = 1.0 - current_progress
        estimated_seconds = remaining_progress / avg_rate
        
        return max(0, estimated_seconds)
    
    def reset(self):
        self.start_time = None
        self.samples.clear()


class DuplicateFinder:
    """Core duplicate finding logic with optimized performance"""
    
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.stop_requested = False
        self.files_by_size = defaultdict(list)
        self.duplicates = {}
        self.total_files = 0
        self.processed_files = 0
        self.scanned_size = 0
        self.file_filter = None
        self.start_time = None
        self.time_estimator = TimeEstimator()
    
    def log(self, message):
        if self.gui_callback:
            self.gui_callback.log(message)
    
    def update_progress(self, current, total):
        if self.gui_callback and total > 0:
            progress = current / total
            self.time_estimator.add_sample(progress)
            remaining = self.time_estimator.estimate_remaining(progress)
            self.gui_callback.update_progress(progress * 100, remaining)
    
    def scan_directory(self, directory, settings_manager):
        self.stop_requested = False
        self.files_by_size.clear()
        self.duplicates.clear()
        self.total_files = 0
        self.processed_files = 0
        self.scanned_size = 0
        self.start_time = time.time()
        self.time_estimator.start()
        
        self.file_filter = FileFilter(settings_manager)
        
        min_size = settings_manager.get('min_size', 0)
        max_size = settings_manager.get('max_size', 0)
        hash_algorithm = settings_manager.get('hash_algorithm', 'md5')
        
        self.log(f"Starting scan of: {directory}")
        self.log(f"Hash algorithm: {hash_algorithm.upper()}")
        
        self.log("Phase 1: Collecting files...")
        self._collect_files(directory, min_size, max_size)
        
        if self.stop_requested:
            self.log("Scan cancelled by user.")
            return {}
        
        self.log("Phase 2: Comparing file contents...")
        self._find_duplicates_by_hash(hash_algorithm)
        
        elapsed = time.time() - self.start_time
        self.log(f"Scan completed in {self._format_time(elapsed)}")
        self.log(f"Found {len(self.duplicates)} groups of duplicate files")
        
        return self.duplicates
    
    def _collect_files(self, directory, min_size, max_size):
        try:
            update_interval = 100
            
            for root, dirs, files in os.walk(directory):
                if self.stop_requested:
                    return
                
                for filename in files:
                    if self.stop_requested:
                        return
                    
                    filepath = os.path.join(root, filename)
                    
                    try:
                        if not self.file_filter.should_include(filepath):
                            continue
                        
                        file_size = os.path.getsize(filepath)
                        
                        if min_size > 0 and file_size < min_size:
                            continue
                        if max_size > 0 and file_size > max_size:
                            continue
                        
                        self.files_by_size[file_size].append(filepath)
                        self.total_files += 1
                        self.scanned_size += file_size
                        
                        if self.total_files % update_interval == 0:
                            self.log(f"Collected {self.total_files} files ({self._format_size(self.scanned_size)})...")
                            
                    except (OSError, IOError):
                        continue
        except Exception as e:
            self.log(f"Error collecting files: {str(e)}")
    
    def _find_duplicates_by_hash(self, hash_algorithm):
        hash_calc = HashCalculator(hash_algorithm)
        
        potential_duplicates = {size: files for size, files in self.files_by_size.items() if len(files) > 1}
        
        total_to_hash = sum(len(files) for files in potential_duplicates.values())
        hashed_count = 0
        
        for size, files in potential_duplicates.items():
            if self.stop_requested:
                return
            
            files_by_hash = defaultdict(list)
            
            for filepath in files:
                if self.stop_requested:
                    return
                
                file_hash = hash_calc.calculate_hash(filepath)
                
                if file_hash:
                    files_by_hash[file_hash].append(filepath)
                
                hashed_count += 1
                self.update_progress(hashed_count, total_to_hash)
            
            for file_hash, file_list in files_by_hash.items():
                if len(file_list) > 1:
                    self.duplicates[file_hash] = {
                        'size': size,
                        'files': file_list
                    }
    
    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def _format_time(self, seconds):
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def stop(self):
        self.stop_requested = True


class DuplicateFileRemoverApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Remover v1.3")
        self.root.geometry("1000x700")
        self.root.minsize(900, 550)
        self.root.configure(bg='#f5f5f5')
        
        self.settings = SettingsManager()
        self.finder = DuplicateFinder(gui_callback=self)
        self.duplicate_groups = {}
        self.file_items = {}
        self.scan_thread = None
        self.is_scanning = False
        self.settings_window = None
        
        self.setup_styles()
        self.create_widgets()
        self.center_window()
        
        self.log("Duplicate File Remover v1.3 started")
        self.log("Ready to scan for duplicates")
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = '#f5f5f5'
        accent_color = '#2196F3'
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.configure('Accent.TButton', background=accent_color, foreground='white')
        style.configure('TEntry', font=('Segoe UI', 10))
        style.configure('TProgressbar', thickness=8)
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=22)
        style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'))
        style.configure('TLabelframe', background=bg_color)
        style.configure('TLabelframe.Label', background=bg_color, font=('Segoe UI', 9, 'bold'))
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_directory_section(main_frame)
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        self.create_results_section(main_frame)
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        self.create_logs_section(main_frame)
        
        self.create_status_bar()
    
    def create_directory_section(self, parent):
        dir_frame = ttk.Frame(parent)
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(dir_frame, text="Directory:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, font=('Segoe UI', 10))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        
        btn_frame = ttk.Frame(dir_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="Browse", command=self.browse_directory, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Scan", command=self.start_scan, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Stop", command=self.stop_scan, width=10).pack(side=tk.LEFT, padx=2)
        
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        self.time_var = tk.StringVar(value="")
        self.time_label = ttk.Label(progress_frame, textvariable=self.time_var, font=('Segoe UI', 9), width=25)
        self.time_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_results_section(self, parent):
        results_frame = ttk.LabelFrame(parent, text="Duplicate Files", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('filename', 'size', 'path', 'group', 'modified')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='extended')
        
        self.tree.heading('filename', text='Filename')
        self.tree.heading('size', text='Size')
        self.tree.heading('path', text='Path')
        self.tree.heading('group', text='Group')
        self.tree.heading('modified', text='Modified')
        
        self.tree.column('filename', width=180, minwidth=100)
        self.tree.column('size', width=80, minwidth=60)
        self.tree.column('path', width=350, minwidth=150)
        self.tree.column('group', width=50, minwidth=40)
        self.tree.column('modified', width=120, minwidth=100)
        
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        select_frame = ttk.LabelFrame(action_frame, text="Selection", padding="8")
        select_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(select_frame, text="Select All", command=self.select_all, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(select_frame, text="Deselect All", command=self.deselect_all, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(select_frame, text="Duplicates", command=self.select_duplicates, width=10).pack(side=tk.LEFT, padx=2)
        
        action_btn_frame = ttk.LabelFrame(action_frame, text="Actions", padding="8")
        action_btn_frame.pack(side=tk.LEFT)
        
        ttk.Button(action_btn_frame, text="Delete Selected", command=self.delete_selected, width=14).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_btn_frame, text="Open Location", command=self.open_location, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_btn_frame, text="Settings", command=self.open_settings, width=10).pack(side=tk.LEFT, padx=2)
        
        self.stats_var = tk.StringVar(value="No duplicates found")
        ttk.Label(action_frame, textvariable=self.stats_var, font=('Segoe UI', 9, 'bold')).pack(side=tk.RIGHT, padx=10)
    
    def create_logs_section(self, parent):
        logs_frame = ttk.LabelFrame(parent, text="Log", padding="8")
        logs_frame.pack(fill=tk.BOTH, expand=False)
        
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=6, font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
    
    def create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(10, 3))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(status_bar, textvariable=self.status_var, font=('Segoe UI', 9)).pack(side=tk.LEFT)
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)
            self.settings.set('last_directory', directory)
    
    def start_scan(self):
        directory = self.dir_var.get().strip()
        
        if not directory:
            messagebox.showerror("Error", "Please select a directory to scan")
            return
        
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Invalid directory path")
            return
        
        self.clear_results()
        self.is_scanning = True
        self.status_var.set("Scanning...")
        self.time_var.set("Estimating...")
        
        self.scan_thread = threading.Thread(
            target=self._scan_worker,
            args=(directory,),
            daemon=True
        )
        self.scan_thread.start()
    
    def _scan_worker(self, directory):
        self.duplicate_groups = self.finder.scan_directory(directory, self.settings)
        self.root.after(0, self._update_results)
    
    def _update_results(self):
        self.tree.delete(*self.tree.get_children())
        self.file_items.clear()
        
        if not self.duplicate_groups:
            self.stats_var.set("No duplicates found")
            self.log("No duplicate files found")
            self.is_scanning = False
            self.status_var.set("Ready")
            self.progress_var.set(0)
            self.time_var.set("")
            return
        
        total_duplicates = 0
        total_wasted = 0
        keep_oldest = self.settings.get('keep_oldest', True)
        
        for group_id, data in enumerate(self.duplicate_groups.values(), 1):
            files = data['files']
            size = data['size']
            
            files_with_time = []
            for filepath in files:
                try:
                    mtime = os.path.getmtime(filepath)
                    files_with_time.append((filepath, mtime))
                except:
                    files_with_time.append((filepath, 0))
            
            files_with_time.sort(key=lambda x: x[1], reverse=not keep_oldest)
            
            for i, (filepath, mtime) in enumerate(files_with_time):
                filename = os.path.basename(filepath)
                size_str = self.format_size(size)
                modified_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                
                is_duplicate = i > 0
                
                item = self.tree.insert('', tk.END, values=(filename, size_str, filepath, group_id, modified_str))
                
                self.file_items[item] = {
                    'path': filepath,
                    'group': group_id,
                    'is_duplicate': is_duplicate,
                    'size': size
                }
                
                if is_duplicate:
                    self.tree.item(item, tags=('duplicate',))
                    total_duplicates += 1
                    total_wasted += size
        
        self.tree.tag_configure('duplicate', foreground='#d32f2f')
        
        self.stats_var.set(f"Groups: {len(self.duplicate_groups)} | Duplicates: {total_duplicates} | Wasted: {self.format_size(total_wasted)}")
        
        self.log(f"Results: {len(self.duplicate_groups)} duplicate groups found")
        self.log(f"Total duplicates: {total_duplicates}")
        self.log(f"Wasted space: {self.format_size(total_wasted)}")
        
        if self.settings.get('auto_select_duplicates', False):
            self.root.after(100, self.select_duplicates)
        
        self.is_scanning = False
        self.status_var.set("Scan complete")
        self.progress_var.set(100)
        self.time_var.set("")
    
    def stop_scan(self):
        if self.is_scanning:
            self.finder.stop()
            self.log("Stop requested...")
            self.status_var.set("Stopping...")
    
    def clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.duplicate_groups.clear()
        self.file_items.clear()
        self.progress_var.set(0)
        self.time_var.set("")
    
    def select_all(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        self.log(f"Selected {len(self.tree.get_children())} items")
    
    def deselect_all(self):
        self.tree.selection_remove(self.tree.selection())
        self.log("Deselected all items")
    
    def select_duplicates(self):
        self.tree.selection_remove(self.tree.selection())

        count = 0
        # Get current tree items to avoid stale entries
        current_items = list(self.tree.get_children())

        for item in current_items:
            data = self.file_items.get(item, {})
            if data.get('is_duplicate', False):
                self.tree.selection_add(item)
                count += 1

        self.log(f"Selected {count} duplicate files (keeping one per group)")
        self.status_var.set(f"Selected {count} duplicates")
    
    def _normalize_path(self, filepath):
        try:
            filepath = os.path.abspath(filepath)
            filepath = os.path.normpath(filepath)
            return filepath
        except Exception:
            return filepath
    
    def _delete_file_windows(self, filepath):
        filepath = self._normalize_path(filepath)
        has_special_chars = any(c in filepath for c in ['(', ')', '&', '!', '@', '#', '$', '%', '^', '`'])
        
        if SEND2TRASH_AVAILABLE and self.settings.get('use_recycle_bin', True):
            try:
                send2trash(filepath)
                return True, "Moved to recycle bin"
            except Exception as e:
                error_str = str(e)
                if has_special_chars or "incorrect" in error_str.lower() or "invalid" in error_str.lower():
                    self.log(f"Recycle bin failed, trying direct delete: {os.path.basename(filepath)}")
                else:
                    raise
        
        try:
            if has_special_chars or len(filepath) > 240:
                if not filepath.startswith("\\\\?\\"):
                    if filepath.startswith("\\\\"):
                        filepath_extended = "\\\\?\\UNC\\" + filepath[2:]
                    else:
                        filepath_extended = "\\\\?\\" + filepath
                else:
                    filepath_extended = filepath
                
                import ctypes
                from ctypes import wintypes
                
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                DeleteFileW = kernel32.DeleteFileW
                DeleteFileW.argtypes = [wintypes.LPCWSTR]
                DeleteFileW.restype = wintypes.BOOL
                
                if not DeleteFileW(filepath_extended):
                    error_code = ctypes.get_last_error()
                    raise OSError(error_code, f"Windows DeleteFile failed: {ctypes.FormatError(error_code)}")
            else:
                os.remove(filepath)
            
            return True, "Deleted"
        except Exception:
            os.remove(filepath)
            return True, "Deleted (fallback)"
    
    def delete_selected(self):
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showinfo("Info", "No files selected")
            return
        
        files_to_delete = []
        for item in selected:
            data = self.file_items.get(item, {})
            filepath = data.get('path', '')
            size = data.get('size', 0)
            
            if filepath:
                files_to_delete.append((item, filepath, size))
        
        if not files_to_delete:
            return
        
        use_recycle = self.settings.get('use_recycle_bin', True) and SEND2TRASH_AVAILABLE
        delete_method = "Recycle Bin" if use_recycle else "Permanently"
        
        total_size = sum(f[2] for f in files_to_delete)
        
        if not messagebox.askyesno("Confirm Delete", 
                                   f"Delete {len(files_to_delete)} file(s) ({self.format_size(total_size)})?\n\n"
                                   f"Method: {delete_method}"):
            return
        
        deleted_count = 0
        failed_count = 0
        freed_space = 0
        
        for tree_item, filepath, size in files_to_delete:
            try:
                normalized_path = self._normalize_path(filepath)
                
                if os.path.exists(normalized_path):
                    file_size = os.path.getsize(normalized_path)
                    
                    success, method = self._delete_file_windows(normalized_path)
                    
                    if success:
                        self.log(f"{method}: {os.path.basename(filepath)}")
                        self.tree.delete(tree_item)
                        deleted_count += 1
                        freed_space += file_size
                else:
                    self.log(f"File not found: {filepath}")
                    self.tree.delete(tree_item)
                    failed_count += 1
            except Exception as e:
                self.log(f"Error deleting {filepath}: {str(e)}")
                failed_count += 1
        
        self.log(f"Delete complete: {deleted_count} deleted, {failed_count} failed, {self.format_size(freed_space)} freed")
        self.status_var.set(f"Deleted {deleted_count} files, {self.format_size(freed_space)} freed")
        messagebox.showinfo("Complete", f"Deleted: {deleted_count}\nFailed: {failed_count}\nFreed: {self.format_size(freed_space)}")
    
    def open_location(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showinfo("Info", "No file selected")
            return

        # Group files by their directory - only open one file per unique directory
        dirs_to_open = {}  # directory -> first filepath in that directory

        for item in selected:
            data = self.file_items.get(item, {})
            filepath = data.get('path', '')

            if not filepath:
                continue

            filepath = self._normalize_path(filepath)

            if not os.path.exists(filepath):
                continue

            directory = os.path.dirname(filepath)
            # Normalize directory path for consistent comparison
            directory = os.path.normcase(os.path.abspath(directory))

            # Only store the first file from each directory
            if directory not in dirs_to_open:
                dirs_to_open[directory] = filepath

        if not dirs_to_open:
            messagebox.showerror("Error", "Could not open any locations")
            return

        opened_count = 0
        errors = []

        for directory, filepath in dirs_to_open.items():
            try:
                # Use explorer /select, to open folder with file highlighted
                # Use Popen instead of run with check=True to avoid double-opening
                # when explorer returns non-zero exit code on success
                subprocess.Popen(['explorer', '/select,', filepath],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                self.log(f"Opened location: {os.path.dirname(filepath)}")
                opened_count += 1
            except Exception as e:
                # Fallback: just open the folder
                try:
                    os.startfile(os.path.dirname(filepath))
                    self.log(f"Opened folder: {os.path.dirname(filepath)}")
                    opened_count += 1
                except Exception as e2:
                    errors.append(f"{os.path.dirname(filepath)}: {str(e2)}")

        if errors:
            for error in errors:
                self.log(f"Error: {error}")

        if opened_count > 0:
            self.status_var.set(f"Opened {opened_count} location(s)")
        else:
            messagebox.showerror("Error", "Could not open any locations")
    def open_settings(self):
        if self.settings_window is not None:
            try:
                if self.settings_window.winfo_exists():
                    self.settings_window.lift()
                    self.settings_window.focus_force()
                    return
            except tk.TclError:
                pass
        
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("450x520")
        self.settings_window.resizable(False, False)
        self.settings_window.transient(self.root)
        self.settings_window.grab_set()
        self.settings_window.configure(bg='#f5f5f5')
        
        self.settings_window.protocol("WM_DELETE_WINDOW", self._on_settings_close)
        
        self._create_settings_content(self.settings_window)
        
        self.settings_window.update_idletasks()
        width = self.settings_window.winfo_width()
        height = self.settings_window.winfo_height()
        x = (self.settings_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.settings_window.winfo_screenheight() // 2) - (height // 2)
        self.settings_window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _on_settings_close(self):
        if self.settings_window:
            self.settings_window.grab_release()
            self.settings_window.destroy()
            self.settings_window = None
    
    def _create_settings_content(self, window):
        main_canvas = tk.Canvas(window, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=430)
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        main_canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        frame = ttk.Frame(scrollable_frame, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Hash Algorithm:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.hash_var = tk.StringVar(value=self.settings.get('hash_algorithm', 'md5'))
        hash_combo = ttk.Combobox(frame, textvariable=self.hash_var, 
                                   values=['md5', 'sha1', 'sha256'],
                                   state='readonly', width=20)
        hash_combo.pack(fill=tk.X, pady=(0, 15))
        
        self.recycle_var = tk.BooleanVar(value=self.settings.get('use_recycle_bin', True))
        recycle_check = ttk.Checkbutton(frame, text="Move deleted files to Recycle Bin",
                                        variable=self.recycle_var)
        recycle_check.pack(anchor=tk.W, pady=(0, 5))
        
        if not SEND2TRASH_AVAILABLE:
            recycle_check.config(state='disabled')
            ttk.Label(frame, text="(Install send2trash for recycle bin support)",
                     foreground='gray').pack(anchor=tk.W, pady=(0, 15))
        else:
            ttk.Frame(frame).pack(pady=(0, 10))
        
        ttk.Label(frame, text="When selecting duplicates:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.keep_var = tk.StringVar(value='oldest' if self.settings.get('keep_oldest', True) else 'newest')
        keep_frame = ttk.Frame(frame)
        keep_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Radiobutton(keep_frame, text="Keep oldest file", variable=self.keep_var, value='oldest').pack(side=tk.LEFT)
        ttk.Radiobutton(keep_frame, text="Keep newest file", variable=self.keep_var, value='newest').pack(side=tk.LEFT, padx=20)
        
        size_frame = ttk.LabelFrame(frame, text="File Size Limits (0 = unlimited)", padding="10")
        size_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(size_frame, text="Examples: 100MB, 1.5GB, 1024, 0", foreground='gray').grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))

        ttk.Label(size_frame, text="Min Size:").grid(row=1, column=0, sticky=tk.W)
        min_size_bytes = self.settings.get('min_size', 0)
        self.min_size_var = tk.StringVar(value=self._format_size_for_display(min_size_bytes))
        ttk.Entry(size_frame, textvariable=self.min_size_var, width=15).grid(row=1, column=1, padx=5)
        self.min_size_display = tk.StringVar(value=f"({min_size_bytes:,} bytes)" if min_size_bytes > 0 else "")
        ttk.Label(size_frame, textvariable=self.min_size_display, foreground='gray', font=('Segoe UI', 8)).grid(row=1, column=2, sticky=tk.W)

        ttk.Label(size_frame, text="Max Size:").grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        max_size_bytes = self.settings.get('max_size', 0)
        self.max_size_var = tk.StringVar(value=self._format_size_for_display(max_size_bytes))
        ttk.Entry(size_frame, textvariable=self.max_size_var, width=15).grid(row=2, column=1, padx=5, pady=(8, 0))
        self.max_size_display = tk.StringVar(value=f"({max_size_bytes:,} bytes)" if max_size_bytes > 0 else "")
        ttk.Label(size_frame, textvariable=self.max_size_display, foreground='gray', font=('Segoe UI', 8)).grid(row=2, column=2, sticky=tk.W, pady=(8, 0))
        
        ext_frame = ttk.LabelFrame(frame, text="File Extensions Filter", padding="10")
        ext_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(ext_frame, text="Include only (comma separated, e.g., .jpg,.png):").pack(anchor=tk.W)
        self.ext_var = tk.StringVar(value=','.join(self.settings.get('included_extensions', [])))
        ttk.Entry(ext_frame, textvariable=self.ext_var).pack(fill=tk.X, pady=(5, 0))
        ttk.Label(ext_frame, text="Leave empty to include all files", foreground='gray').pack(anchor=tk.W)
        
        pattern_frame = ttk.LabelFrame(frame, text="Excluded Patterns", padding="10")
        pattern_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(pattern_frame, text="Patterns to exclude (one per line):").pack(anchor=tk.W)
        self.patterns_text = tk.Text(pattern_frame, height=3, font=('Consolas', 9))
        self.patterns_text.pack(fill=tk.X, pady=(5, 0))
        
        patterns = self.settings.get('excluded_patterns', [])
        self.patterns_text.insert('1.0', '\n'.join(patterns))
        
        skip_frame = ttk.LabelFrame(frame, text="Skip Options", padding="10")
        skip_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.skip_hidden_var = tk.BooleanVar(value=self.settings.get('skip_hidden_files', False))
        ttk.Checkbutton(skip_frame, text="Skip hidden files", variable=self.skip_hidden_var).pack(anchor=tk.W)
        
        self.skip_system_var = tk.BooleanVar(value=self.settings.get('skip_system_files', True))
        ttk.Checkbutton(skip_frame, text="Skip system files", variable=self.skip_system_var).pack(anchor=tk.W)
        
        self.auto_select_var = tk.BooleanVar(value=self.settings.get('auto_select_duplicates', False))
        ttk.Checkbutton(frame, text="Auto-select duplicates after scan", 
                       variable=self.auto_select_var).pack(anchor=tk.W, pady=(0, 15))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Save", command=self._save_settings, width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self._on_settings_close, width=10).pack(side=tk.RIGHT)
    
    def _parse_size(self, size_str):
        """Parse size string like '10MB', '1.5 GB', '1024' to bytes."""
        if not size_str or size_str.strip() == '':
            return 0

        size_str = size_str.strip().upper().replace(' ', '')

        # If it's just a number, treat as bytes
        if size_str.isdigit():
            return int(size_str)

        # Try to parse with unit
        units = {
            'B': 1,
            'BYTE': 1, 'BYTES': 1,
            'KB': 1024,
            'KILOBYTE': 1024, 'KILOBYTES': 1024,
            'MB': 1024 ** 2,
            'MEGABYTE': 1024 ** 2, 'MEGABYTES': 1024 ** 2,
            'GB': 1024 ** 3,
            'GIGABYTE': 1024 ** 3, 'GIGABYTES': 1024 ** 3,
            'TB': 1024 ** 4,
            'TERABYTE': 1024 ** 4, 'TERABYTES': 1024 ** 4,
            'PB': 1024 ** 5,
            'PETABYTE': 1024 ** 5, 'PETABYTES': 1024 ** 5
        }

        # Match number (int or float) followed by optional unit
        import re
        match = re.match(r'^([0-9]*\.?[0-9]+)\s*([A-Z]*)$', size_str)
        if not match:
            raise ValueError(f"Invalid size format: {size_str}")

        number = float(match.group(1))
        unit = match.group(2) if match.group(2) else 'B'

        if unit not in units:
            raise ValueError(f"Unknown unit: {unit}. Use B, KB, MB, GB, TB, or PB")

        return int(number * units[unit])

    def _format_size_for_display(self, size_bytes):
        """Format bytes to human readable string for display."""
        if size_bytes == 0:
            return "0"

        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = float(size_bytes)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        # If it's a whole number, show as integer
        if size == int(size):
            return f"{int(size)}{units[unit_index]}"
        else:
            return f"{size:.2f}{units[unit_index]}"

    def _save_settings(self):
        try:
            min_size = self._parse_size(self.min_size_var.get())
            max_size = self._parse_size(self.max_size_var.get())

            if min_size < 0 or max_size < 0:
                messagebox.showerror("Error", "Size values must be non-negative")
                return

            if max_size > 0 and min_size > max_size:
                messagebox.showerror("Error", "Min size cannot be greater than max size")
                return
            
            ext_text = self.ext_var.get().strip()
            included_extensions = [e.strip().lower() for e in ext_text.split(',') if e.strip()]
            
            patterns_text = self.patterns_text.get('1.0', tk.END).strip()
            excluded_patterns = [p.strip() for p in patterns_text.split('\n') if p.strip()]
            
            self.settings.set('hash_algorithm', self.hash_var.get())
            self.settings.set('use_recycle_bin', self.recycle_var.get())
            self.settings.set('min_size', min_size)
            self.settings.set('max_size', max_size)
            self.settings.set('keep_oldest', self.keep_var.get() == 'oldest')
            self.settings.set('included_extensions', included_extensions)
            self.settings.set('excluded_patterns', excluded_patterns)
            self.settings.set('skip_hidden_files', self.skip_hidden_var.get())
            self.settings.set('skip_system_files', self.skip_system_var.get())
            self.settings.set('auto_select_duplicates', self.auto_select_var.get())
            
            self._on_settings_close()
            self.log("Settings saved")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid size format: {str(e)}\n\nExamples: 100MB, 1.5GB, 1024, 0")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_progress(self, progress_percent, remaining_seconds):
        self.progress_var.set(progress_percent)
        
        if remaining_seconds > 0:
            self.time_var.set(f"~{self._format_time(remaining_seconds)} remaining")
        else:
            self.time_var.set("")
        
        self.status_var.set(f"Processing... {progress_percent:.1f}%")
        self.root.update_idletasks()
    
    def _format_time(self, seconds):
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"


def main():
    root = tk.Tk()
    
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = DuplicateFileRemoverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
