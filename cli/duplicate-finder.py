import os
import hashlib
import argparse
import sys
import shutil
from collections import defaultdict
from datetime import datetime
import time

# --- Configuration Constants ---
HASH_CHUNK_SIZE = 65536     # 64 KB chunks for reading large files
PARTIAL_HASH_SIZE = 4096    # Check first 4 KB for intermediate pigeonhole
ZERO_BYTE_SIZE = 0

# --- Helper Functions for Hashing ---

def _hash_file_chunked(filepath, size_limit=None, hash_algorithm=hashlib.sha256):
    """
    Calculates the hash of a file up to a specified size limit.
    Reads the file in chunks to handle large files efficiently.
    """
    hasher = hash_algorithm()
    bytes_read = 0
    
    try:
        with open(filepath, 'rb') as f:
            while True:
                # Determine how much chunk to read
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
        print(f"\n[ERROR] Failed to read or hash file {filepath}: {e}", file=sys.stderr)
        return None

def get_partial_hash(filepath):
    """Calculates the hash of the first 4KB (PARTIAL_HASH_SIZE)."""
    return _hash_file_chunked(filepath, size_limit=PARTIAL_HASH_SIZE)

def get_full_hash(filepath):
    """Calculates the hash of the entire file."""
    return _hash_file_chunked(filepath)

# --- Core Logic Functions ---

def scan_files(root_path, allowed_extensions, min_size, include_zero_byte):
    """
    PIGEONHOLE LEVEL 1: Recursively scans directory and groups files by size.
    Applies initial filtering (extension, min size, zero-byte handling).
    """
    files_by_size = defaultdict(list)
    
    print(f"\n[PHASE 1] Scanning {root_path} and Grouping by Size...")

    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            if not os.path.isfile(filepath):
                continue
                
            try:
                file_size = os.path.getsize(filepath)
                
                # 1. Zero-byte handling
                if file_size == ZERO_BYTE_SIZE and not include_zero_byte:
                    continue

                # 2. Minimum size filtering
                if file_size < min_size:
                    continue

                # 3. Extension filtering
                if allowed_extensions:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in allowed_extensions:
                        continue
                        
                files_by_size[file_size].append(filepath)
            
            except OSError as e:
                # Handle permission denied or other system errors
                print(f"[WARNING] Skipping file {filepath} due to OS error: {e}", file=sys.stderr)

    return files_by_size

def find_duplicates(files_by_size):
    """
    PIGEONHOLE LEVEL 2 & 3: Refines size-based groups using partial and full hashing.
    """
    potential_duplicates = defaultdict(list)
    confirmed_duplicates = []
    
    # Filter for groups that have more than one file (i.e., potential duplicates)
    groups_to_check = {size: paths for size, paths in files_by_size.items() if len(paths) > 1}
    total_potential = sum(len(paths) for paths in groups_to_check.values())
    
    if not total_potential:
        return []
        
    print(f"\n[PHASE 2] Starting 3-Level Pigeonhole Check on {total_potential} potential files...")

    # LEVEL 2: Partial Hash Check
    partial_hash_count = 0
    for file_list in groups_to_check.values():
        
        # Group same-sized files by partial hash
        files_by_partial_hash = defaultdict(list)

        for filepath in file_list:
            partial_hash = get_partial_hash(filepath)
            partial_hash_count += 1
            print(f"\r Hashing Level 2 Progress: {partial_hash_count}/{total_potential} files...", end='', flush=True)

            if partial_hash:
                files_by_partial_hash[partial_hash].append(filepath)

        # Move groups with confirmed partial duplicates to the next level
        for partial_hash, paths in files_by_partial_hash.items():
            if len(paths) > 1:
                potential_duplicates[partial_hash].extend(paths)

    print("\n Hashing Level 2 Complete.")

    # LEVEL 3: Full Hash Check (only on groups that passed Level 2)
    total_to_full_hash = sum(len(paths) for paths in potential_duplicates.values())
    
    if not total_to_full_hash:
        print("No files passed the partial hash check.")
        return []
        
    print(f"\n[PHASE 3] Starting Full Hash Check on {total_to_full_hash} files...")
    
    full_hash_count = 0
    # Process files that matched both size and partial hash
    for file_list in potential_duplicates.values():
        
        # Group partial-hash-matched files by full hash
        files_by_full_hash = defaultdict(list)

        for filepath in file_list:
            full_hash = get_full_hash(filepath)
            full_hash_count += 1
            print(f"\r Hashing Level 3 Progress: {full_hash_count}/{total_to_full_hash} files...", end='', flush=True)

            if full_hash:
                files_by_full_hash[full_hash].append(filepath)

        # A set with len > 1 is a CONFIRMED duplicate group
        for _, paths in files_by_full_hash.items():
            if len(paths) > 1:
                confirmed_duplicates.append(paths)

    print("\n Hashing Level 3 Complete.")
    return confirmed_duplicates

