# API Reference

This document describes the main public classes and functions in Pigeon Finder for programmatic use.

## file_io (top-level module)

- scan_files(root_path: str,
                               allowed_extensions: set[str] | None,
                               min_size: int = 0,
                               include_zero_byte: bool = True,
                               progress_callback: callable | None = None) -> dict[int, list[str]]
     - Behavior: Recursively scans `root_path` and groups discovered files by file size (Level 1 pigeonhole grouping).
     - Returns: a mapping {file_size: [file_path, ...]} for all files matching the filters.
     - Progress callback: if provided it is invoked as `progress_callback(seen: int, total: int)` where `seen` is number of files processed and `total` is an estimated total candidates (may be None or 0 if unknown).
     - Errors: raises `OSError`/`PermissionError` when directories cannot be read; callers should catch exceptions when scanning protected locations.

- select_original_file(duplicate_set: list[str], keep_mode: str = 'newest') -> str
     - Behavior: given a list of equal-sized duplicate file paths, returns the path chosen as the "original" to keep.
     - keep_mode options: `'newest'` (keep file with newest mtime), `'oldest'` (keep oldest mtime), `'path_length'` (keep the shortest path string), `'first'` (default deterministic selection: first in list).
     - Implementation note: selection is performed with explicit loops, not via `min`/`max` built-ins, to keep behavior explicit and portable.

- process_action(duplicate_set: list[str], original_path: str, action: str, move_path: str | None = None) -> int
     - Behavior: performs filesystem operations on every path in `duplicate_set` except `original_path`.
     - action: `'delete'` or `'move'`.
     - For `'move'` the `move_path` must be provided; files are moved into that directory preserving filenames (with collision handling).
     - Returns: the number of successfully processed files (int).
     - Errors: on filesystem errors, the function will skip the failing file and continue; it returns a count of successful operations. It may also log or raise depending on the `file_io` configuration.

## core.pigeonhole_engine.PigeonholeEngine

- class PigeonholeEngine(hash_algorithm: str = 'md5')
     - find_duplicates(file_groups: dict[int, list[str]], progress_callback: callable | None = None) -> dict[str, list[str]]
          - Input: a mapping produced by `scan_files` (size -> [paths]).
          - Output: mapping from canonical/original file path -> list of duplicate file paths.
          - Internal behavior: For each size group with more than one file:
                    1. Quick screening (partial byte comparisons) to remove obvious non-matches.
                    2. Chunked full hashing for remaining candidates to confirm exact duplicates.
          - Progress callback: if provided, called as `progress_callback(stage: str, completed: int, total: int)` where `stage` is one of `"quick_screen"` or `"full_hash"`.
          - Error handling: I/O errors when reading files are caught per-file, logged, and do not abort the entire run.

     - get_optimization_stats() -> dict
          - Returns runtime statistics: number of files scanned, hash operations avoided (estimate), comparisons performed, and time spent per stage.

     - calculate_efficiency_gain(total_files: int) -> float
          - Returns a percentage estimating how many comparisons were avoided vs the naive O(n^2) approach. Used for reporting and not guaranteed exact.

## core.hashing.FileHasher

- This helper performs chunked hashing and quick partial comparisons.
     - calculate_hash(filepath: str) -> str
          - Reads the file in constant-size chunks and returns the hex digest string for the configured algorithm.
     - quick_hash_comparison(file1: str, file2: str, nbytes: int = 4096) -> bool
          - Reads `nbytes` from each file at deterministic offsets and returns True if the sampled bytes match. Used for quick screening to avoid full hashing.

## Other useful modules

- `core/file_scanner.py` — higher-level scanning utilities used by CLI and batch processors.
- `core/duplicate_manager.py` — helpers for grouping and formatting duplicate sets and for selecting originals.
- `cli/duplicate-finder.py` — example CLI wrapper showing how to call `scan_files` and `PigeonholeEngine` from scripts.

## Example: programmatic usage

```python
from file_io import scan_files, process_action
from core.pigeonhole_engine import PigeonholeEngine

files_by_size = scan_files(r"C:\Users\You\Pictures", {'.jpg', '.png'}, 0, True)
engine = PigeonholeEngine('sha256')

def progress(stage_or_seen, completed=None, total=None):
          # `scan_files` will call progress(seen, total);
          # PigeonholeEngine will call progress(stage, completed, total)
          print(stage_or_seen, completed, total)

duplicates = engine.find_duplicates(files_by_size, progress_callback=progress)
for original, dups in duplicates.items():
          print(original, '->', dups)

# Example: delete duplicates while keeping the original
for original, dups in duplicates.items():
          processed = process_action([original] + dups, original, action='delete')
          print(f"Processed {processed} files for group {original}")
```

## Notes & best practices

- When scanning large drives, prefer to limit `allowed_extensions` or set `min_size` to avoid scanning OS/system files.
- Use the progress callbacks to keep UIs responsive and provide user feedback; the GUI scan worker already consumes these callbacks and emits Qt signals.
- For very large datasets consider running hashing with a stronger algorithm (like `sha256`) for correctness; performance will be slower.
