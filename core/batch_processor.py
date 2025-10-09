"""
Advanced Batch Processing for Large Operations
"""

import threading
import queue
import time
from typing import List, Dict, Callable, Any
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class BatchProcessor:
    """
    Advanced batch processor with threading and progress tracking
    for handling large file operations
    """
    
    def __init__(self, max_workers=4, batch_size=100):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.workers = []
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.is_running = False
        self.progress_callbacks = []
    
    def add_progress_callback(self, callback: Callable):
        """Add progress callback function"""
        self.progress_callbacks.append(callback)
    
    def process_batch(self, tasks: List[Any], process_func: Callable) -> List[Any]:
        """
        Process a batch of tasks using multiple threads
        
        Args:
            tasks: List of tasks to process
            process_func: Function to process each task
            
        Returns:
            List of results
        """
        if not tasks:
            return []
        
        self.is_running = True
        self.workers = []
        results = []
        
        # Split tasks into batches
        batches = [tasks[i:i + self.batch_size] for i in range(0, len(tasks), self.batch_size)]
        
        total_batches = len(batches)
        completed_batches = 0
        
        def worker(batch, batch_index):
            """Worker function to process a batch"""
            batch_results = []
            for task_index, task in enumerate(batch):
                if not self.is_running:
                    break
                
                try:
                    result = process_func(task)
                    batch_results.append(result)
                    
                    # Calculate overall progress
                    overall_progress = ((batch_index * self.batch_size + task_index + 1) / len(tasks)) * 100
                    self._notify_progress(overall_progress, f"Processing batch {batch_index + 1}/{total_batches}")
                    
                except Exception as e:
                    logger.error(f"Batch processing error for task {task}: {e}")
                    batch_results.append({'error': str(e), 'task': task})
            
            self.result_queue.put((batch_index, batch_results))
        
        # Start workers for each batch
        for i, batch in enumerate(batches):
            if not self.is_running:
                break
            thread = threading.Thread(target=worker, args=(batch, i))
            thread.daemon = True
            thread.start()
            self.workers.append(thread)
        
        # Collect results
        batch_results = [None] * total_batches
        
        while completed_batches < total_batches and self.is_running:
            try:
                batch_index, results_batch = self.result_queue.get(timeout=1.0)
                batch_results[batch_index] = results_batch
                completed_batches += 1
                
                self._notify_progress(
                    (completed_batches / total_batches) * 100,
                    f"Completed {completed_batches}/{total_batches} batches"
                )
                
            except queue.Empty:
                continue
        
        # Flatten results
        for batch in batch_results:
            if batch:
                results.extend(batch)
        
        self.is_running = False
        return results
    
    def stop_processing(self):
        """Stop batch processing"""
        self.is_running = False
        for worker in self.workers:
            worker.join(timeout=1.0)
    
    def _notify_progress(self, progress: float, message: str):
        """Notify progress to all callbacks"""
        for callback in self.progress_callbacks:
            try:
                callback(progress, message)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

