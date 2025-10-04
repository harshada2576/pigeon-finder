import os
import shutil
from collections import defaultdict
from datetime import datetime

# --- Configuration Constants (Needed for Traversal/Filtering) ---
ZERO_BYTE_SIZE = 0

# --- File System Traversal (The Scanning Component) ---

def scan_files(root_path, allowed_extensions, min_size, include_zero_byte):
    """
    Member 2's primary task: Recursively scans directory and groups files by size (Pigeonhole Level 1).
    Applies filtering based on CLI arguments.
    """
    files_by_size = defaultdict(list)
    
    print(f"[M2] Scanning {root_path} and Grouping by Size (Level 1 Pigeonhole)...")

    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            if not os.path.isfile(filepath):
                continue
                
            try:
                file_size = os.path.getsize(filepath)
                
                # Filtering logic
                if file_size == ZERO_BYTE_SIZE and not include_zero_byte:
                    continue
                if file_size < min_size:
                    continue
                if allowed_extensions:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in allowed_extensions:
                        continue
                        
                files_by_size[file_size].append(filepath)
            
            except OSError as e:
                print(f"[WARNING] Skipping file {filepath} due to OS error: {e}", file=sys.stderr)

    return files_by_size

# --- Action Execution (The Writing/Altering Component) ---

def select_original_file(duplicate_set, keep_mode):
    """
    Selects the 'original' file based on the specified keep_mode.
    Member 2 provides this as a utility for Member 5's action logic.
    """
    
    def get_mtime(path):
        try:
            return os.path.getmtime(path)
        except:
            return 0 

    if keep_mode == 'newest':
        return max(duplicate_set, key=get_mtime)
    elif keep_mode == 'oldest':
        return min(duplicate_set, key=get_mtime)
    elif keep_mode == 'path_length':
        return min(duplicate_set, key=len)
        
    return max(duplicate_set, key=get_mtime)

def process_action(duplicate_set, original_path, action, move_path=None):
    """
    Performs deletion or moving on all files in the set EXCEPT the original.
    """
    processed_count = 0
    files_to_act_on = [p for p in duplicate_set if p != original_path]
    
    if not files_to_act_on:
        return 0

    print(f"  [ACTION] Keeping: {os.path.basename(original_path)}")

    for target_path in files_to_act_on:
        try:
            if action == 'delete':
                os.remove(target_path)
                print(f"  [DELETED] {target_path}")
            elif action == 'move':
                os.makedirs(move_path, exist_ok=True)
                
                filename = os.path.basename(target_path)
                dest_path = os.path.join(move_path, filename)
                
                # Create a unique path if destination already exists
                if os.path.exists(dest_path):
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    dest_path = os.path.join(move_path, f"{name}_DUP_{timestamp}{ext}")

                shutil.move(target_path, dest_path)
                print(f"  [MOVED] {target_path} -> {dest_path}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"  [ERROR] Failed to {action} {target_path}: {e}", file=sys.stderr)
            
    return processed_count

