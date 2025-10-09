This file is important for contributors and developers, as it describes the high-level design and structure of the project's codebase.

Markdown

# Architecture

Understanding the project's architecture is key to contributing effectively and making informed decisions about development.

## High-Level Overview

**[Your Project Name]** follows a **[Pattern, e.g., Layered, Microservice, MVC]** architecture. Its core philosophy is **[e.g., separation of concerns, performance, extensibility]**.

At a high level, the system is composed of three main layers:

1.  **Presentation Layer:** Handles input/output (HTTP, CLI, GUI).
2.  **Business/Service Layer:** Contains the core logic and handles interactions between the presentation and data layers.
3.  **Data Layer:** Manages persistence (database, file system, external APIs).

# Pigeon Finder - Architecture Overview

This document explains the core architecture of Pigeon Finder, focusing on the duplicate-finding pipeline, threading model, and how modules interact.

## High-level components

- UI (`pigeon_finder_gui.py`)
	- PyQt5-based desktop GUI. Hosts the main window, status bar, progress bar, controls and results table.
	- Starts a background `ScanWorker` that runs in a `QThread` to avoid blocking the GUI.

- File scanning (`file_io.py`)
	- Responsible for recursive filesystem traversal and Level 1 grouping by file size. Exposes `scan_files` with optional progress callback.

- Pigeonhole engine (`core/pigeonhole_engine.py`)
	- Implements the two-stage duplicate detection for candidate sets produced from size groups:
		1. Quick screen: partial byte comparisons and lightweight checks to reduce candidates.
		2. Full hashing: chunked hashing (to limit memory usage) and exact duplicate confirmation.

- Hashing utilities (`core/hashing.py`)
	- Provides chunked hashing functions and constants (e.g., partial read length for quick screen and chunk size for full hashing).

- Duplicate manager (`core/duplicate_manager.py`)
	- Collects, merges and formats duplicate groups for the UI or CLI output. Performs selection of the canonical/original file within each group.

## Data flow

1. User triggers a scan from the GUI (or runs the CLI). The GUI creates a `ScanWorker` and starts a `QThread`.
2. `ScanWorker` calls `file_io.scan_files(root_path, ...)`, passing a small progress callback.
3. `scan_files` returns a mapping size -> [paths]. The worker forwards this to `PigeonholeEngine.find_duplicates`.
4. `PigeonholeEngine` iterates each size group. For groups with >1 file, it applies the quick screen to prune obviously non-duplicates.
5. Remaining candidate groups are hashed using chunked reads by `FileHasher.calculate_hash` and compared to confirm duplicates.
6. The engine collects confirmed duplicates into canonical groups and returns a mapping original -> [duplicates].
7. `ScanWorker` emits progress and final results back to the GUI via Qt signals. The GUI updates the table and status bar.

## Threading & Concurrency

- The GUI runs in the main thread. Long-running operations (scan + hashing) run in a secondary `QThread` managed by `ScanWorker`.
- Communication uses Qt signals (progress_update, scan_complete, error_occurred) to marshal data safely across threads.

## Hashing & Performance considerations

- Quick screen: The engine performs small, fixed-length byte comparisons at deterministic offsets (start/middle/end) to quickly rule out mismatches without hashing.
- Chunked hashing: Files are hashed in fixed-size chunks to avoid loading large files entirely into memory. Hash state is updated per-chunk.
- Aggregate operations: For algorithm-critical code (grouping, selection, aggregation), we avoid Python built-in helpers like `min`, `max`, `sum`, `sorted`, `any`, `all`. Instead, explicit loops are used for clarity and to ensure consistent behavior across Python versions.

## Extensibility

- Hash algorithms: `PigeonholeEngine` accepts a hash algorithm parameter (e.g., 'md5', 'sha256') to switch algorithms.
- New quick-screen heuristics can be added into the engine without changing the high-level data flow.

## Deployment notes

- Desktop: The project runs as a standalone PyQt5 application. Use the provided `quick_setup.ps1` to create a `.venv` and install dependencies on Windows.
- Packaging: PyInstaller spec files may be used for generating standalone executables; careful handling of binary wheels (PyQt5, Pillow) is needed on Windows.

## Diagram (text)

GUI -> ScanWorker(QThread) -> file_io.scan_files -> PigeonholeEngine -> core.hashing -> DuplicateManager -> GUI

Each arrow represents a function call or signal emission and the primary direction of data flow.






