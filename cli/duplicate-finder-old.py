import os
import hashlib
import argparse
from collections import defaultdict
import sys

# --- Configuration ---
HASH_CHUNK_SIZE = 65536  # Read file in 64KB chunks for efficient hashing

def get_file_hash(filepath, hash_algorithm=hashlib.sha256):
    """
    Calculates the hash of a file, reading it in chunks.
    This handles large files without loading the entire file into memory.
    """
    hasher = hash_algorithm()
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(HASH_CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        # Handle files that can't be opened (e.g., permissions errors)
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        return None

def find_duplicates(root_path):
    """
    Finds duplicate files in a directory using the Pigeonhole Principle.

    1. Pigeonhole Principle (Level 1): Group files by size.
    2. Pigeonhole Principle (Level 2): Group same-sized files by hash.
    """
    
    # 1. PIGEONHOLE LEVEL 1: Group files by size (the most effective filter)
    # The 'size' is the "pigeonhole" (container). Files of different sizes 
    # cannot be duplicates. Only groups with size > 1 need hashing.
    files_by_size = defaultdict(list)
    
    print(f"--- Phase 1: Scanning {root_path} and Grouping by Size (Pigeonhole) ---")
    
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            # Skip non-files or symbolic links to prevent infinite loops/errors
            if not os.path.isfile(filepath):
                continue
                
            try:
                file_size = os.path.getsize(filepath)
                # Store the file path in the list corresponding to its size
                files_by_size[file_size].append(filepath)
            except Exception as e:
                print(f"Warning: Could not get size of {filepath}. Skipping. Error: {e}")

    # 2. PIGEONHOLE LEVEL 2: Group same-sized files by hash
    # The 'hash' is the "pigeonhole" for this secondary check.
    duplicates = defaultdict(list)
    total_files_to_hash = sum(len(paths) for size, paths in files_by_size.items() if len(paths) > 1)
    
    print(f"\n--- Phase 2: Hashing {total_files_to_hash} Potential Duplicates ---")
    
    hashed_count = 0
    # Process only the groups where duplicates are possible (size > 1)
    for file_size, file_list in files_by_size.items():
        if len(file_list) > 1:
            
            # files_by_hash = {hash_value: [path1, path2, ...]}
            files_by_hash = defaultdict(list) 
            
            for filepath in file_list:
                file_hash = get_file_hash(filepath)
                hashed_count += 1
                
                # Simple progress indicator
                print(f"\r Hashing progress: {hashed_count}/{total_files_to_hash} files...", end='', flush=True)

                if file_hash:
                    files_by_hash[file_hash].append(filepath)

            # 3. Final Filtering: Identify the actual duplicate groups
            # Only hashes that map to more than one file are true duplicates
            for file_hash, paths in files_by_hash.items():
                if len(paths) > 1:
                    duplicates[file_hash].extend(paths)

    print("\r Hashing progress: Complete.                                           ")
    return duplicates

def generate_report(duplicates):
    """
    Prints the final set of duplicate file paths.
    """
    if not duplicates:
        print("\n--- REPORT ---")
        print("No duplicate files found.")
        return

    print("\n--- REPORT: DUPLICATE FILES FOUND ---")
    duplicate_count = 0
    
    for i, (file_hash, paths) in enumerate(duplicates.items(), 1):
        # Only report if a group is actually a duplicate (len > 1)
        if len(paths) > 1:
            print(f"\n[SET {i}] - Hash: {file_hash[:10]}... ({len(paths)} files)")
            for path in paths:
                print(f"  - {path}")
            duplicate_count += 1
    
    if duplicate_count == 0:
        print("\nNo duplicate files found (after hash validation).")
    else:
        print(f"\nTotal Duplicate Sets Found: {duplicate_count}")

def main():
    """
    Main function to handle CLI and execute the finder.
    """
    parser = argparse.ArgumentParser(
        description="A Duplicate File Finder using the Pigeonhole Principle for efficiency."
    )
    parser.add_argument(
        "path",
        type=str,
        help="The root directory path to scan for duplicate files."
    )
    args = parser.parse_args()
    
    root_path = os.path.abspath(args.path)

    if not os.path.isdir(root_path):
        print(f"Error: Path '{root_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Execute the core logic
    duplicate_groups = find_duplicates(root_path)

    # Generate the final report
    generate_report(duplicate_groups)

if __name__ == "__main__":
    main()
