"""
Advanced File Scanner with Pigeonhole Principle optimization
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

logger = logging.getLogger(__name__)

class FileScanner:
    """Advanced file scanner with real-time monitoring"""
    
    def __init__(self):
        self.scanned_files: Dict[str, Dict] = {}
        self.observer = None
        self.is_monitoring = False
        
    def scan_directory(self, directory: str, 
                      extensions: Optional[List[str]] = None,
                      min_size: int = 0,
                      max_size: int = 0) -> Dict[str, Dict]:
        """
        Scan directory for files with optional filters
        
        Args:
            directory: Path to scan
            extensions: List of file extensions to include
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes
            
        Returns:
            Dictionary of file information
        """
        directory = os.path.normpath(directory)
        if not os.path.exists(directory):
            raise ValueError(f"Directory does not exist: {directory}")
            
        self.scanned_files.clear()
        scanned_count = 0
        
        for root, dirs, files in os.walk(directory):
            # Skip system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['System Volume Information']]
            
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    
                    # Get file stats
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    
                    # Apply filters
                    if min_size > 0 and file_size < min_size:
                        continue
                    if max_size > 0 and file_size > max_size:
                        continue
                    if extensions:
                        file_ext = Path(file).suffix.lower()
                        if file_ext not in [ext.lower() for ext in extensions]:
                            continue
                    
                    # Store file info
                    self.scanned_files[file_path] = {
                        'size': file_size,
                        'modified': stat.st_mtime,
                        'created': stat.st_ctime,
                        'path': file_path,
                        'name': file
                    }
                    
                    scanned_count += 1
                    
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not access file {file}: {e}")
                    continue
        
        logger.info(f"Scanned {scanned_count} files from {directory}")
        return self.scanned_files.copy()
    
    def get_file_groups_by_size(self) -> Dict[int, List[str]]:
        """Group files by size for pigeonhole principle optimization"""
        size_groups = {}
        for file_path, info in self.scanned_files.items():
            size = info['size']
            if size == 0:  # Skip empty files
                continue
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(file_path)
        
        # Only return groups with more than one file (potential duplicates)
        return {size: files for size, files in size_groups.items() if len(files) > 1}
    
    def start_monitoring(self, directory: str, callback):
        """Start real-time directory monitoring"""
        class ChangeHandler(FileSystemEventHandler):
            def on_created(self, event):
                if not event.is_directory:
                    callback('created', event.src_path)
            
            def on_deleted(self, event):
                if not event.is_directory:
                    callback('deleted', event.src_path)
            
            def on_modified(self, event):
                if not event.is_directory:
                    callback('modified', event.src_path)
        
        self.observer = Observer()
        handler = ChangeHandler()
        self.observer.schedule(handler, directory, recursive=True)
        self.observer.start()
        self.is_monitoring = True
        logger.info(f"Started monitoring directory: {directory}")
    
    def stop_monitoring(self):
        """Stop directory monitoring"""
        if self.observer and self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            logger.info("Stopped directory monitoring")
    
    def get_system_stats(self) -> Dict:
        """Get system resource statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }