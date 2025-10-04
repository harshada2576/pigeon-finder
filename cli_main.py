import argparse
import sys
import os
import time
from datetime import datetime

# --- Import components from other team members ---
from core_engine import find_duplicates 
from file_io import scan_files, process_action, select_original_file

# --- Reporting Functions (M5 Responsibility) ---

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
    report_content.append(f"Action Taken: {args.action or 'None'}")
    report_content.append("-" * 65)
    
    if total_sets == 0:
        report_content.append("\nSUCCESS: No confirmed duplicate file sets found.")
    else:
        report_content.append(f"\nSummary: Found {total_sets} Duplicate Set(s) containing {total_duplicates} duplicate files.")
        
        total_processed = 0
        
        for i, duplicate_set in enumerate(duplicate_sets, 1):
            
            # Use M2's utility to select the original
            original_path = select_original_file(duplicate_set, args.keep_mode)
            
            report_content.append(f"\n[DUPLICATE SET {i}] ({len(duplicate_set)} files)")
            report_content.append(f"  Original ({args.keep_mode}): {original_path}")
            
            # --- Perform Action if requested (using M2's function) ---
            if args.action:
                processed_count = process_action(duplicate_set, original_path, args.action, args.move_path)
                total_processed += processed_count
                report_content.append(f"  Action Result: Successfully processed {processed_count} file(s).")
                
            report_content.append("  Files Found (Duplicates to be acted upon):")
            files_to_remove = [p for p in duplicate_set if p != original_path]
            for path in files_to_remove:
                report_content.append(f"    - {path}")
                
        report_content.append("-" * 65)
        report_content.append(f"Total Duplicates Identified: {total_duplicates}")
        if args.action:
            report_content.append(f"Total Duplicates Processed ({args.action.upper()}): {total_processed}")
            
    report_content.append("=====================================================================")

    # Print to console and save to output file
    print("\n" + "\n".join(report_content))
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write("\n".join(report_content))
            print(f"\n[INFO] Report successfully saved to: {args.output}")
        except Exception as e:
            print(f"\n[ERROR] Could not write report to file {args.output}: {e}", file=sys.stderr)


# --- Main Execution Workflow (M5 Integration Responsibility) ---

def main():
    """Parses arguments and runs the integrated duplicate finder workflow."""
    
    # Argument Parsing (M4 Responsibility)
    parser = argparse.ArgumentParser(
        description="A robust CLI Duplicate File Finder using 3-Level Pigeonhole Principle (Size -> Partial Hash -> Full Hash)."
    )
    
    parser.add_argument("path", type=str, help="The root directory path to scan.")
    parser.add_argument("--ext", type=str, default="", help="Comma-separated list of file extensions.")
    parser.add_argument("--min-size", type=int, default=0, help="Minimum file size (in bytes) to consider.")
    parser.add_argument("--include-zero-byte", action="store_true", help="Include zero-byte files in the scan.")
    
    # Action Group
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--delete", action="store_const", const="delete", dest="action", help="DELETE all duplicate files.")
    action_group.add_argument("--move", action="store_const", const="move", dest="action", help="MOVE all duplicate files.")
    parser.add_argument("--move-path", type=str, help="Destination directory for files when using --move.")
    
    # Keep Original
    parser.add_argument(
        "--keep-mode",
        type=str,
        choices=['newest', 'oldest', 'path_length'],
        default='newest',
        help="Criteria to select the 'original' file to keep: 'newest' (default), 'oldest', or 'path_length' (shortest path)."
    )

    # Output Argument
    parser.add_argument("--output", type=str, help="Save the final report to the specified file path.")
    
    args = parser.parse_args()
    
    # --- Pre-Execution Validation ---
    root_path = os.path.abspath(args.path)
    if not os.path.isdir(root_path):
        print(f"Error: Path '{root_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)
        
    if args.action == 'move' and not args.move_path:
        print("Error: When using --move, you must specify a destination path using --move-path.", file=sys.stderr)
        sys.exit(1)

    allowed_extensions = {f".{ext.strip().lower()}" for ext in args.ext.split(',')} if args.ext else set()

    start_time = time.time()
    print(f"\nStarting Duplicate Finder Scan at {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # --- 1. M2: Scan and Size Pigeonhole (Level 1) ---
    files_by_size = scan_files(root_path, allowed_extensions, args.min_size, args.include_zero_byte)

    # --- 2. M1: Hashing Pigeonhole (Level 2 & 3) ---
    duplicate_sets = find_duplicates(files_by_size)

    # --- 3. M5: Reporting and Action ---
    generate_report(duplicate_sets, args, start_time)

if __name__ == "__main__":
    main()

