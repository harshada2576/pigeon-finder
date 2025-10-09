import sys
import os
import time
import hashlib
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
# Import shared backend logic
from file_io import scan_files, process_action, select_original_file
from core import PigeonholeEngine

# Import all necessary PyQt5 modules
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QComboBox, QSpinBox, QProgressBar, QStackedWidget, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog, QGroupBox, QHeaderView
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QMutex, QObject, QUrl
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

# --- 1. CORE LOGIC & CONFIGURATION (Member 1 & 2 Integration) ---
HASH_CHUNK_SIZE = 65536
PARTIAL_HASH_SIZE = 4096
ZERO_BYTE_SIZE = 0
mutex = QMutex()

# Helper Functions (M1 Logic - Hashing)
def _hash_file_chunked(filepath, size_limit=None, hash_algorithm=hashlib.sha256):
    """Calculates hash of a file up to a size limit, reading in chunks."""
    hasher = hash_algorithm()
    bytes_read = 0
    
    try:
        with open(filepath, 'rb') as f:
            while True:
                remaining = size_limit - bytes_read if size_limit is not None else HASH_CHUNK_SIZE
                chunk_size = min(HASH_CHUNK_SIZE, remaining) if size_limit is not None else HASH_CHUNK_SIZE
                
                if chunk_size <= 0: break

                chunk = f.read(chunk_size)
                if not chunk: break
                
                hasher.update(chunk)
                bytes_read += len(chunk)

                if size_limit is not None and bytes_read >= size_limit: break
                    
        return hasher.hexdigest()
    except Exception:
        return None

def get_partial_hash(filepath):
    return _hash_file_chunked(filepath, size_limit=PARTIAL_HASH_SIZE)

def get_full_hash(filepath):
    return _hash_file_chunked(filepath)

# I/O Action Logic (M2 Logic - Keep Original)
def get_file_metadata(path):
    """Returns file size and modification time."""
    try:
        return os.path.getsize(path), os.path.getmtime(path)
    except:
        return 0, 0

def select_original_file(duplicate_set, keep_mode):
    """Selects the 'original' file based on keep_mode."""
    
    if keep_mode == 'newest':
        return max(duplicate_set, key=lambda p: get_file_metadata(p)[1])
    elif keep_mode == 'oldest':
        return min(duplicate_set, key=lambda p: get_file_metadata(p)[1])
    elif keep_mode == 'path_length':
        return min(duplicate_set, key=len)
    return max(duplicate_set, key=lambda p: get_file_metadata(p)[1])


# --- 2. THE SCAN WORKER THREAD (M1 & M2 Execution) ---

class ScanWorker(QObject):
    """
    Worker class to run the I/O and Hashing logic in a separate thread.
    This prevents the UI from freezing during scanning.
    """
    # Signals for communication with the main thread
    progress_update = pyqtSignal(int, int) # Current, Total
    scan_complete = pyqtSignal(list, float) # Duplicates list, runtime
    error_occurred = pyqtSignal(str)

    def __init__(self, root_path, allowed_extensions, min_size, include_zero_byte):
        super().__init__()
        self.root_path = root_path
        self.allowed_extensions = allowed_extensions
        self.min_size = min_size
        self.include_zero_byte = include_zero_byte
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run_scan(self):
        start_time = time.time()
        files_by_size = scan_files(self.root_path, self.allowed_extensions, self.min_size, self.include_zero_byte)
        if not files_by_size:
            self.scan_complete.emit([], time.time() - start_time)
            return
        engine = PigeonholeEngine()
        duplicate_dict = engine.find_duplicates(files_by_size)
        duplicates = [[original] + dups for original, dups in duplicate_dict.items()]
        runtime = time.time() - start_time
        self.scan_complete.emit(duplicates, runtime)


        
        # Minimal Light Theme (Off-white base, teal accent)
        self.light_stylesheet = """
            QMainWindow, QWidget { background-color: #f5f7fa; color: #2c3e50; }
            QPushButton { 
                background-color: #1abc9c; color: white; border: 1px solid #16a085; 
                padding: 8px; border-radius: 5px; min-width: 80px; 
            }
            QPushButton:hover { background-color: #16a085; }
            QLineEdit, QSpinBox, QComboBox { 
                background-color: white; color: #2c3e50; border: 1px solid #bdc3c7; 
                padding: 5px; border-radius: 3px; 
            }
            QGroupBox { 
                border: 2px solid #bdc3c7; margin-top: 10px; padding: 10px;
                border-radius: 5px; 
            }
            QTableWidget {
                background-color: white; color: #2c3e50; border: 1px solid #bdc3c7;
                selection-background-color: #3498db;
                gridline-color: #d1d5da;
            }
            QHeaderView::section { 
                background-color: #ecf0f1; padding: 4px; border: 1px solid #bdc3c7;
                color: #2c3e50;
            }
            QProgressBar::chunk { background-color: #3498db; }
        """

    def apply_theme(self):
        """Applies the current theme stylesheet."""
        if self.current_theme == 'dark':
            self.setStyleSheet(self.dark_stylesheet)
            self.theme_button.setText("🌞 Light Mode")
        else:
            self.setStyleSheet(self.light_stylesheet)
            self.theme_button.setText("🌙 Dark Mode")

    def toggle_theme(self):
        """Switches between dark and light modes."""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()


    def _setup_ui(self):
        """Builds the main layout and initializes widgets."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Top Bar (Logo and Theme Toggle) ---
        top_bar = QHBoxLayout()
        logo_label = QLabel("🐦 PigeonFinder")
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        top_bar.addWidget(logo_label)
        top_bar.addStretch(1)

        self.theme_button = QPushButton()
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setToolTip("Toggle between Light and Dark themes")
        top_bar.addWidget(self.theme_button)
        
        # --- LEFT PANEL: Settings and Controls ---
        self.settings_panel = QWidget()
        self.settings_panel.setFixedWidth(350)
        self.settings_layout = QVBoxLayout(self.settings_panel)
        self.settings_layout.addLayout(top_bar)
        
        # 1. Target Directory Group
        path_group = QGroupBox("Target Directory")
        path_layout = QHBoxLayout(path_group)
        self.path_input = QLineEdit(os.path.expanduser('~'))
        self.path_input.setToolTip("Enter the path to scan or drag a folder here.")
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self._select_directory)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        self.settings_layout.addWidget(path_group)

        # 2. Filtering Group
        filter_group = QGroupBox("Scan Filtering")
        filter_layout = QGridLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Extensions (e.g., jpg,mp4):"), 0, 0)
        self.ext_input = QLineEdit("jpg,png,pdf")
        filter_layout.addWidget(self.ext_input, 0, 1)

        filter_layout.addWidget(QLabel("Min Size (Bytes):"), 1, 0)
        self.min_size_input = QSpinBox()
        self.min_size_input.setRange(0, 1000000000)
        self.min_size_input.setSuffix(" bytes")
        filter_layout.addWidget(self.min_size_input, 1, 1)

        self.zero_byte_check = QCheckBox("Include Zero-Byte Files")
        self.zero_byte_check.setChecked(False)
        filter_layout.addWidget(self.zero_byte_check, 2, 0, 1, 2)
        self.settings_layout.addWidget(filter_group)
        
        # 3. Action Group
        action_group = QGroupBox("Duplicate Management")
        action_layout = QVBoxLayout(action_group)

        action_layout.addWidget(QLabel("Action:"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Do Nothing (Report Only)", "Delete Duplicates", "Move Duplicates"])
        self.action_combo.currentTextChanged.connect(self._toggle_move_path)
        action_layout.addWidget(self.action_combo)

        action_layout.addWidget(QLabel("Keep Mode (Original):"))
        self.keep_mode_combo = QComboBox()
        self.keep_mode_combo.addItems(["Newest File", "Oldest File", "Shortest Path"])
        action_layout.addWidget(self.keep_mode_combo)
        
        # Move Path (Initially hidden)
        self.move_path_widget = QWidget()
        self.move_path_layout = QHBoxLayout(self.move_path_widget)
        self.move_path_layout.setContentsMargins(0,0,0,0)
        self.move_path_input = QLineEdit(os.path.join(os.path.expanduser('~'), 'PigeonFinder_Moved'))
        self.move_path_browse = QPushButton("...")
        self.move_path_browse.clicked.connect(self._select_move_directory)
        self.move_path_layout.addWidget(self.move_path_input)
        self.move_path_layout.addWidget(self.move_path_browse)
        
        self.settings_layout.addWidget(action_group)
        self.settings_layout.addWidget(self.move_path_widget)
        self.move_path_widget.hide() # Hide by default

        # 4. Scan Button
        self.scan_button = QPushButton("🚀 Start Scan")
        self.scan_button.setStyleSheet("font-size: 16px; padding: 10px; font-weight: bold;")
        self.scan_button.clicked.connect(self._start_scan_thread)
        self.settings_layout.addWidget(self.scan_button)
        
        self.settings_layout.addStretch(1) # Push everything up


        # --- CENTER PANEL: Stacked View (Status/Results) ---
        self.center_stack = QStackedWidget()
        
        # Page 0: Status/Pre-Scan View
        self.status_page = QWidget()
        self.status_layout = QVBoxLayout(self.status_page)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(30)
        self.status_layout.addWidget(self.progress_bar, 1)

        self.status_message = QLabel("Ready to scan. Select a folder and filters.")
        self.status_message.setAlignment(Qt.AlignCenter)
        self.status_message.setStyleSheet("font-size: 14px; padding: 20px;")
        self.status_layout.addWidget(self.status_message, 1)
        self.status_layout.addStretch(10)
        self.center_stack.addWidget(self.status_page)
        
        # Page 1: Results View
        self.results_page = QWidget()
        self.results_layout = QVBoxLayout(self.results_page)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Action", "File Name", "Size", "Path", "Date Modified"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # Stretch Path column
        self.results_table.cellChanged.connect(self._handle_manual_selection)
        self.results_layout.addWidget(self.results_table)

        # Result Action Bar
        result_action_bar = QHBoxLayout()
        self.summary_label = QLabel("Summary: 0 Sets, 0 Duplicates.")
        result_action_bar.addWidget(self.summary_label)
        result_action_bar.addStretch(1)
        
        self.export_button = QPushButton("Export Report")
        self.export_button.clicked.connect(self._export_report)
        result_action_bar.addWidget(self.export_button)
        
        self.execute_button = QPushButton("Execute Actions (0 files)")
        self.execute_button.setStyleSheet("background-color: #e74c3c; font-weight: bold;")
        self.execute_button.clicked.connect(self._confirm_execute_actions)
        result_action_bar.addWidget(self.execute_button)
        
        self.results_layout.addLayout(result_action_bar)
        self.center_stack.addWidget(self.results_page)
        
        # Add panels to main layout
        main_layout.addWidget(self.settings_panel)
        main_layout.addWidget(self.center_stack)


    # --- UI Slot Methods ---

    def _select_directory(self):
        """Opens a file dialog to select the target directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Target Directory", self.path_input.text())
        if directory:
            self.path_input.setText(directory)

    def _select_move_directory(self):
        """Opens a file dialog to select the move destination directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Move Destination", self.move_path_input.text())
        if directory:
            self.move_path_input.setText(directory)
    
    def _toggle_move_path(self, text):
        """Shows/hides the move path input based on action selection."""
        self.move_path_widget.setVisible(text == "Move Duplicates")

    def _update_execute_button(self):
        """Updates the count on the Execute button based on table content."""
        count = 0
        for i in range(self.results_table.rowCount()):
            # Check the status of the 'Action' column (which is a QComboBox/QLineEdit in this design, we simplify to string)
            # In a full impl, this would read the QComboBox state. Here, we just count non-original rows.
            item_text = self.results_table.item(i, 0).text()
            if item_text in ["Delete", "Move"]:
                 count += 1
        
        self.execute_button.setText(f"Execute Actions ({count} files)")
        self.execute_count = count


    # --- Scan Execution and Threading ---

    def _start_scan_thread(self):
        """Initializes and starts the scan in a separate thread."""
        root_path = self.path_input.text()
        if not os.path.isdir(root_path):
            QMessageBox.critical(self, "Invalid Path", "Please select a valid directory to scan.")
            return

        # Disable UI elements during scan
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning... (Do not close)")
        self.center_stack.setCurrentIndex(0)
        self.progress_bar.setValue(0)
        self.status_message.setText("Starting scan and hashing...")

        # Parse filtering arguments
        ext_list = {f".{e.strip().lower()}" for e in self.ext_input.text().split(',')} if self.ext_input.text() else set()
        min_size = self.min_size_input.value()
        include_zero_byte = self.zero_byte_check.isChecked()

        # Initialize thread and worker
        self.thread = QThread()
        self.worker = ScanWorker(root_path, ext_list, min_size, include_zero_byte)
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run_scan)
        self.worker.progress_update.connect(self._update_progress)
        self.worker.scan_complete.connect(self._scan_finished)
        self.worker.error_occurred.connect(self._handle_scan_error)
        
        self.thread.start()

    def _update_progress(self, current, total):
        """Updates the progress bar and status message."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.status_message.setText(f"Processing: {current}/{total} files. Hashing is in progress...")

    def _scan_finished(self, duplicate_sets, runtime):
        """Handles scan completion, updates UI, and displays results."""
        self.thread.quit()
        self.thread.wait()
        
        self.scan_button.setEnabled(True)
        self.scan_button.setText("🚀 Start Scan")
        self.status_message.setText(f"Scan complete in {runtime:.2f} seconds.")
        
        self.duplicate_sets = duplicate_sets
        self._display_results(duplicate_sets, runtime)

    def _handle_scan_error(self, message):
        """Displays a critical error message."""
        self.thread.quit()
        self.thread.wait()
        self.scan_button.setEnabled(True)
        self.scan_button.setText("🚀 Start Scan")
        QMessageBox.critical(self, "Scan Error", message)
        self.status_message.setText("Scan terminated due to an error.")


    # --- Results Display and Management (M5 Integration) ---
    
    def _display_results(self, duplicate_sets, runtime):
        """Populates the results table with confirmed duplicates."""
        self.center_stack.setCurrentIndex(1)
        
        total_duplicates = sum(len(s) - 1 for s in duplicate_sets)
        total_files = sum(len(s) for s in duplicate_sets)
        self.summary_label.setText(f"Summary: {len(duplicate_sets)} Sets found, {total_duplicates} Duplicates (of {total_files} total files).")

        self.results_table.setRowCount(0) # Clear previous results
        
        keep_mode = self.keep_mode_combo.currentText().split()[0].lower() # e.g., 'newest'
        
        row_count = 0
        for i, duplicate_set in enumerate(duplicate_sets):
            original_path = select_original_file(duplicate_set, keep_mode)
            
            for path in duplicate_set:
                self.results_table.insertRow(row_count)
                
                # Determine action and styling
                is_original = (path == original_path)
                action_text = "KEEP (Original)" if is_original else "Delete" if self.action_combo.currentText() == "Delete Duplicates" else "Move" if self.action_combo.currentText() == "Move Duplicates" else "KEEP (Duplicate)"
                
                # --- ACTION COLUMN (Column 0) ---
                action_item = QTableWidgetItem(action_text)
                if is_original:
                    action_item.setBackground(self.palette().color(self.palette().Highlight)) # Use highlight color for KEPT file
                action_item.setFlags(Qt.ItemIsEnabled) # Cannot change the action for the original
                self.results_table.setItem(row_count, 0, action_item)

                # --- METADATA COLUMNS ---
                size, mtime = get_file_metadata(path)
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

                self.results_table.setItem(row_count, 1, QTableWidgetItem(os.path.basename(path)))
                self.results_table.setItem(row_count, 2, QTableWidgetItem(f"{size / 1024:.2f} KB"))
                self.results_table.setItem(row_count, 3, QTableWidgetItem(path))
                self.results_table.setItem(row_count, 4, QTableWidgetItem(mtime_str))

                # Style the rows to show grouping (simple alternating row style)
                bg_color = '#3b556b' if i % 2 == 0 and self.current_theme == 'dark' else '#ebeef2' if i % 2 == 0 else 'transparent'
                for col in range(5):
                    self.results_table.item(row_count, col).setBackground(self.palette().color(self.palette().Base).lighter(105) if self.current_theme == 'light' else self.palette().color(self.palette().Midlight))
                    if is_original:
                         self.results_table.item(row_count, col).setBackground(self.palette().color(self.palette().Highlight))
                    
                row_count += 1

        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._update_execute_button()

    def _handle_manual_selection(self):
        """Placeholder for future manual selection logic."""
        # This slot would handle changing the action column manually.
        self._update_execute_button()
        
    def _confirm_execute_actions(self):
        """Shows a confirmation box before execution."""
        if self.execute_count == 0:
            QMessageBox.information(self, "No Actions", "No files are currently marked for deletion or moving.")
            return

        action_type = self.action_combo.currentText().split()[0].upper()
        move_path = self.move_path_input.text() if action_type == 'MOVE' else ''
        
        confirmation = QMessageBox.question(
            self, f"Confirm {action_type} Action",
            f"WARNING: You are about to {action_type} {self.execute_count} files.\n"
            f"This action is permanent and cannot be undone.\n\n"
            f"Proceed with {action_type}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmation == QMessageBox.Yes:
            self._execute_actions(action_type.lower(), move_path)
    
    def _execute_actions(self, action, move_path=""):
        """M2 Logic: Iterates through the table and executes actions."""
        
        QMessageBox.information(self, "Action Started", f"Starting {action} process. UI may momentarily freeze...")
        
        processed_count = 0
        
        # Iterate through the confirmed duplicate sets (the original data structure)
        for duplicate_set in self.duplicate_sets:
            keep_mode = self.keep_mode_combo.currentText().split()[0].lower()
            original_path = select_original_file(duplicate_set, keep_mode)

            # Use the M2 logic to process the action
            processed_count += self._process_io_action(duplicate_set, original_path, action, move_path)

        QMessageBox.information(self, "Action Complete", f"Successfully completed {action} for {processed_count} files!")
        # Rerun scan or refresh results here if needed
        self.duplicate_sets = []
        self._display_results([], 0)


    def _process_io_action(self, duplicate_set, original_path, action, move_path=None):
        # Use shared process_action from file_io.py
        return process_action(duplicate_set, original_path, action, move_path)
        
    def _export_report(self):
        """Saves the scan results and summary to a file."""
        if not self.duplicate_sets:
            QMessageBox.warning(self, "Export Failed", "No scan results available to export.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Save Report", "PigeonFinder_Report.txt", "Text Files (*.txt);;CSV Files (*.csv)")
        
        if filename:
            try:
                content = self._generate_report_content()
                with open(filename, 'w') as f:
                    f.write(content)
                QMessageBox.information(self, "Export Success", f"Report saved successfully to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save file: {e}")

    def _generate_report_content(self):
        """Generates text report content from current results."""
        report = [
            "=====================================================================",
            "             PIGEONFINDER DUPLICATE FILE REPORT                      ",
            "=====================================================================",
            f"Time Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Target Path: {self.path_input.text()}",
            f"Keep Mode: {self.keep_mode_combo.currentText()}",
            f"Total Sets Found: {len(self.duplicate_sets)}",
            "---------------------------------------------------------------------"
        ]
        
        keep_mode = self.keep_mode_combo.currentText().split()[0].lower()
        
        for i, duplicate_set in enumerate(self.duplicate_sets, 1):
            original_path = select_original_file(duplicate_set, keep_mode)
            
            report.append(f"\n[SET {i}] - {len(duplicate_set)} Files")
            report.append(f"  ORIGINAL ({keep_mode.upper()}): {original_path}")
            
            for path in duplicate_set:
                action = " (KEPT)" if path == original_path else " (DUPLICATE)"
                report.append(f"    - {path}{action}")
                
        return "\n".join(report)


if __name__ == '__main__':
    # Set high DPI awareness for modern cross-platform displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    window = PigeonFinderApp()
    window.show()
    sys.exit(app.exec_())

