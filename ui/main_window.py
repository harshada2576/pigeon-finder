"""
Main Application Window - Complete Enhanced Version
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import logging
from pathlib import Path
from ..core.file_scanner import FileScanner
from ..core.pigeonhole_engine import PigeonholeEngine
from ..core.duplicate_manager import DuplicateManager
from core.file_scanner import FileScanner
from core.pigeonhole_engine import PigeonholeEngine
from core.duplicate_manager import DuplicateManager
from ..core.batch_processor import SmartBatchManager
from ..core.file_preview import PreviewDialog
from .results_panel import ResultsPanel
from .stats_panel import StatsPanel
from .progress_dialog import ProgressDialog
from .advanced_tools import AdvancedToolsPanel
from .styles import Styles
from ..utils.config import Config

logger = logging.getLogger(__name__)

class MainWindow(ctk.CTk):
    """Main application window with all advanced features"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config = Config()
        self.scanner = FileScanner()
        self.engine = PigeonholeEngine()
        self.manager = DuplicateManager()
        self.scanner = FileScanner()
        self.engine = PigeonholeEngine()
        self.manager = DuplicateManager()
        self.batch_manager = SmartBatchManager()
        
        # UI state
        self.is_scanning = False
        self.is_monitoring = False
        self.current_directory = ""
        self.duplicate_groups = {}
        
        self.setup_window()
        self.create_widgets()
        self.apply_styles()
        self.load_config()
        
    def setup_window(self):
        """Configure main window"""
        self.title("Pigeon Finder - Advanced Duplicate File Detective")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
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
        
        # Create menu bar
        self.create_menu_bar()
        
    def create_menu_bar(self):
        """Create application menu bar"""
        # Note: CustomTkinter doesn't have a native menu bar, so we'll create a toolbar-style menu
        menu_frame = ctk.CTkFrame(self, height=40)
        menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        menu_frame.grid_propagate(False)
        
        # File menu
        file_btn = ctk.CTkButton(
            menu_frame,
            text="File",
            width=60,
            command=self.show_file_menu
        )
        file_btn.pack(side="left", padx=5)
        
        # Tools menu
        tools_btn = ctk.CTkButton(
            menu_frame,
            text="Tools", 
            width=60,
            command=self.show_tools_menu
        )
        tools_btn.pack(side="left", padx=5)
        
        # View menu
        view_btn = ctk.CTkButton(
            menu_frame,
            text="View",
            width=60,
            command=self.show_view_menu
        )
        view_btn.pack(side="left", padx=5)
        
        # Help menu
        help_btn = ctk.CTkButton(
            menu_frame,
            text="Help",
            width=60,
            command=self.show_help_menu
        )
        help_btn.pack(side="left", padx=5)
        
        # Spacer
        ctk.CTkLabel(menu_frame, text="").pack(side="left", expand=True)
        
        # Theme switcher
        self.theme_var = ctk.StringVar(value="System")
        theme_menu = ctk.CTkOptionMenu(
            menu_frame,
            values=["System", "Light", "Dark"],
            variable=self.theme_var,
            command=self.change_theme,
            width=100
        )
        theme_menu.pack(side="right", padx=5)
        
    def create_sidebar(self):
        """Create sidebar with controls"""
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        sidebar.grid(row=1, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Title and logo area
        self.create_sidebar_header(sidebar)
        
        # Directory selection
        self.create_directory_section(sidebar)
        
        # Scan options
        self.create_scan_options(sidebar)
        
        # Action buttons
        self.create_action_buttons(sidebar)
        
        # Quick actions
        self.create_quick_actions(sidebar)
        
        # Statistics
        self.create_sidebar_stats(sidebar)
        
    def create_sidebar_header(self, parent):
        """Create sidebar header with title and logo"""
        header_frame = ctk.CTkFrame(parent, fg_color=Styles.COLOR_PRIMARY)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🕊️ Pigeon Finder",
            font=("Arial", 20, "bold"),
            text_color="white"
        )
        title_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Duplicate File Detective",
            font=Styles.FONT_SMALL,
            text_color="white"
        )
        subtitle_label.pack(pady=(0, 10))
        
    def create_directory_section(self, parent):
        """Create directory selection section"""
        dir_frame = ctk.CTkFrame(parent)
        dir_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(dir_frame, text="Scan Directory", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        # Recent directories dropdown
        recent_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        recent_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(recent_frame, text="Recent:", font=Styles.FONT_SMALL).pack(side="left")
        
        self.recent_dirs_var = ctk.StringVar(value="Select directory...")
        recent_menu = ctk.CTkOptionMenu(
            recent_frame,
            variable=self.recent_dirs_var,
            command=self.select_recent_directory,
            values=self.config.get('recent_directories', []) or ["No recent directories"]
        )
        recent_menu.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Directory entry
        self.dir_entry = ctk.CTkEntry(dir_frame, placeholder_text="Select directory or choose from recent...")
        self.dir_entry.pack(fill="x", pady=5)
        
        # Browse button
        browse_btn = ctk.CTkButton(
            dir_frame, 
            text="Browse Directory", 
            command=self.browse_directory,
            fg_color=Styles.COLOR_SECONDARY,
            hover_color=Styles.COLOR_SECONDARY_DARK
        )
        browse_btn.pack(fill="x", pady=5)
        
    def create_scan_options(self, parent):
        """Create scan options section"""
        options_frame = ctk.CTkFrame(parent)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(options_frame, text="Scan Options", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        # File size filters
        size_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        size_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(size_frame, text="File Size Filter (MB):").pack(anchor="w")
        
        size_input_frame = ctk.CTkFrame(size_frame, fg_color="transparent")
        size_input_frame.pack(fill="x", pady=2)
        
        self.min_size = ctk.CTkEntry(size_input_frame, placeholder_text="Min", width=70)
        self.min_size.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(size_input_frame, text="to").pack(side="left", padx=5)
        
        self.max_size = ctk.CTkEntry(size_input_frame, placeholder_text="Max", width=70)
        self.max_size.pack(side="left", padx=(5, 0))
        
        # File extensions
        ext_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        ext_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(ext_frame, text="File Extensions:").pack(anchor="w")
        self.ext_entry = ctk.CTkEntry(ext_frame, placeholder_text=".jpg, .png, .pdf (empty for all)")
        self.ext_entry.pack(fill="x", pady=2)
        
        # Hash algorithm
        algo_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        algo_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(algo_frame, text="Hash Algorithm:").pack(anchor="w")
        self.algo_var = ctk.StringVar(value=self.config.get('scanning.default_algorithm', 'md5'))
        algo_menu = ctk.CTkOptionMenu(
            algo_frame, 
            values=["md5", "sha1", "sha256", "sha512", "blake2b"],
            variable=self.algo_var
        )
        algo_menu.pack(fill="x", pady=2)
        
        # Advanced options
        self.advanced_options_frame = ctk.CTkFrame(options_frame)
        self.advanced_options_frame.pack(fill="x", pady=5)
        
        self.quick_scan_var = ctk.BooleanVar(value=self.config.get('scanning.use_quick_scan', True))
        quick_scan_cb = ctk.CTkCheckBox(
            self.advanced_options_frame,
            text="Use Quick Scan (Pigeonhole Principle)",
            variable=self.quick_scan_var
        )
        quick_scan_cb.pack(anchor="w", pady=2)
        
        self.include_hidden_var = ctk.BooleanVar(value=False)
        hidden_cb = ctk.CTkCheckBox(
            self.advanced_options_frame,
            text="Include Hidden Files",
            variable=self.include_hidden_var
        )
        hidden_cb.pack(anchor="w", pady=2)
        
    def create_action_buttons(self, parent):
        """Create action buttons"""
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.scan_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 Start Scan",
            command=self.start_scan,
            fg_color=Styles.COLOR_PRIMARY,
            hover_color=Styles.COLOR_PRIMARY_DARK,
            font=Styles.FONT_BUTTON,
            height=40
        )
        self.scan_btn.pack(fill="x", pady=5)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹️ Stop Scan",
            command=self.stop_scan,
            state="disabled",
            fg_color=Styles.COLOR_SECONDARY,
            hover_color=Styles.COLOR_SECONDARY_DARK,
            height=35
        )
        self.stop_btn.pack(fill="x", pady=5)
        
        # Monitor toggle
        self.monitor_btn = ctk.CTkButton(
            btn_frame,
            text="👁️ Start Monitoring",
            command=self.toggle_monitoring,
            height=35
        )
        self.monitor_btn.pack(fill="x", pady=5)
        
    def create_quick_actions(self, parent):
        """Create quick actions section"""
        actions_frame = ctk.CTkFrame(parent)
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(actions_frame, text="Quick Actions", font=Styles.FONT_SUBHEADING).pack(anchor="w", pady=5)
        
        # Action buttons grid
        actions_grid = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_grid.pack(fill="x", pady=5)
        
        # Row 1
        row1 = ctk.CTkFrame(actions_grid, fg_color="transparent")
        row1.pack(fill="x", pady=2)
        
        ctk.CTkButton(
            row1,
            text="Preview Files",
            command=self.preview_selected_files,
            width=120
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            row1,
            text="Export Results",
            command=self.export_results,
            width=120
        ).pack(side="right", padx=2)
        
        # Row 2
        row2 = ctk.CTkFrame(actions_grid, fg_color="transparent")
        row2.pack(fill="x", pady=2)
        
        ctk.CTkButton(
            row2,
            text="Clean Empty Dirs",
            command=self.clean_empty_directories,
            width=120
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            row2,
            text="System Info",
            command=self.show_system_info,
            width=120
        ).pack(side="right", padx=2)
        
    def create_sidebar_stats(self, parent):
        """Create statistics display in sidebar"""
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(stats_frame, text="Scan Statistics", font=Styles.FONT_SUBHEADING).pack(pady=10)
        
        self.stats_labels = {}
        stats = [
            ("Files Scanned", "0"),
            ("Duplicate Groups", "0"),
            ("Space Wasted", "0 MB"),
            ("Efficiency Gain", "0%"),
            ("Scan Time", "0s")
        ]
        
        for stat_name, default_value in stats:
            stat_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.pack(fill="x", padx=10, pady=3)
            
            ctk.CTkLabel(stat_frame, text=stat_name, font=Styles.FONT_SMALL).pack(side="left")
            label = ctk.CTkLabel(stat_frame, text=default_value, font=Styles.FONT_SMALL_BOLD)
            label.pack(side="right")
            self.stats_labels[stat_name] = label
            
        # Efficiency bar
        efficiency_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        efficiency_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(efficiency_frame, text="Pigeonhole Efficiency", font=Styles.FONT_SMALL).pack(anchor="w")
        self.efficiency_bar = ctk.CTkProgressBar(efficiency_frame)
        self.efficiency_bar.pack(fill="x", pady=2)
        self.efficiency_bar.set(0)
        
    def create_main_content(self):
        """Create main content area"""
        # Create tab view
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=20, pady=20)
        
        # Results tab
        self.results_tab = self.tab_view.add("📊 Duplicate Results")
        self.results_panel = ResultsPanel(self.results_tab, self.manager)
        self.results_panel.pack(fill="both", expand=True)
        
        # Statistics tab
        self.stats_tab = self.tab_view.add("📈 Detailed Statistics")
        self.stats_panel = StatsPanel(self.stats_tab)
        self.stats_panel.pack(fill="both", expand=True)
        
        # Advanced Tools tab
        self.tools_tab = self.tab_view.add("🛠️ Advanced Tools")
        self.advanced_tools = AdvancedToolsPanel(self.tools_tab)
        self.advanced_tools.pack(fill="both", expand=True)
        
        # Preview tab (initially empty)
        self.preview_tab = self.tab_view.add("👁️ File Preview")
        self.setup_preview_tab()
        
        # Configure grid weights for main content
        for tab in [self.results_tab, self.stats_tab, self.tools_tab, self.preview_tab]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            
    def setup_preview_tab(self):
        """Setup the preview tab"""
        preview_frame = ctk.CTkFrame(self.preview_tab)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial message
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="Select files from the Results tab to preview them here.\n\n"
                 "Supported formats: Images (JPG, PNG, GIF, etc.) and Text files.",
            font=Styles.FONT_NORMAL,
            text_color=Styles.COLOR_TEXT_SECONDARY
        )
        self.preview_label.pack(expand=True)
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = ctk.CTkFrame(self, height=30)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        status_frame.grid_propagate(False)
        
        # Status message
        self.status_label = ctk.CTkLabel(status_frame, text="Ready to scan...")
        self.status_label.pack(side="left", padx=10)
        
        # Progress bar for operations
        self.status_progress = ctk.CTkProgressBar(status_frame, width=200, height=15)
        self.status_progress.pack(side="left", padx=10)
        self.status_progress.set(0)
        
        # System info
        self.system_info_label = ctk.CTkLabel(status_frame, text="")
        self.system_info_label.pack(side="right", padx=10)
        
    def apply_styles(self):
        """Apply custom styles"""
        # Set theme from config
        theme = self.config.get('ui.theme', 'System')
        ctk.set_appearance_mode(theme)
        self.theme_var.set(theme)
        
    def load_config(self):
        """Load configuration settings"""
        # Update recent directories dropdown
        recent_dirs = self.config.get('recent_directories', [])
        if recent_dirs:
            recent_menu = self.recent_dirs_var._textvariable
            # Note: This would need to be implemented based on how CTkOptionMenu works
            
    def browse_directory(self):
        """Browse for directory"""
        directory = filedialog.askdirectory(title="Select directory to scan for duplicates")
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            self.current_directory = directory
            self.config.add_recent_directory(directory)
            self.update_status(f"Selected directory: {directory}")
            
    def select_recent_directory(self, choice):
        """Select directory from recent list"""
        if choice and choice != "No recent directories":
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, choice)
            self.current_directory = choice
            
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
        self.status_progress.set(0)
        
        # Save scan preferences
        self.config.set('scanning.default_algorithm', self.algo_var.get())
        self.config.set('scanning.use_quick_scan', self.quick_scan_var.get())
        
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
        
    def toggle_monitoring(self):
        """Toggle directory monitoring"""
        directory = self.dir_entry.get().strip()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory first")
            return
            
        if not self.is_monitoring:
            # Start monitoring
            try:
                self.scanner.start_monitoring(directory, self._monitoring_callback)
                self.is_monitoring = True
                self.monitor_btn.configure(text="👁️ Stop Monitoring", fg_color=Styles.COLOR_DANGER)
                self.update_status(f"Started monitoring: {directory}")
            except Exception as e:
                messagebox.showerror("Monitoring Error", f"Could not start monitoring: {e}")
        else:
            # Stop monitoring
            self.scanner.stop_monitoring()
            self.is_monitoring = False
            self.monitor_btn.configure(text="👁️ Start Monitoring", fg_color=Styles.COLOR_SECONDARY)
            self.update_status("Stopped directory monitoring")
            
    def _monitoring_callback(self, event_type, file_path):
        """Handle file system monitoring events"""
        message = f"File {event_type}: {os.path.basename(file_path)}"
        self.after(0, lambda: self.update_status(message))
        
    def _scan_thread(self, directory, extensions, min_size, max_size):
        """Scan thread function"""
        import time
        start_time = time.time()
        
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
            self.duplicate_groups = duplicate_groups
            scan_time = time.time() - start_time
            
            self.after(0, lambda: self._scan_complete(scan_time))
            
        except Exception as e:
            logger.error(f"Scan error: {e}")
            self.after(0, lambda: self._scan_error(str(e)))
    
    def _scan_progress_callback(self, progress, message):
        """Update scan progress"""
        if self.is_scanning:
            self.after(0, lambda: self.update_status(f"{message} - {progress:.1f}%"))
            self.after(0, lambda: self.status_progress.set(progress / 100))
    
    def _scan_complete(self, scan_time):
        """Handle scan completion"""
        self.is_scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_progress.set(0)
        
        # Update results panel
        self.manager.set_duplicates(self.duplicate_groups)
        self.results_panel.update_results(self.manager.duplicate_groups)
        
        # Update statistics
        stats = self.manager.get_duplicate_stats()
        efficiency = self.engine.calculate_efficiency_gain(len(self.scanner.scanned_files))
        
        self.stats_labels["Files Scanned"].configure(text=str(len(self.scanner.scanned_files)))
        self.stats_labels["Duplicate Groups"].configure(text=str(stats['total_groups']))
        self.stats_labels["Space Wasted"].configure(text=f"{stats['wasted_space'] / (1024*1024):.1f} MB")
        self.stats_labels["Efficiency Gain"].configure(text=f"{efficiency:.1f}%")
        self.stats_labels["Scan Time"].configure(text=f"{scan_time:.1f}s")
        
        # Update efficiency bar
        self.efficiency_bar.set(efficiency / 100)
        
        # Update stats panel
        self.stats_panel.update_stats(stats, self.engine.get_optimization_stats())
        
        self.update_status(f"Scan complete! Found {stats['total_duplicates']} duplicate files in {scan_time:.1f}s.")
        
        # Show notification
        if stats['total_duplicates'] > 0:
            messagebox.showinfo(
                "Scan Complete", 
                f"Found {stats['total_groups']} duplicate groups with {stats['total_duplicates']} files.\n"
                f"Wasted space: {stats['wasted_space'] / (1024*1024):.1f} MB\n"
                f"Pigeonhole efficiency: {efficiency:.1f}%"
            )
    
    def _scan_error(self, error_message):
        """Handle scan error"""
        self.is_scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_progress.set(0)
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error_message}")
        self.update_status("Scan failed")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=message)
        
        # Update system info
        try:
            sys_stats = self.scanner.get_system_stats()
            sys_text = f"CPU: {sys_stats['cpu_percent']:.1f}% | Memory: {sys_stats['memory_percent']:.1f}% | Disk: {sys_stats['disk_usage']:.1f}%"
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
    
    def show_file_menu(self):
        """Show file menu options"""
        menu = ctk.CTkToplevel(self)
        menu.title("File Menu")
        menu.geometry("200x150")
        menu.transient(self)
        menu.grab_set()
        
        # Center on parent
        self.center_window(menu)
        
        ctk.CTkButton(menu, text="New Scan", command=lambda: self.menu_action("new_scan")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="Open Results", command=lambda: self.menu_action("open_results")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="Export Results", command=lambda: self.menu_action("export")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="Settings", command=lambda: self.menu_action("settings")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="Exit", command=self.quit).pack(fill="x", pady=2)
        
    def show_tools_menu(self):
        """Show tools menu options"""
        menu = ctk.CTkToplevel(self)
        menu.title("Tools Menu")
        menu.geometry("220x180")
        menu.transient(self)
        menu.grab_set()
        
        self.center_window(menu)
        
        ctk.CTkButton(menu, text="Batch Operations", command=lambda: self.menu_action("batch_ops")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="File Preview", command=lambda: self.menu_action("preview")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="Clean Empty Folders", command=lambda: self.menu_action("clean_folders")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="Disk Space Analyzer", command=lambda: self.menu_action("disk_analyzer")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="System Information", command=lambda: self.menu_action("system_info")).pack(fill="x", pady=2)
        
    def show_view_menu(self):
        """Show view menu options"""
        menu = ctk.CTkToplevel(self)
        menu.title("View Menu")
        menu.geometry("180x120")
        menu.transient(self)
        menu.grab_set()
        
        self.center_window(menu)
        
        ctk.CTkButton(menu, text="Refresh", command=lambda: self.menu_action("refresh")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="Reset Layout", command=lambda: self.menu_action("reset_layout")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="Show Log", command=lambda: self.menu_action("show_log")).pack(fill="x", pady=2)
        
    def show_help_menu(self):
        """Show help menu options"""
        menu = ctk.CTkToplevel(self)
        menu.title("Help Menu")
        menu.geometry("200x120")
        menu.transient(self)
        menu.grab_set()
        
        self.center_window(menu)
        
        ctk.CTkButton(menu, text="User Guide", command=lambda: self.menu_action("user_guide")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="About Pigeon Finder", command=lambda: self.menu_action("about")).pack(fill="x", pady=2)
        ctk.CTkButton(menu, text="Check for Updates", command=lambda: self.menu_action("updates")).pack(fill="x", pady=2)
        
    def menu_action(self, action):
        """Handle menu actions"""
        if action == "new_scan":
            self.dir_entry.delete(0, "end")
            self.update_status("Ready for new scan")
        elif action == "export":
            self.export_results()
        elif action == "batch_ops":
            self.tab_view.set("🛠️ Advanced Tools")
        elif action == "preview":
            self.preview_selected_files()
        elif action == "clean_folders":
            self.clean_empty_directories()
        elif action == "system_info":
            self.show_system_info()
        elif action == "about":
            self.show_about()
        # Close any open menu windows
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkToplevel) and child.title() and "Menu" in child.title():
                child.destroy()
    
    def center_window(self, window):
        """Center a window on the main window"""
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - window.winfo_height()) // 2
        window.geometry(f"+{x}+{y}")
    
    def change_theme(self, choice):
        """Change application theme"""
        ctk.set_appearance_mode(choice)
        self.config.set('ui.theme', choice)
    
    def preview_selected_files(self):
        """Preview selected files"""
        selected_files = list(self.results_panel.selected_files) if hasattr(self.results_panel, 'selected_files') else []
        
        if not selected_files:
            # Try to get files from current duplicate groups
            all_duplicates = []
            for original, duplicates in self.duplicate_groups.items():
                all_duplicates.extend([original] + duplicates)
            
            if all_duplicates:
                selected_files = all_duplicates[:10]  # Preview first 10 files
        
        if not selected_files:
            messagebox.showinfo("Preview", "No files selected for preview. Select files in the Results tab first.")
            return
        
        # Open preview dialog
        preview_dialog = PreviewDialog(self, selected_files)
        
    def export_results(self):
        """Export scan results to file"""
        if not self.duplicate_groups:
            messagebox.showwarning("Export", "No scan results to export. Please run a scan first.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("Pigeon Finder - Duplicate File Report\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Scan Directory: {self.current_directory}\n")
                    f.write(f"Scan Date: {self.get_current_timestamp()}\n\n")
                    
                    total_duplicates = 0
                    total_space = 0
                    
                    for i, (original, duplicates) in enumerate(self.duplicate_groups.items(), 1):
                        f.write(f"Duplicate Group {i}:\n")
                        f.write(f"  Original: {original}\n")
                        f.write(f"  Size: {os.path.getsize(original) / (1024*1024):.2f} MB\n")
                        f.write("  Duplicates:\n")
                        
                        for duplicate in duplicates:
                            f.write(f"    - {duplicate}\n")
                            total_space += os.path.getsize(duplicate)
                        
                        total_duplicates += len(duplicates)
                        f.write("\n")
                    
                    f.write(f"Summary:\n")
                    f.write(f"  Total Groups: {len(self.duplicate_groups)}\n")
                    f.write(f"  Total Duplicates: {total_duplicates}\n")
                    f.write(f"  Wasted Space: {total_space / (1024*1024):.2f} MB\n")
                
                messagebox.showinfo("Export Successful", f"Results exported to:\n{filename}")
                self.update_status(f"Results exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
    
    def clean_empty_directories(self):
        """Find and clean empty directories"""
        directory = self.dir_entry.get().strip()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory first")
            return
        
        try:
            empty_dirs = self.find_empty_directories(directory)
            
            if not empty_dirs:
                messagebox.showinfo("Cleanup", "No empty directories found.")
                return
            
            result = messagebox.askyesno(
                "Clean Empty Directories",
                f"Found {len(empty_dirs)} empty directories.\n\nDelete them?",
                icon="warning"
            )
            
            if result:
                deleted_count = 0
                for dir_path in empty_dirs:
                    try:
                        os.rmdir(dir_path)
                        deleted_count += 1
                    except OSError:
                        pass  # Directory might not be empty anymore
                
                messagebox.showinfo("Cleanup Complete", f"Deleted {deleted_count} empty directories.")
                self.update_status(f"Cleaned {deleted_count} empty directories")
                
        except Exception as e:
            messagebox.showerror("Cleanup Error", f"Error during cleanup:\n{str(e)}")
    
    def find_empty_directories(self, directory):
        """Recursively find empty directories"""
        empty_dirs = []
        
        for root, dirs, files in os.walk(directory, topdown=False):
            # Check if directory is empty
            if not dirs and not files:
                empty_dirs.append(root)
        
        return empty_dirs
    
    def show_system_info(self):
        """Show system information"""
        try:
            import psutil
            import platform
            
            system_info = (
                f"System Information:\n"
                f"OS: {platform.system()} {platform.release()}\n"
                f"Processor: {platform.processor()}\n"
                f"CPU Cores: {psutil.cpu_count()}\n"
                f"Total RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB\n"
                f"Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB\n"
                f"Disk Usage: {psutil.disk_usage('/').percent:.1f}%"
            )
            
            messagebox.showinfo("System Information", system_info)
            
        except Exception as e:
            messagebox.showerror("System Info", f"Could not retrieve system information:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = (
            "Pigeon Finder - Advanced Duplicate File Detective\n\n"
            "Version 1.0.0\n\n"
            "A sophisticated duplicate file detection tool that uses the "
            "Pigeonhole Principle for optimal performance.\n\n"
            "Features:\n"
            "• Mathematical optimization using Pigeonhole Principle\n"
            "• Multiple hash algorithms (MD5, SHA1, SHA256, SHA512, BLAKE2b)\n"
            "• Real-time directory monitoring\n"
            "• Batch file operations\n"
            "• Advanced file preview\n"
            "• Professional UI with dark/light themes\n\n"
            "Built with Python and CustomTkinter"
        )
        
        messagebox.showinfo("About Pigeon Finder", about_text)
    
    def get_current_timestamp(self):
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __del__(self):
        """Cleanup on exit"""
        if hasattr(self, 'scanner'):
            self.scanner.stop_monitoring()
        
        # Save configuration
        if hasattr(self, 'config'):
            self.config.save()

# Run the application
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()