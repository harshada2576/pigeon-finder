#!/usr/bin/env python3
"""
Pigeon Finder - Fixed Entry Point
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point with fixed imports"""
    try:
        # Import after path modification
        from ui_main_window import MainWindow
        import customtkinter as ctk
        
        # Set appearance mode
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Create and run main window
        app = MainWindow()
        app.mainloop()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please make sure all dependencies are installed.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()