import os
from collections import defaultdict
import logging
from core_hashing import FileHasher

logger = logging.getLogger(__name__)

class PigeonholeEngine:
    def __init__(self, hash_algorithm='md5'):
        self.hasher = FileHasher(hash_algorithm)
        self.stats = {
            'files_processed': 0,
            'hash_computations_saved': 0,
            'comparisons_made': 0,
        }
    
    def find_duplicates(self, file_groups, progress_callback=None):
        duplicate_groups = {}
        total_groups = len(file_groups)
        
        for i, (size, file_list) in enumerate(file_groups.items()):
            if progress_callback:
                progress = (i / total_groups) * 100
                progress_callback(progress, f"Processing {len(file_list)} files of size {size}")
            
            if len(file_list) == 1:
                continue
            
            size_duplicates = self._find_duplicates_in_group(file_list)
            duplicate_groups.update(size_duplicates)
            
            self.stats['files_processed'] += len(file_list)
        
        return duplicate_groups
    
    def _find_duplicates_in_group(self, file_list):
        if len(file_list) < 2:
            return {}
        
        duplicate_groups = {}
        processed_files = set()
        hash_groups = defaultdict(list)
        
        for file_path in file_list:
            if file_path in processed_files:
                continue
            
            try:
                file_hash = self.hasher.calculate_hash(file_path)
                hash_groups[file_hash].append(file_path)
                processed_files.add(file_path)
            except Exception as e:
                continue
        
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                original = min(files, key=lambda x: os.path.getmtime(x))
                duplicates = [f for f in files if f != original]
                duplicate_groups[original] = duplicates
        
        return duplicate_groups
    
    def get_optimization_stats(self):
        return self.stats.copy()
    
    def calculate_efficiency_gain(self, total_files):
        if total_files == 0:
            return 0.0
        naive_comparisons = total_files * (total_files - 1) // 2
        actual_comparisons = self.stats['comparisons_made']
        if naive_comparisons == 0:
            return 0.0
        return ((naive_comparisons - actual_comparisons) / naive_comparisons) * 100