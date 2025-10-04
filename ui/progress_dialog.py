"""
Progress Dialog for Long-Running Operations
"""

import customtkinter as ctk
from tkinter import ttk
import threading
import time
from .styles import Styles

class ProgressDialog(ctk.CTkToplevel):
    """Modal progress dialog for long-running operations"""
    
    def __init__(self, parent, title="Processing", message="Please wait..."):
        super().__init__(parent)
        
        self.parent = parent
        self.is_cancelled = False
        
        self.setup_dialog(title, message)
        self.center_on_parent()
        
    def setup_dialog(self, title, message):
        """Setup the dialog UI"""
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        self.transient(self.parent)
        self.grab_set()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text=title,
            font=Styles.FONT_HEADING
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Message
        self.message_label = ctk.CTkLabel(
            self,
            text=message,
            font=Styles.FONT_NORMAL,
            wraplength=360
        )
        self.message_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self,
            text="Cancel",
            command=self.cancel,
            fg_color=Styles.COLOR_SECONDARY,
            hover_color=Styles.COLOR_SECONDARY_DARK,
            width=80
        )
        self.cancel_button.grid(row=3, column=0, padx=20, pady=(10, 20))
        
    def center_on_parent(self):
        """Center the dialog on parent window"""
        self.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def update_progress(self, value, message=None):
        """Update progress bar and message"""
        if message:
            self.message_label.configure(text=message)
        
        self.progress_bar.set(value / 100.0)
        self.update()
    
    def cancel(self):
        """Cancel the operation"""
        self.is_cancelled = True
        self.cancel_button.configure(state="disabled", text="Cancelling...")
    
    def run_operation(self, operation, *args, **kwargs):
        """Run an operation with progress tracking"""
        self.operation_result = None
        self.operation_error = None
        
        def wrapper():
            try:
                self.operation_result = operation(*args, **kwargs)
            except Exception as e:
                self.operation_error = e
        
        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()
        
        # Wait for completion
        while thread.is_alive():
            if self.is_cancelled:
                return None
            self.update()
            time.sleep(0.1)
        
        if self.operation_error:
            raise self.operation_error
        
        return self.operation_result