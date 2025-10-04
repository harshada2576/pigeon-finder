#!/usr/bin/env python3
"""
Pigeon Finder - Duplicate File Finder using Pigeonhole Principle
Main Entry Point - Fixed Import Version
"""

import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import the modules
try:
    from ui.main_window import MainWindow
    import customtkinter as ctk
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all dependencies are installed and the project structure is correct.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pigeon_finder.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Set appearance mode and color theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Create and run main window
        app = MainWindow()
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()