#!/usr/bin/env python3
"""
Pigeon Finder - Launcher (canonical entrypoint)

This script provides a stable, backwards-compatible launcher that starts the
primary PyQt5 GUI (`pigeon_finder_gui.PigeonFinderApp`). Historically this
project also included a CustomTkinter-based frontend (`ui_main_window`) which
was removed during cleanup. This script now launches the current canonical GUI.
"""

import sys
import os


def main():
    # Ensure project root is on sys.path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        # Import the PyQt5 application class and run it
        from pigeon_finder_gui import PigeonFinderApp
        from PyQt5.QtWidgets import QApplication

        QApplication.setAttribute(0x00000001)  # Qt.AA_EnableHighDpiScaling
        QApplication.setAttribute(0x00000002)  # Qt.AA_UseHighDpiPixmaps

        app = QApplication(sys.argv)
        window = PigeonFinderApp()
        window.show()
        sys.exit(app.exec_())

    except ImportError as e:
        print(f"Import error: {e}")
        print("This launcher requires PyQt5 and the canonical GUI (pigeon_finder_gui.py).")
        print("Please run `.\ast_setup.ps1` or install dependencies listed in requirements.txt.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()