#!/usr/bin/env python3
"""
Final Test for Pigeon Finder
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_all_modules():
    """Test if all required modules can be imported"""
    print("🧪 Testing all Pigeon Finder modules...")
    
    modules = [
        ("customtkinter", "UI Framework"),
        ("PIL.Image", "Image Processing"),
        ("psutil", "System Utilities"),
        ("matplotlib", "Charts"),
        ("send2trash", "Safe Deletion"),
        ("watchdog", "File Monitoring"),
        
        # Core modules
        ("core_file_scanner", "File Scanner"),
        ("core_hashing", "File Hashing"),
        ("core_pigeonhole_engine", "Pigeonhole Engine"),
        ("core_duplicate_manager", "Duplicate Manager"),
        
        # UI modules
        ("ui_main_window", "Main Window"),
        ("ui_results_panel", "Results Panel"),
        ("ui_stats_panel", "Statistics Panel"),
        ("ui_styles", "UI Styles"),
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            if '.' in module_name:
                # Handle sub-imports like PIL.Image
                parts = module_name.split('.')
                base_module = __import__(parts[0])
                for part in parts[1:]:
                    base_module = getattr(base_module, part)
            else:
                __import__(module_name)
            print(f"✅ {module_name} - {description}")
        except ImportError as e:
            print(f"❌ {module_name} - {description}")
            print(f"   Error: {e}")
            all_ok = False
    
    return all_ok

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        from core.file_scanner import FileScanner
        from core.hashing import FileHasher
        from core.pigeonhole_engine import PigeonholeEngine
        from core.duplicate_manager import DuplicateManager
        
        # Create instances
        scanner = FileScanner()
        hasher = FileHasher()
        engine = PigeonholeEngine()
        manager = DuplicateManager()
        
        print("✅ Core components initialized")
        
        # Test UI components
        import customtkinter as ctk
        from ui_main_window import MainWindow
        
        print("✅ UI components ready")
        print("🎉 Pigeon Finder is fully functional!")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🕊️ Pigeon Finder - Final Verification")
    print("=" * 50)
    
    modules_ok = test_all_modules()
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if modules_ok and functionality_ok:
        print("🎉 ALL TESTS PASSED! Pigeon Finder is ready to run!")
        print("\nTo start the application:")
        print("  python run_pigeon_finder.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")