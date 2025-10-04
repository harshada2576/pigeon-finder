"""
Duplicate File Management
"""

import os
import shutil
from typing import Dict, List, Set, Tuple
from send2trash import send2trash
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DuplicateManager:
    """Manage duplicate files with various operations"""
    
    def __init__(self):
        self.duplicate_groups: Dict[str, List[str]] = {}
        self.selected_files: Set[str] = set()
    
    def set_duplicates(self, duplicate_groups: Dict[str, List[str]]):
        """Set the duplicate groups to manage"""
        self.duplicate_groups = duplicate_groups
        self.selected_files.clear()
    
    def get_all_duplicates(self) -> List[str]:
        """Get all duplicate file paths (excluding originals)"""
        all_duplicates = []
        for original, duplicates in self.duplicate_groups.items():
            all_duplicates.extend(duplicates)
        return all_duplicates
    
    def get_duplicate_stats(self) -> Dict:
        """Get statistics about duplicates"""
        total_duplicates = 0
        total_size = 0
        file_types = {}
        
        for original, duplicates in self.duplicate_groups.items():
            total_duplicates += len(duplicates)
            try:
                original_size = os.path.getsize(original)
                total_size += original_size * len(duplicates)
                
                # Count file types
                ext = Path(original).suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + len(duplicates) + 1
            except OSError:
                continue
        
        return {
            'total_groups': len(self.duplicate_groups),
            'total_duplicates': total_duplicates,
            'wasted_space': total_size,
            'file_types': file_types
        }
    
    def select_files(self, file_paths: List[str]):
        """Select files for batch operations"""
        self.selected_files.update(file_paths)
    
    def deselect_files(self, file_paths: List[str]):
        """Deselect files"""
        self.selected_files.difference_update(file_paths)
    
    def delete_files(self, file_paths: List[str], use_trash: bool = True) -> Tuple[int, List[str]]:
        """
        Delete duplicate files
        
        Args:
            file_paths: List of files to delete
            use_trash: Send to recycle bin instead of permanent delete
            
        Returns:
            Tuple of (success_count, failed_files)
        """
        success_count = 0
        failed_files = []
        
        for file_path in file_paths:
            try:
                if use_trash:
                    send2trash(file_path)
                else:
                    os.remove(file_path)
                success_count += 1
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                failed_files.append(file_path)
                logger.error(f"Failed to delete {file_path}: {e}")
        
        # Update duplicate groups
        self._update_groups_after_deletion(file_paths)
        
        return success_count, failed_files
    
    def move_files(self, file_paths: List[str], destination: str) -> Tuple[int, List[str]]:
        """
        Move files to destination directory
        
        Args:
            file_paths: List of files to move
            destination: Destination directory
            
        Returns:
            Tuple of (success_count, failed_files)
        """
        os.makedirs(destination, exist_ok=True)
        success_count = 0
        failed_files = []
        
        for file_path in file_paths:
            try:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(destination, filename)
                
                # Handle filename conflicts
                counter = 1
                base_name = Path(filename).stem
                extension = Path(filename).suffix
                
                while os.path.exists(dest_path):
                    new_filename = f"{base_name}_{counter}{extension}"
                    dest_path = os.path.join(destination, new_filename)
                    counter += 1
                
                shutil.move(file_path, dest_path)
                success_count += 1
                logger.info(f"Moved {file_path} to {dest_path}")
                
            except Exception as e:
                failed_files.append(file_path)
                logger.error(f"Failed to move {file_path}: {e}")
        
        # Update duplicate groups
        self._update_groups_after_deletion(file_paths)
        
        return success_count, failed_files
    
    def _update_groups_after_deletion(self, deleted_files: List[str]):
        """Update duplicate groups after file deletion"""
        new_groups = {}
        
        for original, duplicates in self.duplicate_groups.items():
            # Remove deleted files from duplicates list
            remaining_duplicates = [dup for dup in duplicates if dup not in deleted_files]
            
            # Only keep groups that still have duplicates
            if remaining_duplicates:
                new_groups[original] = remaining_duplicates
        
        self.duplicate_groups = new_groups
        # Remove deleted files from selection
        self.selected_files.difference_update(deleted_files)