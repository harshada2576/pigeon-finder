#!/usr/bin/env python3
"""
Verify Pigeon Finder Setup
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    """Check if all required imports work"""
    print("🔍 Checking imports...")
    
    imports = [
        ("customtkinter", "CustomTkinter UI framework"),
        ("PIL.Image", "Pillow for image processing"),
        ("psutil", "System utilities"),
        ("matplotlib.pyplot", "Plotting charts"),
        ("send2trash", "Safe file deletion"),
        ("watchdog", "File system monitoring"),
        ("prettytable", "Table formatting"),
    ]
    
    all_ok = True
    for import_name, description in imports:
        try:
            if import_name == "customtkinter":
                import customtkinter as ctk
                ctk.set_appearance_mode("System")
                print(f"✅ {import_name} - {description}")
            elif import_name == "PIL.Image":
                from PIL import Image
                print(f"✅ {import_name} - {description}")
            elif import_name == "matplotlib.pyplot":
                import matplotlib.pyplot as plt
                print(f"✅ {import_name} - {description}")
            elif import_name == "prettytable":
                from prettytable import PrettyTable
                print(f"✅ {import_name} - {description}")
            else:
                __import__(import_name.split('.')[0])
                print(f"✅ {import_name} - {description}")
        except ImportError as e:
            print(f"❌ {import_name} - {description}")
            print(f"   Error: {e}")
            all_ok = False
    
    return all_ok

def check_project_modules():
    """Check if project modules can be imported"""
    print("\n🔍 Checking project modules...")
    
    modules = [
        "core.file_scanner",
        "core.hashing", 
        "core.duplicate_manager",
        "core.pigeonhole_engine",
        "ui.main_window",
        "ui.results_panel",
        "ui.stats_panel",
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}")
            print(f"   Error: {e}")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("🕊️ Pigeon Finder Setup Verification")
    print("=" * 50)
    
    imports_ok = check_imports()
    modules_ok = check_project_modules()
    
    print("\n" + "=" * 50)
    if imports_ok and modules_ok:
        print("🎉 All checks passed! Pigeon Finder is ready to run!")
        print("\nTo start the application:")
        print("  python main.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)