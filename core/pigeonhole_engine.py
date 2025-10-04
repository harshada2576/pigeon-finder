"""
Pigeonhole Principle Engine for Efficient Duplicate Detection
"""

import os
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import logging
from .hashing import FileHasher

logger = logging.getLogger(__name__)

class PigeonholeEngine:
    """
    Advanced duplicate detection using Pigeonhole Principle
    Optimizes by grouping files before hashing
    """
    
    def __init__(self, hash_algorithm: str = 'md5'):
        self.hasher = FileHasher(hash_algorithm)
        self.stats = {
            'files_processed': 0,
            'hash_computations_saved': 0,
            'comparisons_made': 0,
            'time_saved': 0.0
        }
    
    def find_duplicates(self, file_groups: Dict[int, List[str]], 
                       progress_callback=None) -> Dict[str, List[str]]:
        """
        Find duplicates using pigeonhole principle optimization
        
        Args:
            file_groups: Files grouped by size (from pigeonhole principle)
            progress_callback: Callback for progress updates
            
        Returns:
            Dictionary of original -> duplicates
        """
        duplicate_groups = {}
        total_groups = len(file_groups)
        
        for i, (size, file_list) in enumerate(file_groups.items()):
            if progress_callback:
                progress = (i / total_groups) * 100
                progress_callback(progress, f"Processing {len(file_list)} files of size {size}")
            
            if len(file_list) == 1:
                continue
            
            # Find duplicates within this size group
            size_duplicates = self._find_duplicates_in_group(file_list)
            duplicate_groups.update(size_duplicates)
            
            # Update statistics
            self.stats['files_processed'] += len(file_list)
            potential_comparisons = len(file_list) * (len(file_list) - 1) // 2
            self.stats['comparisons_made'] += len(size_duplicates)
            self.stats['hash_computations_saved'] += potential_comparisons - len(size_duplicates)
        
        logger.info(f"Pigeonhole optimization saved {self.stats['hash_computations_saved']} computations")
        return duplicate_groups
    
    def _find_duplicates_in_group(self, file_list: List[str]) -> Dict[str, List[str]]:
        """Find duplicates within a group of same-sized files"""
        if len(file_list) < 2:
            return {}
        
        # Quick screening using partial comparison
        candidate_groups = self._quick_screen_duplicates(file_list)
        
        # Detailed hash comparison for candidate groups
        duplicate_groups = {}
        processed_files = set()
        
        for group in candidate_groups:
            if len(group) < 2:
                continue
            
            # Compute full hashes and group duplicates
            hash_groups = defaultdict(list)
            for file_path in group:
                if file_path in processed_files:
                    continue
                
                try:
                    file_hash = self.hasher.calculate_hash(file_path)
                    hash_groups[file_hash].append(file_path)
                    processed_files.add(file_path)
                except Exception as e:
                    logger.warning(f"Could not hash {file_path}: {e}")
                    continue
            
            # Create duplicate groups (keep one original per hash group)
            for file_hash, files in hash_groups.items():
                if len(files) > 1:
                    original = self._select_original_file(files)
                    duplicates = [f for f in files if f != original]
                    duplicate_groups[original] = duplicates
        
        return duplicate_groups
    
    def _quick_screen_duplicates(self, file_list: List[str]) -> List[List[str]]:
        """
        Quick screening using pigeonhole principle:
        - Compare first few bytes first
        - Group files that match in initial screening
        """
        candidate_groups = []
        processed = set()
        
        for i, file1 in enumerate(file_list):
            if file1 in processed:
                continue
            
            current_group = [file1]
            processed.add(file1)
            
            for j, file2 in enumerate(file_list[i+1:], i+1):
                if file2 in processed:
                    continue
                
                if self.hasher.quick_hash_comparison(file1, file2):
                    current_group.append(file2)
                    processed.add(file2)
            
            candidate_groups.append(current_group)
        
        return candidate_groups
    
    def _select_original_file(self, files: List[str]) -> str:
        """Select the best candidate as original file"""
        # Prefer files that are not in system directories
        non_system_files = [f for f in files if not self._is_system_directory(f)]
        if non_system_files:
            files = non_system_files
        
        # Prefer files with earlier modification time (older files)
        return min(files, key=lambda x: os.path.getmtime(x))
    
    def _is_system_directory(self, file_path: str) -> bool:
        """Check if file is in a system directory"""
        system_dirs = {'system', 'windows', 'program files', 'programdata', 'recovery'}
        path_parts = file_path.lower().split(os.sep)
        return any(sys_dir in path_parts for sys_dir in system_dirs)
    
    def get_optimization_stats(self) -> Dict:
        """Get statistics about optimization efficiency"""
        return self.stats.copy()
    
    def calculate_efficiency_gain(self, total_files: int) -> float:
        """Calculate efficiency gain from pigeonhole principle"""
        if total_files == 0:
            return 0.0
        
        naive_comparisons = total_files * (total_files - 1) // 2
        actual_comparisons = self.stats['comparisons_made']
        
        if naive_comparisons == 0:
            return 0.0
        
        return ((naive_comparisons - actual_comparisons) / naive_comparisons) * 100