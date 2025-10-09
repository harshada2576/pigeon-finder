import sys
import os
import sys
import os
import time
import hashlib
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QComboBox, QSpinBox, QProgressBar, QStackedWidget, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog, QGroupBox, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QObject

# Import shared backend logic
from file_io import scan_files, process_action, select_original_file
from core import PigeonholeEngine

# --- 1. CORE LOGIC & CONFIGURATION ---
HASH_CHUNK_SIZE = 65536
PARTIAL_HASH_SIZE = 4096
mutex = QMutex()


def _hash_file_chunked(filepath, size_limit=None, hash_algorithm=hashlib.sha256):
    hasher = hash_algorithm()
    bytes_read = 0
    try:
        with open(filepath, 'rb') as f:
            while True:
                remaining = size_limit - bytes_read if size_limit is not None else None
                if size_limit is not None:
                    # explicit min(HASH_CHUNK_SIZE, remaining) without using min()
                    if remaining <= 0:
                        chunk_size = 0
                    elif remaining < HASH_CHUNK_SIZE:
                        chunk_size = remaining
                    else:
                        chunk_size = HASH_CHUNK_SIZE
                else:
                    chunk_size = HASH_CHUNK_SIZE
                if chunk_size <= 0:
                    break
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
                bytes_read += len(chunk)
                if size_limit is not None and bytes_read >= size_limit:
                    break
        return hasher.hexdigest()
    except Exception:
        return None


def get_partial_hash(filepath):
    return _hash_file_chunked(filepath, size_limit=PARTIAL_HASH_SIZE)


def get_full_hash(filepath):
    return _hash_file_chunked(filepath)


def get_file_metadata(path):
    try:
        return os.path.getsize(path), os.path.getmtime(path)
    except Exception:
        return 0, 0


def select_original_file(duplicate_set, keep_mode):
    # Explicit selection without built-in min/max
    if not duplicate_set:
        return None

    def _mtime(p):
        try:
            return get_file_metadata(p)[1]
        except Exception:
            return 0

    if keep_mode == 'newest':
        best = None
        best_mtime = -1
        for p in duplicate_set:
            m = _mtime(p)
            if m > best_mtime:
                best_mtime = m
                best = p
        return best

    if keep_mode == 'oldest':
        best = None
        best_mtime = None
        for p in duplicate_set:
            m = _mtime(p)
            if best is None or m < best_mtime:
                best_mtime = m
                best = p
        return best

    if keep_mode == 'path_length':
        best = None
        best_len = None
        for p in duplicate_set:
            l = len(p)
            if best is None or l < best_len:
                best_len = l
                best = p
        return best

    # Default to newest
    best = None
    best_mtime = -1
    for p in duplicate_set:
        m = _mtime(p)
        if m > best_mtime:
            best_mtime = m
            best = p
    return best


class ScanWorker(QObject):
    """Background worker that performs scanning/hashing and emits signals."""
    progress_update = pyqtSignal(int, int)  # current, total
    scan_complete = pyqtSignal(list, float)  # duplicates, runtime
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
        try:
            # Provide a progress callback to the scanning function
            def progress_cb(current, total):
                # If stop requested, raise to interrupt
                if not self._is_running:
                    raise Exception('Scan cancelled')
                self.progress_update.emit(current, total)

            files_by_size = scan_files(self.root_path, self.allowed_extensions, self.min_size, self.include_zero_byte, progress_callback=progress_cb)
            if not files_by_size:
                self.scan_complete.emit([], time.time() - start_time)
                return
            engine = PigeonholeEngine()
            duplicate_dict = engine.find_duplicates(files_by_size)
            duplicates = [[original] + dups for original, dups in duplicate_dict.items()]
            runtime = time.time() - start_time
            self.scan_complete.emit(duplicates, runtime)
        except Exception as e:
            self.error_occurred.emit(str(e))


class PigeonFinderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PigeonFinder")
        self.resize(1100, 700)

        self.current_theme = 'light'
        self.light_stylesheet = """
            QMainWindow, QWidget { background-color: #f5f7fa; color: #2c3e50; }
            QPushButton { background-color: #1abc9c; color: white; border: 1px solid #16a085; padding: 8px; border-radius: 5px; min-width: 80px; }
            QPushButton:hover { background-color: #16a085; }
            QLineEdit, QSpinBox, QComboBox { background-color: white; color: #2c3e50; border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; }
            QGroupBox { border: 2px solid #bdc3c7; margin-top: 10px; padding: 10px; border-radius: 5px; }
            QTableWidget { background-color: white; color: #2c3e50; border: 1px solid #bdc3c7; selection-background-color: #3498db; gridline-color: #d1d5da; }
            QHeaderView::section { background-color: #ecf0f1; padding: 4px; border: 1px solid #bdc3c7; color: #2c3e50; }
            QProgressBar::chunk { background-color: #3498db; }
        """
        self.dark_stylesheet = """
            QMainWindow, QWidget { background-color: #1e1e2f; color: #dfe6ee; }
        """

        self._setup_ui()

    def apply_theme(self):
        if self.current_theme == 'dark':
            self.setStyleSheet(self.dark_stylesheet)
            self.theme_button.setText("🌞 Light Mode")
        else:
            self.setStyleSheet(self.light_stylesheet)
            self.theme_button.setText("🌙 Dark Mode")

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Top bar
        top_bar = QHBoxLayout()
        logo_label = QLabel("🐦 PigeonFinder")
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        top_bar.addWidget(logo_label)
        top_bar.addStretch(1)
        self.theme_button = QPushButton()
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setToolTip("Toggle between Light and Dark themes")
        top_bar.addWidget(self.theme_button)

        # Left settings panel
        self.settings_panel = QWidget()
        self.settings_panel.setFixedWidth(350)
        self.settings_layout = QVBoxLayout(self.settings_panel)
        self.settings_layout.addLayout(top_bar)

        path_group = QGroupBox("Target Directory")
        path_layout = QHBoxLayout(path_group)
        self.path_input = QLineEdit(os.path.expanduser('~'))
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self._select_directory)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        self.settings_layout.addWidget(path_group)

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
        self.move_path_widget.hide()

        # Scan controls
        scan_controls = QHBoxLayout()
        self.scan_button = QPushButton("🚀 Start Scan")
        self.scan_button.setStyleSheet("font-size: 16px; padding: 10px; font-weight: bold;")
        self.scan_button.clicked.connect(self._start_scan_thread)
        scan_controls.addWidget(self.scan_button)

        self.cancel_button = QPushButton("✖ Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_scan)
        scan_controls.addWidget(self.cancel_button)

        self.test_scan_button = QPushButton("🔎 Test Scan (test_dir)")
        self.test_scan_button.clicked.connect(self._start_test_scan)
        scan_controls.addWidget(self.test_scan_button)

        self.settings_layout.addLayout(scan_controls)
        self.settings_layout.addStretch(1)

        # Center stack
        self.center_stack = QStackedWidget()
        self.status_page = QWidget()
        self.status_layout = QVBoxLayout(self.status_page)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(30)
        self.status_layout.addWidget(self.progress_bar, 1)
        self.status_message = QLabel("Ready to scan. Select a folder and filters.")
        self.status_message.setAlignment(Qt.AlignCenter)
        self.status_layout.addWidget(self.status_message, 1)
        self.status_layout.addStretch(10)
        self.center_stack.addWidget(self.status_page)

        self.results_page = QWidget()
        self.results_layout = QVBoxLayout(self.results_page)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Action", "File Name", "Size", "Path", "Date Modified"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.results_table.cellChanged.connect(self._handle_manual_selection)
        self.results_layout.addWidget(self.results_table)

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

        main_layout.addWidget(self.settings_panel)
        main_layout.addWidget(self.center_stack)

        # Menu and status bar
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        file_menu.addAction("Export Report", self._export_report)
        file_menu.addAction("Exit", lambda: self.close())
        view_menu = menu.addMenu("View")
        view_menu.addAction("Toggle Theme", self.toggle_theme)

        self.statusBar().showMessage("Ready")

    # UI slots and helpers
    def _select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Target Directory", self.path_input.text())
        if directory:
            self.path_input.setText(directory)

    def _select_move_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Move Destination", self.move_path_input.text())
        if directory:
            self.move_path_input.setText(directory)

    def _toggle_move_path(self, text):
        self.move_path_widget.setVisible(text == "Move Duplicates")

    def _update_execute_button(self):
        count = 0
        for i in range(self.results_table.rowCount()):
            item = self.results_table.item(i, 0)
            if item and item.text() in ["Delete", "Move"]:
                count += 1
        self.execute_button.setText(f"Execute Actions ({count} files)")
        self.execute_count = count

    # Scanning/threading
    def _start_scan_thread(self):
        root_path = self.path_input.text()
        if not os.path.isdir(root_path):
            QMessageBox.critical(self, "Invalid Path", "Please select a valid directory to scan.")
            return

        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning... (Do not close)")
        self.center_stack.setCurrentIndex(0)
        self.progress_bar.setValue(0)
        self.status_message.setText("Starting scan and hashing...")

        ext_list = {f".{e.strip().lower()}" for e in self.ext_input.text().split(',')} if self.ext_input.text() else set()
        min_size = self.min_size_input.value()
        include_zero_byte = self.zero_byte_check.isChecked()
        # Enable cancel and show status
        self.cancel_button.setEnabled(True)
        self.statusBar().showMessage(f"Scanning {root_path}...")

        self.thread = QThread()
        # Pass a progress callback into scan_files via the worker
        self.worker = ScanWorker(root_path, ext_list, min_size, include_zero_byte)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run_scan)
        self.worker.progress_update.connect(self._update_progress)
        self.worker.scan_complete.connect(self._scan_finished)
        self.worker.error_occurred.connect(self._handle_scan_error)
        self.thread.start()

    def _update_progress(self, current, total):
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.status_message.setText(f"Processing: {current}/{total} files. Hashing is in progress...")
            self.statusBar().showMessage(f"Scanning: {current}/{total}")

    def _scan_finished(self, duplicate_sets, runtime):
        try:
            self.thread.quit()
            self.thread.wait()
        except Exception:
            pass
        self.scan_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.scan_button.setText("🚀 Start Scan")
        self.status_message.setText(f"Scan complete in {runtime:.2f} seconds.")
        self.statusBar().showMessage(f"Scan complete in {runtime:.2f}s")
        self.duplicate_sets = duplicate_sets
        self._display_results(duplicate_sets, runtime)

    def _handle_scan_error(self, message):
        try:
            self.thread.quit()
            self.thread.wait()
        except Exception:
            pass
        self.scan_button.setEnabled(True)
        self.scan_button.setText("🚀 Start Scan")
        QMessageBox.critical(self, "Scan Error", message)
        self.status_message.setText("Scan terminated due to an error.")
        self.statusBar().showMessage("Scan error")

    def _cancel_scan(self):
        # Attempt to stop worker and thread
        try:
            if hasattr(self, 'worker') and hasattr(self.worker, 'stop'):
                self.worker.stop()
            if hasattr(self, 'thread'):
                self.thread.quit()
                self.thread.wait(1000)
        except Exception:
            pass
        self.cancel_button.setEnabled(False)
        self.scan_button.setEnabled(True)
        self.scan_button.setText("🚀 Start Scan")
        self.statusBar().showMessage("Scan cancelled")

    def _start_test_scan(self):
        test_path = os.path.join(os.path.dirname(__file__), 'test_dir')
        if not os.path.isdir(test_path):
            QMessageBox.warning(self, "No test_dir", f"test_dir not found at {test_path}")
            return
        self.path_input.setText(test_path)
        self._start_scan_thread()

    # Results display
    def _display_results(self, duplicate_sets, runtime):
        self.center_stack.setCurrentIndex(1)
        total_duplicates = 0
        total_files = 0
        for s in duplicate_sets:
            total_files += len(s)
            # explicit max(0, len(s) - 1) replacement
            dups = len(s) - 1
            if dups < 0:
                dups = 0
            total_duplicates += dups
        self.summary_label.setText(f"Summary: {len(duplicate_sets)} Sets found, {total_duplicates} Duplicates (of {total_files} total files).")
        self.results_table.setRowCount(0)
        keep_mode = self.keep_mode_combo.currentText().split()[0].lower()
        row_count = 0
        for i, duplicate_set in enumerate(duplicate_sets):
            original_path = select_original_file(duplicate_set, keep_mode)
            for path in duplicate_set:
                self.results_table.insertRow(row_count)
                is_original = (path == original_path)
                action_text = "KEEP (Original)" if is_original else "Delete" if self.action_combo.currentText() == "Delete Duplicates" else "Move" if self.action_combo.currentText() == "Move Duplicates" else "KEEP (Duplicate)"
                action_item = QTableWidgetItem(action_text)
                if is_original:
                    action_item.setBackground(self.palette().color(self.palette().Highlight))
                action_item.setFlags(Qt.ItemIsEnabled)
                self.results_table.setItem(row_count, 0, action_item)
                size, mtime = get_file_metadata(path)
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                self.results_table.setItem(row_count, 1, QTableWidgetItem(os.path.basename(path)))
                self.results_table.setItem(row_count, 2, QTableWidgetItem(f"{size / 1024:.2f} KB"))
                self.results_table.setItem(row_count, 3, QTableWidgetItem(path))
                self.results_table.setItem(row_count, 4, QTableWidgetItem(mtime_str))
                for col in range(5):
                    item = self.results_table.item(row_count, col)
                    if item:
                        item.setBackground(self.palette().color(self.palette().Base).lighter(105) if self.current_theme == 'light' else self.palette().color(self.palette().Midlight))
                        if is_original:
                            item.setBackground(self.palette().color(self.palette().Highlight))
                row_count += 1
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._update_execute_button()

    def _handle_manual_selection(self):
        self._update_execute_button()

    def _confirm_execute_actions(self):
        if getattr(self, 'execute_count', 0) == 0:
            QMessageBox.information(self, "No Actions", "No files are currently marked for deletion or moving.")
            return
        action_type = self.action_combo.currentText().split()[0].upper()
        move_path = self.move_path_input.text() if action_type == 'MOVE' else ''
        confirmation = QMessageBox.question(self, f"Confirm {action_type} Action", f"WARNING: You are about to {action_type} {self.execute_count} files.\nThis action is permanent and cannot be undone.\n\nProceed with {action_type}?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self._execute_actions(action_type.lower(), move_path)

    def _execute_actions(self, action, move_path=""):
        QMessageBox.information(self, "Action Started", f"Starting {action} process. UI may momentarily freeze...")
        processed_count = 0
        for duplicate_set in getattr(self, 'duplicate_sets', []):
            keep_mode = self.keep_mode_combo.currentText().split()[0].lower()
            original_path = select_original_file(duplicate_set, keep_mode)
            processed_count += self._process_io_action(duplicate_set, original_path, action, move_path)
        QMessageBox.information(self, "Action Complete", f"Successfully completed {action} for {processed_count} files!")
        self.duplicate_sets = []
        self._display_results([], 0)

    def _process_io_action(self, duplicate_set, original_path, action, move_path=None):
        return process_action(duplicate_set, original_path, action, move_path)

    def _export_report(self):
        if not getattr(self, 'duplicate_sets', None):
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
        report = [
            "=====================================================================",
            "             PIGEONFINDER DUPLICATE FILE REPORT                      ",
            "=====================================================================",
            f"Time Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Target Path: {self.path_input.text()}",
            f"Keep Mode: {self.keep_mode_combo.currentText()}",
            f"Total Sets Found: {len(getattr(self, 'duplicate_sets', []))}",
            "---------------------------------------------------------------------"
        ]
        keep_mode = self.keep_mode_combo.currentText().split()[0].lower()
        for i, duplicate_set in enumerate(getattr(self, 'duplicate_sets', []), 1):
            original_path = select_original_file(duplicate_set, keep_mode)
            report.append(f"\n[SET {i}] - {len(duplicate_set)} Files")
            report.append(f"  ORIGINAL ({keep_mode.upper()}): {original_path}")
            for path in duplicate_set:
                action = " (KEPT)" if path == original_path else " (DUPLICATE)"
                report.append(f"    - {path}{action}")
        return "\n".join(report)


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    window = PigeonFinderApp()
    window.show()
    sys.exit(app.exec_())