class SmartBatchManager:
    """
    Smart batch manager that optimizes operations based on file characteristics
    """
    
    def __init__(self):
        self.processor = BatchProcessor()
        self.operation_history = []
    
    def optimize_batch_size(self, file_paths: List[str]) -> int:
        """Dynamically determine optimal batch size based on file characteristics"""
        if not file_paths:
            return 100
        # Compute total size of existing files without using built-in sum()
        total_size = 0
        for f in file_paths:
            try:
                if os.path.exists(f):
                    total_size += os.path.getsize(f)
            except Exception:
                # Ignore files we cannot stat
                continue

        avg_size = total_size / len(file_paths) if file_paths else 0
        
        # Adjust batch size based on average file size
        if avg_size > 100 * 1024 * 1024:  # > 100MB
            return 10
        elif avg_size > 10 * 1024 * 1024:  # > 10MB
            return 25
        elif avg_size > 1 * 1024 * 1024:  # > 1MB
            return 50
        else:
            return 100
    
    def batch_delete(self, file_paths: List[str], use_trash: bool = True) -> Dict:
        """Batch delete files with optimization"""
        from ..core.duplicate_manager import DuplicateManager
        
        self.processor.batch_size = self.optimize_batch_size(file_paths)
        
        def delete_task(file_path):
            try:
                if use_trash:
                    from send2trash import send2trash
                    send2trash(file_path)
                else:
                    os.remove(file_path)
                return {'success': True, 'file': file_path}
            except Exception as e:
                return {'success': False, 'file': file_path, 'error': str(e)}
        
        results = self.processor.process_batch(file_paths, delete_task)
        
        # Analyze results
        success_count = 0
        failed_files = []
        for r in results:
            if r.get('success'):
                success_count += 1
            else:
                try:
                    failed_files.append(r['file'])
                except Exception:
                    # ignore malformed result entries
                    continue
        
        return {
            'total': len(file_paths),
            'success': success_count,
            'failed': len(failed_files),
            'failed_files': failed_files
        }
    
    def batch_move(self, file_paths: List[str], destination: str) -> Dict:
        """Batch move files with optimization"""
        self.processor.batch_size = self.optimize_batch_size(file_paths)
        
        os.makedirs(destination, exist_ok=True)
        
        def move_task(file_path):
            try:
                filename = Path(file_path).name
                dest_path = os.path.join(destination, filename)
                
                # Handle filename conflicts
                counter = 1
                base_name = Path(filename).stem
                extension = Path(filename).suffix
                
                while os.path.exists(dest_path):
                    new_filename = f"{base_name}_{counter}{extension}"
                    dest_path = os.path.join(destination, new_filename)
                    counter += 1
                
                import shutil
                shutil.move(file_path, dest_path)
                return {'success': True, 'file': file_path, 'new_path': dest_path}
            except Exception as e:
                return {'success': False, 'file': file_path, 'error': str(e)}
        
        results = self.processor.process_batch(file_paths, move_task)
        
        # Analyze results
        success_count = 0
        failed_files = []
        for r in results:
            if r.get('success'):
                success_count += 1
            else:
                try:
                    failed_files.append(r['file'])
                except Exception:
                    continue
        
        return {
            'total': len(file_paths),
            'success': success_count,
            'failed': len(failed_files),
            'failed_files': failed_files,
            'destination': destination
        }
    
    def batch_hash(self, file_paths: List[str], algorithm: str = 'md5') -> Dict:
        """Batch compute file hashes"""
        from ..core.hashing import FileHasher
        
        self.processor.batch_size = self.optimize_batch_size(file_paths)
        hasher = FileHasher(algorithm)
        
        def hash_task(file_path):
            try:
                file_hash = hasher.calculate_hash(file_path)
                return {
                    'success': True, 
                    'file': file_path, 
                    'hash': file_hash,
                    'size': os.path.getsize(file_path)
                }
            except Exception as e:
                return {'success': False, 'file': file_path, 'error': str(e)}
        
        results = self.processor.process_batch(file_paths, hash_task)
        
        # Group by hash to find duplicates
        hash_groups = {}
        for result in results:
            if result.get('success'):
                file_hash = result['hash']
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(result['file'])
        
        # Filter groups with duplicates
        duplicate_groups = {}
        for hash_val, files in hash_groups.items():
            if len(files) > 1:
                duplicate_groups[hash_val] = files

        processed_count = 0
        failed_count = 0
        for r in results:
            if r.get('success'):
                processed_count += 1
            else:
                failed_count += 1

        return {
            'total': len(file_paths),
            'processed': processed_count,
            'failed': failed_count,
            'duplicate_groups': duplicate_groups,
            'results': results
        }
    
    def get_operation_stats(self) -> Dict:
        """Get statistics about batch operations"""
        if not self.operation_history:
            return {}
        
        total_operations = len(self.operation_history)

        successful_operations = 0
        total_files_processed = 0
        for op in self.operation_history:
            try:
                if op.get('success', 0) > 0:
                    successful_operations += 1
            except Exception:
                # ignore malformed history entries
                pass
            try:
                total_files_processed += int(op.get('total', 0))
            except Exception:
                # ignore entries with non-numeric totals
                continue
        
        return {
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'success_rate': (successful_operations / total_operations * 100) if total_operations > 0 else 0,
            'total_files_processed': total_files_processed,
            'average_batch_size': total_files_processed / total_operations if total_operations > 0 else 0
        }