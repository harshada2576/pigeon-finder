"""
Advanced File Hashing with Multiple Algorithms and Optimization
"""

import hashlib
import os
from typing import Dict, List, Optional, Callable
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FileHasher:
    """Advanced file hashing with progress tracking and multiple algorithms"""
    
    # Supported hash algorithms
    HASH_ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512,
        'blake2b': hashlib.blake2b
    }
    
    def __init__(self, algorithm: str = 'md5', chunk_size: int = 8192):
        self.algorithm = algorithm.lower()
        self.chunk_size = chunk_size
        
        if self.algorithm not in self.HASH_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def calculate_hash(self, file_path: str, 
                      progress_callback: Optional[Callable] = None) -> str:
        """
        Calculate file hash with progress tracking
        
        Args:
            file_path: Path to file
            progress_callback: Callback for progress updates
            
        Returns:
            Hexadecimal hash string
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        hash_func = self.HASH_ALGORITHMS[self.algorithm]()
        bytes_read = 0
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(self.chunk_size):
                    hash_func.update(chunk)
                    bytes_read += len(chunk)
                    
                    if progress_callback and file_size > 0:
                        progress = (bytes_read / file_size) * 100
                        progress_callback(file_path, progress)
                        
        except (IOError, OSError) as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
        
        return hash_func.hexdigest()
    
    def calculate_hashes_batch(self, file_paths: List[str],
                             progress_callback: Optional[Callable] = None) -> Dict[str, str]:
        """
        Calculate hashes for multiple files
        
        Args:
            file_paths: List of file paths
            progress_callback: Callback for batch progress
            
        Returns:
            Dictionary mapping file paths to hashes
        """
        results = {}
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            try:
                file_hash = self.calculate_hash(file_path)
                results[file_path] = file_hash
                
                if progress_callback:
                    batch_progress = ((i + 1) / total_files) * 100
                    progress_callback(batch_progress, file_path, file_hash)
                    
            except Exception as e:
                logger.error(f"Failed to hash {file_path}: {e}")
                continue
        
        return results
    
    def quick_hash_comparison(self, file1: str, file2: str) -> bool:
        """
        Quick comparison using file size and partial hashing
        for initial duplicate screening
        """
        # Compare file sizes first
        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)
        
        if size1 != size2:
            return False
        
        # Compare first few chunks
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                for _ in range(3):  # Compare first 3 chunks
                    chunk1 = f1.read(self.chunk_size)
                    chunk2 = f2.read(self.chunk_size)
                    
                    if chunk1 != chunk2:
                        return False
                        
                    if not chunk1:  # End of file
                        break
        except IOError:
            return False
        
        return True

    def get_available_algorithms(self) -> List[str]:
        """Get list of available hash algorithms"""
        return list(self.HASH_ALGORITHMS.keys())