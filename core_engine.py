import hashlib
from collections import defaultdict
import sys

# --- Configuration Constants (Owned by Core) ---
HASH_CHUNK_SIZE = 65536     # 64 KB chunks for reading large files
PARTIAL_HASH_SIZE = 4096    # Check first 4 KB for intermediate pigeonhole

# --- Core Hashing Logic ---

def _hash_file_chunked(filepath, size_limit=None, hash_algorithm=hashlib.sha256):
    """
    Calculates the hash of a file up to a specified size limit, reading in chunks.
    This method is the heart of Member 1's work.
    """
    hasher = hash_algorithm()
    bytes_read = 0
    
    try:
        with open(filepath, 'rb') as f:
            while True:
                # Determine chunk size based on remaining limit, if specified
                remaining = size_limit - bytes_read if size_limit is not None else HASH_CHUNK_SIZE
                chunk_size = min(HASH_CHUNK_SIZE, remaining) if size_limit is not None else HASH_CHUNK_SIZE
                
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
    except Exception as e:
        print(f"\n[ERROR] Core Engine failed to read/hash {filepath}: {e}", file=sys.stderr)
        return None

def get_partial_hash(filepath):
    """Exposed method for generating the Level 2 Pigeonhole hash."""
    return _hash_file_chunked(filepath, size_limit=PARTIAL_HASH_SIZE)

def get_full_hash(filepath):
    """Exposed method for generating the Level 3 confirmation hash."""
    return _hash_file_chunked(filepath)


# --- Core Duplicate Finding Logic (Pigeonhole Levels 2 & 3) ---

def find_duplicates(files_by_size):
    """
    Refines size-based groups using partial and full hashing to confirm duplicates.
    This function is Member 1's primary output (the API for the rest of the team).
    """
    potential_duplicates = defaultdict(list)
    confirmed_duplicates = []
    
    # Filter for groups that have more than one file (i.e., potential duplicates)
    groups_to_check = {size: paths for size, paths in files_by_size.items() if len(paths) > 1}
    total_potential = sum(len(paths) for paths in groups_to_check.values())
    
    if not total_potential:
        print("INFO: No files found with matching sizes.")
        return []
        
    print(f"\n[M1] Starting 3-Level Pigeonhole Check on {total_potential} potential files...")

    # LEVEL 2: Partial Hash Check (Intermediate Pigeonhole)
    for file_list in groups_to_check.values():
        files_by_partial_hash = defaultdict(list)
        for filepath in file_list:
            partial_hash = get_partial_hash(filepath)
            if partial_hash:
                files_by_partial_hash[partial_hash].append(filepath)

        # Move groups with confirmed partial duplicates to the next level
        for partial_hash, paths in files_by_partial_hash.items():
            if len(paths) > 1:
                potential_duplicates[partial_hash].extend(paths)

    # LEVEL 3: Full Hash Check (Final Confirmation)
    total_to_full_hash = sum(len(paths) for paths in potential_duplicates.values())
    print(f"[M1] Passing {total_to_full_hash} files to Full Hash Check (Level 3)...")
    
    if not total_to_full_hash:
        return []

    for file_list in potential_duplicates.values():
        files_by_full_hash = defaultdict(list)

        for filepath in file_list:
            full_hash = get_full_hash(filepath)
            if full_hash:
                files_by_full_hash[full_hash].append(filepath)

        # A set with len > 1 is a CONFIRMED duplicate group
        for _, paths in files_by_full_hash.items():
            if len(paths) > 1:
                confirmed_duplicates.append(paths)

    return confirmed_duplicates

