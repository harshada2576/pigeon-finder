---

# 🐦 PigeonFinder: The Efficient Duplicate File Finder

PigeonFinder is a fast, robust, and feature-rich Command Line Interface (CLI) utility designed to scan large directories and swiftly identify and manage duplicate files. Its efficiency stems from applying the Pigeonhole Principle and using a 3-level hashing strategy to minimize unnecessary file reads.

---

## ✨ Features

PigeonFinder goes beyond simple file comparison by offering intelligent filtering and safe file management options:

- **3-Level Pigeonhole Check for Speed:**
  - **Level 1 (Size):** Groups files by size first (the primary "pigeonhole"). Files with different sizes are immediately ignored.
  - **Level 2 (Partial Hash):** Compares the hash of the first 4KB of content for potential duplicates.
  - **Level 3 (Full Hash):** Only files that pass the first two quick checks undergo the final, costly full SHA-256 hash validation.

- **Actionable Management:** Supports deletion (`--delete`) or moving (`--move`) of duplicate files.
- **Intelligent Keep Mode:** Automatically selects the file to keep (the "original") based on your chosen criteria: newest, oldest, or shortest path.
- **Filtering:** Filter scans by file extension (`--ext`) and minimum size (`--min-size`).
- **Zero-Byte Handling:** Option to include or exclude zero-byte files (which always register as duplicates).
- **Detailed Reporting:** Generates a comprehensive report to the console and/or an output file (`--output`).

---

## ⚙️ Installation

PigeonFinder is written in Python and uses only standard libraries, making installation straightforward.

### Prerequisites

- Python 3.8+

### Setup Steps

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/YOUR_USERNAME/PigeonFinder.git
    cd PigeonFinder
    ```

2. **Create and Activate a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # .\venv\Scripts\activate  # On Windows PowerShell
    ```

3. **Run the CLI:**

    Execute the main script directly. Since all files are modularized, ensure you run the command from the root directory of the project.

---

## 🚀 Usage

The program is run using:

```bash
python cli_main.py <TARGET_DIRECTORY> [OPTIONS]
````

### Argument Reference

| Flag                  | Category   | Description                                                                                        | Example                    |
| --------------------- | ---------- | -------------------------------------------------------------------------------------------------- | -------------------------- |
| `path` (Required)     | Target     | The root directory path to recursively scan for duplicates.                                        | `./MyPhotos`               |
| `--ext`               | Filtering  | Comma-separated list of extensions to include (e.g., jpg,png).                                     | `--ext mp4,mov`            |
| `--min-size`          | Filtering  | Minimum file size (in bytes) to scan. Excludes smaller files.                                      | `--min-size 1024`          |
| `--include-zero-byte` | Filtering  | Include zero-byte files in scan and report as duplicates.                                          | `--include-zero-byte`      |
| `--delete`            | Action     | Deletes all duplicates found, keeping the file selected by `--keep-mode`.                          | `--delete`                 |
| `--move`              | Action     | Moves all duplicates found to the path specified by `--move-path`.                                 | `--move`                   |
| `--move-path`         | Action     | Destination directory for duplicates when using `--move`.                                          | `--move-path ./RecycleBin` |
| `--keep-mode`         | Keep Logic | Determines the "original" to keep: `newest` (default), `oldest`, or `path_length` (shortest path). | `--keep-mode oldest`       |
| `--output`            | Reporting  | Saves the final console report to the specified file.                                              | `--output scan_log.txt`    |

### Usage Examples

* **Find Duplicates, Keep Newest (Default):**

  ```bash
  python cli_main.py /data/projects/backup
  ```

* **Move Duplicates, Filter by Size/Extension, Keep Oldest:**

  ```bash
  python cli_main.py /home/user/downloads --move --move-path /tmp/duplicates --ext mp4,avi --min-size 5000000 --keep-mode oldest
  ```

---

## 🏗️ Modular Architecture (For Developers)

The project is modularized based on the distinct responsibilities of the development team, ensuring clean separation of concerns:

| File Name        | Responsible Team Member        | Core Responsibility                                                                                                                                   |
| ---------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `core_engine.py` | Member 1 (Core Logic)          | Implements hashing algorithms (`get_full_hash`, `get_partial_hash`) and the 3-level Pigeonhole filtering logic (`find_duplicates`). Core engine.      |
| `file_io.py`     | Member 2 (I/O)                 | Manages disk interaction: file traversal (`scan_files`), file metadata retrieval, and destructive actions (`process_action`, `select_original_file`). |
| `cli_main.py`    | Members 4 & 5 (UI/Integration) | Handles CLI arguments (`argparse`), integrates logic from `core_engine.py` and `file_io.py`, and generates final user reports.                        |

---

## 🤝 Contributing

We welcome contributions! If you have suggestions for performance enhancements (especially around the Pigeonhole logic) or new features (like interactive review), please feel free to open an issue or submit a pull request.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

