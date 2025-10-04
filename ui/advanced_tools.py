"""
Advanced Tools Panel for Power Users
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from pathlib import Path
from ..core.batch_processor import SmartBatchManager
from ..core.file_preview import PreviewDialog
from .styles import Styles
import logging

logger = logging.getLogger(__name__)

class AdvancedToolsPanel(ctk.CTkFrame):
    """Advanced tools panel for power users"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.batch_manager = SmartBatchManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup advanced tools UI"""
        # Create tabs for different advanced features
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Batch Operations Tab
        self.batch_tab = self.tab_view.add("Batch Operations")
        self.setup_batch_operations_tab()
        
        # Advanced Scanning Tab
        self.scan_tab = self.tab_view.add("Advanced Scanning")
        self.setup_advanced_scanning_tab()
        
        # System Tools Tab
        self.system_tab = self.tab_view.add("System Tools")
        self.setup_system_tools_tab()
    
    def setup_batch_operations_tab(self):
        """Setup batch operations tab"""
        # File selection
        file_frame = ctk.CTkFrame(self.batch_tab)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(file_frame, text="Selected Files:", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        self.file_listbox = ctk.CTkTextbox(file_frame, height=150)
        self.file_listbox.pack(fill="x", pady=5)
        self.file_listbox.configure(state="disabled")
        
        btn_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(btn_frame, text="Add Files", command=self.add_files).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Add Folder", command=self.add_folder).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Clear List", command=self.clear_file_list).pack(side="left", padx=5)
        
        # Operation selection
        op_frame = ctk.CTkFrame(self.batch_tab)
        op_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(op_frame, text="Batch Operation:", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        self.op_var = ctk.StringVar(value="hash")
        operations = [
            ("Compute Hashes", "hash"),
            ("Delete Files", "delete"),
            ("Move Files", "move"),
            ("Create Symlinks", "symlink")
        ]
        
        for text, value in operations:
            ctk.CTkRadioButton(
                op_frame, 
                text=text, 
                variable=self.op_var, 
                value=value
            ).pack(anchor="w", pady=2)
        
        # Operation-specific options
        self.options_frame = ctk.CTkFrame(self.batch_tab)
        self.options_frame.pack(fill="x", padx=10, pady=10)
        self.setup_operation_options()
        
        # Execute button
        self.execute_btn = ctk.CTkButton(
            self.batch_tab,
            text="Execute Batch Operation",
            command=self.execute_batch_operation,
            fg_color=Styles.COLOR_PRIMARY,
            font=Styles.FONT_BUTTON
        )
        self.execute_btn.pack(pady=20)
        
        # Results area
        self.results_text = ctk.CTkTextbox(self.batch_tab, height=200)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.results_text.configure(state="disabled")
    
    def setup_operation_options(self):
        """Setup operation-specific options"""
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        operation = self.op_var.get()
        
        if operation == "hash":
            self.setup_hash_options()
        elif operation == "move":
            self.setup_move_options()
        elif operation == "delete":
            self.setup_delete_options()
        elif operation == "symlink":
            self.setup_symlink_options()
    
    def setup_hash_options(self):
        """Setup hash computation options"""
        ctk.CTkLabel(self.options_frame, text="Hash Algorithm:").pack(anchor="w", pady=5)
        
        self.hash_algo = ctk.StringVar(value="md5")
        algo_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=["md5", "sha1", "sha256", "sha512"],
            variable=self.hash_algo
        )
        algo_menu.pack(fill="x", pady=5)
    
    def setup_move_options(self):
        """Setup move operation options"""
        ctk.CTkLabel(self.options_frame, text="Destination Directory:").pack(anchor="w", pady=5)
        
        move_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        move_frame.pack(fill="x", pady=5)
        
        self.dest_entry = ctk.CTkEntry(move_frame)
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            move_frame, 
            text="Browse", 
            command=self.browse_destination,
            width=80
        ).pack(side="right")
    
    def setup_delete_options(self):
        """Setup delete operation options"""
        self.use_trash = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.options_frame,
            text="Move to Recycle Bin (safer)",
            variable=self.use_trash
        ).pack(anchor="w", pady=5)
    
    def setup_symlink_options(self):
        """Setup symlink creation options"""
        ctk.CTkLabel(self.options_frame, text="Keep original files in:").pack(anchor="w", pady=5)
        
        symlink_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        symlink_frame.pack(fill="x", pady=5)
        
        self.original_dir_entry = ctk.CTkEntry(symlink_frame)
        self.original_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            symlink_frame, 
            text="Browse", 
            command=self.browse_original_dir,
            width=80
        ).pack(side="right")
    
    def setup_advanced_scanning_tab(self):
        """Setup advanced scanning tab"""
        # Custom pattern matching
        pattern_frame = ctk.CTkFrame(self.scan_tab)
        pattern_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(pattern_frame, text="Custom Search Patterns", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        ctk.CTkLabel(pattern_frame, text="Filename Patterns (regex):").pack(anchor="w", pady=2)
        self.pattern_entry = ctk.CTkEntry(pattern_frame, placeholder_text=".*\\.(jpg|png)$")
        self.pattern_entry.pack(fill="x", pady=5)
        
        ctk.CTkLabel(pattern_frame, text="Content Patterns (text):").pack(anchor="w", pady=2)
        self.content_pattern_entry = ctk.CTkEntry(pattern_frame, placeholder_text="search term")
        self.content_pattern_entry.pack(fill="x", pady=5)
        
        # Advanced filters
        filter_frame = ctk.CTkFrame(self.scan_tab)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(filter_frame, text="Advanced Filters", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        self.include_hidden = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            filter_frame,
            text="Include Hidden Files",
            variable=self.include_hidden
        ).pack(anchor="w", pady=2)
        
        self.include_system = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            filter_frame,
            text="Include System Files",
            variable=self.include_system
        ).pack(anchor="w", pady=2)
        
        # Scan scheduling
        schedule_frame = ctk.CTkFrame(self.scan_tab)
        schedule_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(schedule_frame, text="Scheduled Scanning", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        schedule_btn = ctk.CTkButton(
            schedule_frame,
            text="Schedule Regular Scan",
            command=self.schedule_scan
        )
        schedule_btn.pack(pady=5)
    
    def setup_system_tools_tab(self):
        """Setup system tools tab"""
        # Storage analysis
        storage_frame = ctk.CTkFrame(self.system_tab)
        storage_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(storage_frame, text="Storage Analysis", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        ctk.CTkButton(
            storage_frame,
            text="Analyze Disk Usage",
            command=self.analyze_disk_usage
        ).pack(pady=5)
        
        # System cleanup
        cleanup_frame = ctk.CTkFrame(self.system_tab)
        cleanup_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(cleanup_frame, text="System Cleanup", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        ctk.CTkButton(
            cleanup_frame,
            text="Find Temporary Files",
            command=self.find_temp_files
        ).pack(pady=5)
        
        # Performance monitoring
        perf_frame = ctk.CTkFrame(self.system_tab)
        perf_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(perf_frame, text="Performance", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        self.perf_label = ctk.CTkLabel(perf_frame, text="")
        self.perf_label.pack(pady=5)
        
        ctk.CTkButton(
            perf_frame,
            text="Refresh Performance Stats",
            command=self.update_performance_stats
        ).pack(pady=5)
    
    def add_files(self):
        """Add files to batch operation"""
        files = filedialog.askopenfilenames(title="Select files for batch operation")
        if files:
            self.update_file_list(files)
    
    def add_folder(self):
        """Add folder contents to batch operation"""
        folder = filedialog.askdirectory(title="Select folder for batch operation")
        if folder:
            # Recursively get all files
            file_paths = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_paths.append(os.path.join(root, file))
            self.update_file_list(file_paths)
    
    def update_file_list(self, new_files):
        """Update the file list display"""
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        
        for file_path in new_files:
            self.file_listbox.insert("end", f"{file_path}\n")
        
        self.file_listbox.configure(state="disabled")
        
        # Update execute button state
        has_files = len(new_files) > 0
        self.execute_btn.configure(state="normal" if has_files else "disabled")
    
    def clear_file_list(self):
        """Clear the file list"""
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        self.file_listbox.configure(state="disabled")
        self.execute_btn.configure(state="disabled")
    
    def browse_destination(self):
        """Browse for destination directory"""
        directory = filedialog.askdirectory(title="Select destination directory")
        if directory:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, directory)
    
    def browse_original_dir(self):
        """Browse for original files directory"""
        directory = filedialog.askdirectory(title="Select directory for original files")
        if directory:
            self.original_dir_entry.delete(0, "end")
            self.original_dir_entry.insert(0, directory)
    
    def execute_batch_operation(self):
        """Execute the selected batch operation"""
        # Get files from listbox
        file_text = self.file_listbox.get("1.0", "end-1c")
        file_paths = [line.strip() for line in file_text.split('\n') if line.strip()]
        
        if not file_paths:
            messagebox.showwarning("Warning", "No files selected for batch operation")
            return
        
        operation = self.op_var.get()
        
        try:
            if operation == "hash":
                self.execute_batch_hash(file_paths)
            elif operation == "delete":
                self.execute_batch_delete(file_paths)
            elif operation == "move":
                self.execute_batch_move(file_paths)
            elif operation == "symlink":
                self.execute_batch_symlink(file_paths)
                
        except Exception as e:
            logger.error(f"Batch operation failed: {e}")
            messagebox.showerror("Error", f"Batch operation failed: {str(e)}")
    
    def execute_batch_hash(self, file_paths):
        """Execute batch hash operation"""
        results = self.batch_manager.batch_hash(file_paths, self.hash_algo.get())
        
        # Display results
        self.display_results(results)
    
    def execute_batch_delete(self, file_paths):
        """Execute batch delete operation"""
        result = messagebox.askyesno(
            "Confirm Batch Delete",
            f"Are you sure you want to delete {len(file_paths)} files?",
            icon="warning"
        )
        
        if result:
            results = self.batch_manager.batch_delete(file_paths, self.use_trash.get())
            self.display_results(results)
    
    def execute_batch_move(self, file_paths):
        """Execute batch move operation"""
        destination = self.dest_entry.get().strip()
        if not destination:
            messagebox.showwarning("Warning", "Please select a destination directory")
            return
        
        results = self.batch_manager.batch_move(file_paths, destination)
        self.display_results(results)
    
    def execute_batch_symlink(self, file_paths):
        """Execute batch symlink operation"""
        messagebox.showinfo("Info", "Batch symlink creation is not yet implemented")
    
    def display_results(self, results):
        """Display batch operation results"""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        
        self.results_text.insert("end", "Batch Operation Results\n")
        self.results_text.insert("end", "=" * 50 + "\n\n")
        
        for key, value in results.items():
            if key not in ['failed_files', 'results']:
                self.results_text.insert("end", f"{key}: {value}\n")
        
        if 'failed_files' in results and results['failed_files']:
            self.results_text.insert("end", f"\nFailed files ({len(results['failed_files'])}):\n")
            for failed_file in results['failed_files']:
                self.results_text.insert("end", f"  - {failed_file}\n")
        
        self.results_text.configure(state="disabled")
    
    def schedule_scan(self):
        """Schedule regular scans"""
        messagebox.showinfo("Info", "Scan scheduling feature coming soon!")
    
    def analyze_disk_usage(self):
        """Analyze disk usage"""
        messagebox.showinfo("Info", "Disk usage analysis feature coming soon!")
    
    def find_temp_files(self):
        """Find temporary files"""
        messagebox.showinfo("Info", "Temporary file finder feature coming soon!")
    
    def update_performance_stats(self):
        """Update performance statistics"""
        import psutil
        
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats_text = (
            f"CPU: {cpu_percent:.1f}% | "
            f"Memory: {memory.percent:.1f}% | "
            f"Disk: {disk.percent:.1f}%"
        )
        
        self.perf_label.configure(text=stats_text)