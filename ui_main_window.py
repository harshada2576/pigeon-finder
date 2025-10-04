"""
Fixed Main Window - Absolute Imports
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import logging
from pathlib import Path

# Absolute imports
from core_file_scanner import FileScanner
from core_pigeonhole_engine import PigeonholeEngine
from core_duplicate_manager import DuplicateManager
from ui_results_panel import ResultsPanel
from ui_stats_panel import StatsPanel
from ui_styles import Styles

logger = logging.getLogger(__name__)

class MainWindow(ctk.CTk):
    """Main application window with absolute imports"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.scanner = FileScanner()
        self.engine = PigeonholeEngine()
        self.manager = DuplicateManager()
        
        # UI state
        self.is_scanning = False
        self.current_directory = ""
        
        self.setup_window()
        self.create_widgets()
        self.apply_styles()
        
    def setup_window(self):
        """Configure main window"""
        self.title("Pigeon Finder - Duplicate File Detective")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
    def create_widgets(self):
        """Create all UI widgets"""
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
    def create_sidebar(self):
        """Create sidebar with controls"""
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            sidebar, 
            text="Pigeon Finder",
            font=Styles.FONT_HEADING,
            text_color=Styles.COLOR_PRIMARY
        )
        title_label.pack(pady=(20, 10), padx=20)
        
        # Directory selection
        dir_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        dir_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(dir_frame, text="Scan Directory:").pack(anchor="w")
        
        self.dir_entry = ctk.CTkEntry(dir_frame, placeholder_text="Select directory...")
        self.dir_entry.pack(fill="x", pady=(5, 0))
        
        browse_btn = ctk.CTkButton(
            dir_frame, 
            text="Browse", 
            command=self.browse_directory,
            width=80
        )
        browse_btn.pack(pady=(5, 0))
        
        # Scan options
        self.create_scan_options(sidebar)
        
        # Action buttons
        self.create_action_buttons(sidebar)
        
        # Statistics
        self.create_sidebar_stats(sidebar)
        
    def create_scan_options(self, parent):
        """Create scan options section"""
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(options_frame, text="Scan Options:", font=Styles.FONT_SUBHEADING).pack(anchor="w")
        
        # File size filters
        size_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        size_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(size_frame, text="File Size (MB):").pack(anchor="w")
        
        size_row = ctk.CTkFrame(size_frame, fg_color="transparent")
        size_row.pack(fill="x", pady=(5, 0))
        
        self.min_size = ctk.CTkEntry(size_row, placeholder_text="Min", width=80)
        self.min_size.pack(side="left", padx=(0, 5))
        
        self.max_size = ctk.CTkEntry(size_row, placeholder_text="Max", width=80)
        self.max_size.pack(side="left")
        
        # File extensions
        ext_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        ext_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(ext_frame, text="File Extensions:").pack(anchor="w")
        self.ext_entry = ctk.CTkEntry(ext_frame, placeholder_text=".jpg, .png, .pdf (leave empty for all)")
        self.ext_entry.pack(fill="x", pady=(5, 0))
        
        # Hash algorithm
        algo_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        algo_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(algo_frame, text="Hash Algorithm:").pack(anchor="w")
        self.algo_var = ctk.StringVar(value="md5")
        algo_menu = ctk.CTkOptionMenu(
            algo_frame, 
            values=["md5", "sha1", "sha256", "sha512"],
            variable=self.algo_var
        )
        algo_menu.pack(fill="x", pady=(5, 0))
        
    def create_action_buttons(self, parent):
        """Create action buttons"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        self.scan_btn = ctk.CTkButton(
            btn_frame,
            text="Start Scan",
            command=self.start_scan,
            fg_color=Styles.COLOR_PRIMARY,
            hover_color=Styles.COLOR_PRIMARY_DARK,
            font=Styles.FONT_BUTTON
        )
        self.scan_btn.pack(fill="x", pady=5)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="Stop Scan",
            command=self.stop_scan,
            state="disabled",
            fg_color=Styles.COLOR_SECONDARY,
            hover_color=Styles.COLOR_SECONDARY_DARK
        )
        self.stop_btn.pack(fill="x", pady=5)
        
    def create_sidebar_stats(self, parent):
        """Create statistics display in sidebar"""
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(stats_frame, text="Quick Stats", font=Styles.FONT_SUBHEADING).pack(pady=10)
        
        self.stats_labels = {}
        stats = [
            ("Files Scanned", "0"),
            ("Duplicate Groups", "0"),
            ("Space Wasted", "0 MB"),
            ("Time Saved", "0%")
        ]
        
        for stat_name, default_value in stats:
            stat_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.pack(fill="x", padx=10, pady=2)
            
            ctk.CTkLabel(stat_frame, text=stat_name, font=Styles.FONT_SMALL).pack(side="left")
            label = ctk.CTkLabel(stat_frame, text=default_value, font=Styles.FONT_SMALL_BOLD)
            label.pack(side="right")
            self.stats_labels[stat_name] = label
        
    def create_main_content(self):
        """Create main content area"""
        # Create tab view
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=20, pady=20)
        
        # Results tab
        self.results_tab = self.tab_view.add("Duplicate Results")
        self.results_panel = ResultsPanel(self.results_tab, self.manager)
        self.results_panel.pack(fill="both", expand=True)
        
        # Statistics tab
        self.stats_tab = self.tab_view.add("Detailed Statistics")
        self.stats_panel = StatsPanel(self.stats_tab)
        self.stats_panel.pack(fill="both", expand=True)
        
        # Configure grid weights for main content
        self.results_tab.grid_columnconfigure(0, weight=1)
        self.results_tab.grid_rowconfigure(0, weight=1)
        self.stats_tab.grid_columnconfigure(0, weight=1)
        self.stats_tab.grid_rowconfigure(0, weight=1)
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = ctk.CTkFrame(self, height=30)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        status_frame.grid_propagate(False)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Ready to scan...")
        self.status_label.pack(side="left", padx=10)
        
        # System info
        self.system_info_label = ctk.CTkLabel(status_frame, text="")
        self.system_info_label.pack(side="right", padx=10)
        
    def apply_styles(self):
        """Apply custom styles"""
        # Set theme
        ctk.set_appearance_mode("System")
        
    def browse_directory(self):
        """Browse for directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            self.current_directory = directory
            
    def start_scan(self):
        """Start duplicate file scan"""
        directory = self.dir_entry.get().strip()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory")
            return
        
        # Update engine with selected algorithm
        self.engine = PigeonholeEngine(self.algo_var.get())
        
        # Parse options
        min_size = self.parse_size_input(self.min_size.get())
        max_size = self.parse_size_input(self.max_size.get())
        
        extensions = []
        ext_text = self.ext_entry.get().strip()
        if ext_text:
            extensions = [ext.strip() for ext in ext_text.split(",") if ext.strip()]
        
        # Start scan in separate thread
        self.is_scanning = True
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        thread = threading.Thread(
            target=self._scan_thread,
            args=(directory, extensions, min_size, max_size)
        )
        thread.daemon = True
        thread.start()
        
    def stop_scan(self):
        """Stop current scan"""
        self.is_scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.update_status("Scan stopped by user")
        
    def _scan_thread(self, directory, extensions, min_size, max_size):
        """Scan thread function"""
        try:
            # Step 1: File scanning
            self.update_status("Scanning directory structure...")
            files = self.scanner.scan_directory(directory, extensions, min_size, max_size)
            
            if not self.is_scanning:
                return
                
            # Step 2: Group by size (pigeonhole principle)
            self.update_status("Applying pigeonhole principle optimization...")
            size_groups = self.scanner.get_file_groups_by_size()
            
            if not self.is_scanning:
                return
                
            # Step 3: Find duplicates
            self.update_status("Finding duplicate files...")
            duplicate_groups = self.engine.find_duplicates(
                size_groups,
                progress_callback=self._scan_progress_callback
            )
            
            if not self.is_scanning:
                return
                
            # Step 4: Update UI with results
            self.manager.set_duplicates(duplicate_groups)
            self.after(0, self._scan_complete)
            
        except Exception as e:
            logger.error(f"Scan error: {e}")
            self.after(0, lambda: self._scan_error(str(e)))
    
    def _scan_progress_callback(self, progress, message):
        """Update scan progress"""
        if self.is_scanning:
            self.after(0, lambda: self.update_status(f"{message} - {progress:.1f}%"))
    
    def _scan_complete(self):
        """Handle scan completion"""
        self.is_scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        # Update results panel
        self.results_panel.update_results(self.manager.duplicate_groups)
        
        # Update statistics
        stats = self.manager.get_duplicate_stats()
        efficiency = self.engine.calculate_efficiency_gain(len(self.scanner.scanned_files))
        
        self.stats_labels["Files Scanned"].configure(text=str(len(self.scanner.scanned_files)))
        self.stats_labels["Duplicate Groups"].configure(text=str(stats['total_groups']))
        self.stats_labels["Space Wasted"].configure(text=f"{stats['wasted_space'] / (1024*1024):.1f} MB")
        self.stats_labels["Time Saved"].configure(text=f"{efficiency:.1f}%")
        
        # Update stats panel
        self.stats_panel.update_stats(stats, self.engine.get_optimization_stats())
        
        self.update_status(f"Scan complete! Found {stats['total_duplicates']} duplicate files.")
        
    def _scan_error(self, error_message):
        """Handle scan error"""
        self.is_scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error_message}")
        self.update_status("Scan failed")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=message)
        
        # Update system info
        try:
            sys_stats = self.scanner.get_system_stats()
            sys_text = f"CPU: {sys_stats['cpu_percent']:.1f}% | Memory: {sys_stats['memory_percent']:.1f}%"
            self.system_info_label.configure(text=sys_text)
        except:
            pass
    
    def parse_size_input(self, size_str):
        """Parse size input string to bytes"""
        if not size_str.strip():
            return 0
        
        try:
            size = float(size_str)
            return int(size * 1024 * 1024)  # Convert MB to bytes
        except ValueError:
            return 0