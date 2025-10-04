import os
import time
from pathlib import Path
import psutil
import logging

logger = logging.getLogger(__name__)

class FileScanner:
    def __init__(self):
        self.scanned_files = {}
        
    def scan_directory(self, directory, extensions=None, min_size=0, max_size=0):
        directory = os.path.normpath(directory)
        if not os.path.exists(directory):
            raise ValueError(f"Directory does not exist: {directory}")
            
        self.scanned_files.clear()
        scanned_count = 0
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                try:
                    file_path = os.path.join(root, file)
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
                    
                    self.scanned_files[file_path] = {
                        'size': file_size,
                        'modified': stat.st_mtime,
                        'path': file_path,
                        'name': file
                    }
                    scanned_count += 1
                    
                except (OSError, PermissionError) as e:
                    continue
        
        logger.info(f"Scanned {scanned_count} files from {directory}")
        return self.scanned_files.copy()
    
    def get_file_groups_by_size(self):
        size_groups = {}
        for file_path, info in self.scanned_files.items():
            size = info['size']
            if size == 0:
                continue
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(file_path)
        
        return {size: files for size, files in size_groups.items() if len(files) > 1}
    
    def get_system_stats(self):
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }