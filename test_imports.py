# test_imports.py
try:
    import customtkinter as ctk
    from PIL import Image
    import psutil
    import matplotlib
    from send2trash import send2trash
    import watchdog
    from prettytable import PrettyTable
    
    print("✅ All imports successful!")
    print("🚀 Pigeon Finder is ready!")
    
    # Test basic functionality
    ctk.set_appearance_mode("System")
    print("✅ CustomTkinter working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")