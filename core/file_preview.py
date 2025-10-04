"""
Advanced File Preview and Analysis
"""

import os
import mimetypes
from PIL import Image, ImageTk
import customtkinter as ctk
from pathlib import Path
import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)

class FilePreview:
    """Advanced file preview with multiple format support"""
    
    def __init__(self):
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.supported_text_formats = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv'}
        self.max_file_size_preview = 10 * 1024 * 1024  # 10MB
    
    def can_preview(self, file_path):
        """Check if file can be previewed"""
        if not os.path.exists(file_path):
            return False
        
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size_preview:
            return False
        
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_image_formats.union(self.supported_text_formats)
    
    def get_preview(self, file_path, max_size=(300, 300)):
        """Get file preview as tkinter widget"""
        if not self.can_preview(file_path):
            return self.get_unsupported_preview(file_path)
        
        ext = Path(file_path).suffix.lower()
        
        try:
            if ext in self.supported_image_formats:
                return self.get_image_preview(file_path, max_size)
            elif ext in self.supported_text_formats:
                return self.get_text_preview(file_path)
        except Exception as e:
            logger.error(f"Failed to preview {file_path}: {e}")
            return self.get_error_preview(str(e))
        
        return self.get_unsupported_preview(file_path)
    
    def get_image_preview(self, file_path, max_size):
        """Get image preview"""
        frame = ctk.CTkFrame(width=max_size[0], height=max_size[1])
        
        try:
            image = Image.open(file_path)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            label = ctk.CTkLabel(frame, image=photo, text="")
            label.image = photo  # Keep reference
            label.pack(expand=True, fill="both")
            
        except Exception as e:
            error_label = ctk.CTkLabel(frame, text=f"Image preview error:\n{str(e)}", wraplength=280)
            error_label.pack(expand=True, fill="both")
        
        return frame
    
    def get_text_preview(self, file_path, max_lines=20):
        """Get text file preview"""
        frame = ctk.CTkFrame(width=300, height=200)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Truncate if too long
            lines = content.split('\n')
            if len(lines) > max_lines:
                preview_lines = lines[:max_lines]
                preview_lines.append(f"\n... ({len(lines) - max_lines} more lines)")
                content = '\n'.join(preview_lines)
            
            textbox = ctk.CTkTextbox(frame, wrap="word", font=("Consolas", 10))
            textbox.pack(expand=True, fill="both", padx=5, pady=5)
            textbox.insert("1.0", content)
            textbox.configure(state="disabled")
            
        except Exception as e:
            error_label = ctk.CTkLabel(frame, text=f"Text preview error:\n{str(e)}", wraplength=280)
            error_label.pack(expand=True, fill="both")
        
        return frame
    
    def get_unsupported_preview(self, file_path):
        """Get preview for unsupported files"""
        frame = ctk.CTkFrame(width=300, height=200)
        
        file_info = self.get_file_info(file_path)
        info_text = f"File: {file_info['name']}\nSize: {file_info['size_formatted']}\nType: {file_info['type']}"
        
        label = ctk.CTkLabel(frame, text=info_text, justify="left")
        label.pack(expand=True, fill="both", padx=10, pady=10)
        
        return frame
    
    def get_error_preview(self, error_message):
        """Get error preview"""
        frame = ctk.CTkFrame(width=300, height=200)
        label = ctk.CTkLabel(frame, text=f"Preview Error:\n{error_message}", wraplength=280)
        label.pack(expand=True, fill="both")
        return frame
    
    def get_file_info(self, file_path):
        """Get detailed file information"""
        stat = os.stat(file_path)
        ext = Path(file_path).suffix.lower()
        
        return {
            'name': Path(file_path).name,
            'path': str(Path(file_path).parent),
            'size': stat.st_size,
            'size_formatted': self.format_file_size(stat.st_size),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'type': mimetypes.guess_type(file_path)[0] or 'Unknown',
            'extension': ext
        }
    
    def format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

class PreviewDialog(ctk.CTkToplevel):
    """Dialog for file preview and comparison"""
    
    def __init__(self, parent, file_paths):
        super().__init__(parent)
        
        self.parent = parent
        self.file_paths = file_paths
        self.preview = FilePreview()
        self.current_index = 0
        
        self.setup_dialog()
        self.center_on_parent()
        self.show_preview(0)
    
    def setup_dialog(self):
        """Setup preview dialog"""
        self.title("File Preview - Pigeon Finder")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Navigation toolbar
        self.create_navigation_toolbar()
        
        # Preview area
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)
        
        # File info area
        self.create_info_area()
    
    def create_navigation_toolbar(self):
        """Create navigation toolbar"""
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        nav_frame.pack(side="left")
        
        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀ Previous",
            command=self.previous_file,
            width=100
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="Next ▶",
            command=self.next_file,
            width=100
        )
        self.next_btn.pack(side="left", padx=5)
        
        # File counter
        self.counter_label = ctk.CTkLabel(
            nav_frame,
            text=f"1 / {len(self.file_paths)}",
            font=("Arial", 12, "bold")
        )
        self.counter_label.pack(side="left", padx=20)
        
        # Close button
        close_btn = ctk.CTkButton(
            toolbar,
            text="Close",
            command=self.destroy,
            width=80
        )
        close_btn.pack(side="right")
    
    def create_info_area(self):
        """Create file information area"""
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.info_label = ctk.CTkLabel(
            info_frame,
            text="",
            justify="left",
            font=("Arial", 10)
        )
        self.info_label.pack(fill="x", padx=10, pady=5)
    
    def show_preview(self, index):
        """Show preview for file at index"""
        if index < 0 or index >= len(self.file_paths):
            return
        
        self.current_index = index
        
        # Clear previous preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        # Show new preview
        file_path = self.file_paths[index]
        preview_widget = self.preview.get_preview(file_path)
        preview_widget.grid(row=0, column=0, sticky="nsew")
        
        # Update navigation
        self.update_navigation()
        
        # Update file info
        self.update_file_info(file_path)
    
    def update_navigation(self):
        """Update navigation state"""
        self.counter_label.configure(text=f"{self.current_index + 1} / {len(self.file_paths)}")
        self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_index < len(self.file_paths) - 1 else "disabled")
    
    def update_file_info(self, file_path):
        """Update file information display"""
        file_info = self.preview.get_file_info(file_path)
        
        info_text = (
            f"File: {file_info['name']} | "
            f"Size: {file_info['size_formatted']} | "
            f"Type: {file_info['type']} | "
            f"Modified: {self.format_timestamp(file_info['modified'])}"
        )
        
        self.info_label.configure(text=info_text)
    
    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    def previous_file(self):
        """Show previous file"""
        if self.current_index > 0:
            self.show_preview(self.current_index - 1)
    
    def next_file(self):
        """Show next file"""
        if self.current_index < len(self.file_paths) - 1:
            self.show_preview(self.current_index + 1)
    
    def center_on_parent(self):
        """Center dialog on parent window"""
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