# --- Action and Selection Functions ---

def select_original_file(duplicate_set, keep_mode):
    """
    Selects the 'original' file based on the specified keep_mode.
    Returns the path of the file to KEEP.
    """
    
    # Helper to get file modification time (timestamp)
    def get_mtime(path):
        try:
            return os.path.getmtime(path)
        except:
            # Default to 0 if metadata is inaccessible
            return 0 

    if keep_mode == 'newest':
        # Select the file with the largest modification timestamp (newest)
        return max(duplicate_set, key=get_mtime)
    
    elif keep_mode == 'oldest':
        # Select the file with the smallest modification timestamp (oldest)
        return min(duplicate_set, key=get_mtime)
        
    elif keep_mode == 'path_length':
        # Select the file with the shortest path string (often implies a root/original location)
        return min(duplicate_set, key=len)
        
    # Default is 'newest' if something goes wrong
    return max(duplicate_set, key=get_mtime)

def process_action(duplicate_set, original_path, action, move_path=None):
    """
    Performs deletion or moving on all files in the set EXCEPT the original.
    Returns the count of files successfully processed.
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
                # Ensure the target directory exists
                os.makedirs(move_path, exist_ok=True)
                
                # Create a unique destination path to prevent overwrites
                filename = os.path.basename(target_path)
                dest_path = os.path.join(move_path, filename)
                
                # If destination exists, append a timestamp
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

# --- Reporting Functions ---

def generate_report(duplicate_sets, args, start_time):
    """
    Generates the final report to the console and optionally to a file.
    """
    end_time = time.time()
    total_runtime = end_time - start_time
    total_sets = len(duplicate_sets)
    total_duplicates = sum(len(s) - 1 for s in duplicate_sets)
    
    
    report_content = []
    
    report_content.append("=====================================================================")
    report_content.append("             DUPLICATE FILE FINDER - FINAL REPORT                    ")
    report_content.append("=====================================================================")
    report_content.append(f"Scan Time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    report_content.append(f"Runtime: {total_runtime:.2f} seconds")
    report_content.append("-" * 65)
    report_content.append(f"Target Path: {args.path}")
    report_content.append(f"Keep Mode: {args.keep_mode}")
    report_content.append(f"Zero-Byte Files Included: {args.include_zero_byte}")
    report_content.append(f"Action Taken: {args.action or 'None'}")
    if args.move_path:
        report_content.append(f"Move Directory: {args.move_path}")
    report_content.append("-" * 65)
    
    if total_sets == 0:
        report_content.append("\nSUCCESS: No confirmed duplicate file sets found.")
    else:
        report_content.append(f"\nSummary: Found {total_sets} Duplicate Set(s) containing {total_duplicates} duplicate files.")
        
        total_processed = 0
        
        for i, duplicate_set in enumerate(duplicate_sets, 1):
            
            original_path = select_original_file(duplicate_set, args.keep_mode)
            
            report_content.append(f"\n[DUPLICATE SET {i}] ({len(duplicate_set)} files)")
            report_content.append(f"  Original ({args.keep_mode}): {original_path}")
            
            files_to_remove = [p for p in duplicate_set if p != original_path]
            
            # --- Perform Action if requested ---
            if args.action:
                processed_count = process_action(duplicate_set, original_path, args.action, args.move_path)
                total_processed += processed_count
                report_content.append(f"  Action Result: Successfully processed {processed_count} file(s).")
                
            report_content.append("  Files Found (Duplicates to be acted upon):")
            for path in files_to_remove:
                report_content.append(f"    - {path}")
                
        report_content.append("-" * 65)
        report_content.append(f"Total Duplicates Identified: {total_duplicates}")
        if args.action:
            report_content.append(f"Total Duplicates Processed ({args.action.upper()}): {total_processed}")
            
    report_content.append("=====================================================================")

    # Print to console
    print("\n" + "\n".join(report_content))
    
    # Write to output file if requested
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write("\n".join(report_content))
            print(f"\n[INFO] Report successfully saved to: {args.output}")
        except Exception as e:
            print(f"\n[ERROR] Could not write report to file {args.output}: {e}", file=sys.stderr)


# --- Main Execution ---

def main():
    """Parses arguments and runs the duplicate finder workflow."""
    parser = argparse.ArgumentParser(
        description="A robust CLI Duplicate File Finder using 3-Level Pigeonhole Principle (Size -> Partial Hash -> Full Hash)."
    )
    
    # Required Argument
    parser.add_argument(
        "path",
        type=str,
        help="The root directory path to scan for duplicate files."
    )
    
    # Optional Filtering Arguments
    parser.add_argument(
        "--ext",
        type=str,
        default="",
        help="Comma-separated list of file extensions to include (e.g., jpg,png,pdf). Case-insensitive."
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=0,
        help="Minimum file size (in bytes) to consider for scanning. Default is 0."
    )
    parser.add_argument(
        "--include-zero-byte",
        action="store_true",
        help="Include zero-byte files (which are always duplicates of each other) in the scan."
    )
    
    # Action Arguments
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--delete",
        action="store_const",
        const="delete",
        dest="action",
        help="DELETE all duplicate files found, keeping only the original."
    )
    action_group.add_argument(
        "--move",
        action="store_const",
        const="move",
        dest="action",
        help="MOVE all duplicate files found to a specified directory, keeping only the original."
    )
    parser.add_argument(
        "--move-path",
        type=str,
        help="The destination directory for files when using --move."
    )
    
    # Keep Original Argument
    parser.add_argument(
        "--keep-mode",
        type=str,
        choices=['newest', 'oldest', 'path_length'],
        default='newest',
        help="Criteria used to select the 'original' file to keep: 'newest' (default), 'oldest', or 'path_length' (shortest path)."
    )

    # Output Argument
    parser.add_argument(
        "--output",
        type=str,
        help="Save the final report to the specified file path (e.g., report.txt)."
    )
    
    args = parser.parse_args()
    
    # --- Pre-Execution Validation ---
    root_path = os.path.abspath(args.path)

    if not os.path.isdir(root_path):
        print(f"Error: Path '{root_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)
        
    if args.action == 'move' and not args.move_path:
        print("Error: When using --move, you must specify a destination path using --move-path.", file=sys.stderr)
        sys.exit(1)

    # Prepare extensions list
    allowed_extensions = {f".{ext.strip().lower()}" for ext in args.ext.split(',')} if args.ext else set()

    start_time = time.time()
    print(f"\nStarting Duplicate Finder Scan at {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # --- 1. Scan and Size Pigeonhole (Level 1) ---
    files_by_size = scan_files(root_path, allowed_extensions, args.min_size, args.include_zero_byte)

    # --- 2. Hashing Pigeonhole (Level 2 & 3) ---
    duplicate_sets = find_duplicates(files_by_size)

    # --- 3. Reporting and Action ---
    generate_report(duplicate_sets, args, start_time)

if __name__ == "__main__":
    main()

