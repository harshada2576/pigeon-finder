import hashlib
import os
import logging

logger = logging.getLogger(__name__)

class FileHasher:
    HASH_ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512,
    }
    
    def __init__(self, algorithm='md5', chunk_size=8192):
        self.algorithm = algorithm.lower()
        self.chunk_size = chunk_size
        
        if self.algorithm not in self.HASH_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def calculate_hash(self, file_path, progress_callback=None):
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