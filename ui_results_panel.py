"""
Results Panel for Displaying Duplicates
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
import os

class Styles:
    """Simple styles class"""
    COLOR_PRIMARY = "#2E86AB"
    COLOR_SECONDARY = "#A23B72"
    COLOR_DANGER = "#F44336"
    COLOR_DANGER_DARK = "#D32F2F"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_TEXT_SECONDARY = "#757575"
    COLOR_BORDER = "#E0E0E0"
    COLOR_GROUP_HEADER = "#E8F4FD"
    
    FONT_FAMILY = "Segoe UI"
    FONT_HEADING = (FONT_FAMILY, 20, "bold")
    FONT_SUBHEADING = (FONT_FAMILY, 16, "bold")
    FONT_BOLD = (FONT_FAMILY, 12, "bold")
    FONT_NORMAL = (FONT_FAMILY, 12)
    FONT_SMALL = (FONT_FAMILY, 11)
    FONT_SMALL_BOLD = (FONT_FAMILY, 11, "bold")
    FONT_BUTTON = (FONT_FAMILY, 12, "bold")

class ResultsPanel(ctk.CTkFrame):
    """Panel for displaying and managing duplicate files"""
    
    def __init__(self, parent, duplicate_manager):
        super().__init__(parent)
        self.manager = duplicate_manager
        self.duplicate_groups = {}
        self.selected_files = set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the results panel UI"""
        # Create top toolbar
        self.create_toolbar()
        
        # Create results display
        self.create_results_display()
        
    def create_toolbar(self):
        """Create toolbar with action buttons"""
        toolbar = ctk.CTkFrame(self, height=50)
        toolbar.pack(fill="x", padx=10, pady=10)
        toolbar.pack_propagate(False)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        actions_frame.pack(side="left", padx=10)
        
        self.delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete Selected",
            command=self.delete_selected,
            state="disabled",
            fg_color=Styles.COLOR_DANGER,
            hover_color=Styles.COLOR_DANGER_DARK,
            width=120
        )
        self.delete_btn.pack(side="left", padx=5)
        
        self.move_btn = ctk.CTkButton(
            actions_frame,
            text="Move Selected",
            command=self.move_selected,
            state="disabled",
            width=120
        )
        self.move_btn.pack(side="left", padx=5)
        
        self.select_all_btn = ctk.CTkButton(
            actions_frame,
            text="Select All Duplicates",
            command=self.select_all_duplicates,
            width=140
        )
        self.select_all_btn.pack(side="left", padx=5)
        
        # Selection info
        self.selection_label = ctk.CTkLabel(
            toolbar, 
            text="No files selected",
            font=Styles.FONT_SMALL
        )
        self.selection_label.pack(side="right", padx=10)
        
    def create_results_display(self):
        """Create the main results display area"""
        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial message
        self.initial_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="No duplicates found. Run a scan to see results.",
            font=Styles.FONT_NORMAL,
            text_color=Styles.COLOR_TEXT_SECONDARY
        )
        self.initial_label.pack(pady=50)
        
    def update_results(self, duplicate_groups):
        """Update the results display with new duplicate groups"""
        self.duplicate_groups = duplicate_groups
        self.selected_files.clear()
        
        # Clear existing results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not duplicate_groups:
            self.initial_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No duplicates found!",
                font=Styles.FONT_NORMAL,
                text_color=Styles.COLOR_SUCCESS
            )
            self.initial_label.pack(pady=50)
            return
        
        # Create results for each duplicate group
        for i, (original, duplicates) in enumerate(duplicate_groups.items()):
            self.create_duplicate_group(i, original, duplicates)
        
        self.update_selection_display()
        
    def create_duplicate_group(self, group_id, original, duplicates):
        """Create UI for a single duplicate group"""
        group_frame = ctk.CTkFrame(self.scrollable_frame, border_width=1, border_color=Styles.COLOR_BORDER)
        group_frame.pack(fill="x", padx=5, pady=5)
        
        # Group header
        header_frame = ctk.CTkFrame(group_frame, fg_color=Styles.COLOR_GROUP_HEADER)
        header_frame.pack(fill="x", padx=1, pady=1)
        
        # Original file info
        orig_info = self.get_file_info(original)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            header_content,
            text=f"Original: {orig_info['name']}",
            font=Styles.FONT_BOLD,
            anchor="w"
        ).pack(fill="x")
        
        info_text = f"Size: {orig_info['size_mb']:.2f} MB | Path: {orig_info['path']}"
        ctk.CTkLabel(
            header_content,
            text=info_text,
            font=Styles.FONT_SMALL,
            text_color=Styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        ).pack(fill="x")
        
        # Duplicates list
        for duplicate in duplicates:
            self.create_duplicate_item(group_frame, duplicate)
    
    def create_duplicate_item(self, parent, file_path):
        """Create UI for a single duplicate file"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", padx=10, pady=2)
        
        file_info = self.get_file_info(file_path)
        
        # Checkbox for selection
        var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            item_frame,
            text="",
            variable=var,
            command=lambda p=file_path, v=var: self.toggle_file_selection(p, v),
            width=20
        )
        checkbox.pack(side="left", padx=(0, 10))
        
        # File info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            info_frame,
            text=file_info['name'],
            font=Styles.FONT_NORMAL,
            anchor="w"
        ).pack(fill="x")
        
        path_text = f"Path: {file_info['path']} | Size: {file_info['size_mb']:.2f} MB"
        ctk.CTkLabel(
            info_frame,
            text=path_text,
            font=Styles.FONT_SMALL,
            text_color=Styles.COLOR_TEXT_SECONDARY,
            anchor="w"
        ).pack(fill="x")
        
        # Store reference to checkbox
        item_frame.checkbox_var = var
        item_frame.file_path = file_path
    
    def get_file_info(self, file_path):
        """Get formatted file information"""
        stat = os.stat(file_path)
        return {
            'name': Path(file_path).name,
            'path': str(Path(file_path).parent),
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'modified': stat.st_mtime
        }
    
    def toggle_file_selection(self, file_path, var):
        """Toggle file selection"""
        if var.get():
            self.selected_files.add(file_path)
        else:
            self.selected_files.discard(file_path)
        
        self.update_selection_display()
    
    def select_all_duplicates(self):
        """Select all duplicate files"""
        self.selected_files.clear()
        for original, duplicates in self.duplicate_groups.items():
            self.selected_files.update(duplicates)
        
        # Update all checkboxes
        for widget in self.scrollable_frame.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if hasattr(child, 'checkbox_var') and hasattr(child, 'file_path'):
                        if child.file_path in self.selected_files:
                            child.checkbox_var.set(True)
                        else:
                            child.checkbox_var.set(False)
        
        self.update_selection_display()
    
    def update_selection_display(self):
        """Update selection information and button states"""
        selected_count = len(self.selected_files)
        total_size = sum(os.path.getsize(f) for f in self.selected_files)
        
        self.selection_label.configure(
            text=f"Selected: {selected_count} files ({total_size / (1024*1024):.1f} MB)"
        )
        
        # Enable/disable buttons based on selection
        state = "normal" if selected_count > 0 else "disabled"
        self.delete_btn.configure(state=state)
        self.move_btn.configure(state=state)
    
    def delete_selected(self):
        """Delete selected files"""
        if not self.selected_files:
            return
            
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {len(self.selected_files)} files?\n\n"
            "This action cannot be undone!",
            icon="warning"
        )
        
        if result:
            # Ask for deletion method
            use_trash = messagebox.askyesno(
                "Deletion Method",
                "Send files to Recycle Bin?\n\n"
                "Yes: Send to Recycle Bin (safer)\n"
                "No: Permanent deletion"
            )
            
            success_count, failed_files = self.manager.delete_files(
                list(self.selected_files),
                use_trash=use_trash
            )
            
            if failed_files:
                messagebox.showerror(
                    "Deletion Errors",
                    f"Failed to delete {len(failed_files)} files. "
                    "They may be in use or you may not have permission."
                )
            
            # Refresh display
            self.update_results(self.manager.duplicate_groups)
            messagebox.showinfo(
                "Deletion Complete",
                f"Successfully deleted {success_count} files."
            )
    
    def move_selected(self):
        """Move selected files to another directory"""
        if not self.selected_files:
            return
            
        destination = filedialog.askdirectory(title="Select destination directory")
        if not destination:
            return
            
        success_count, failed_files = self.manager.move_files(
            list(self.selected_files),
            destination
        )
        
        if failed_files:
            messagebox.showerror(
                "Move Errors",
                f"Failed to move {len(failed_files)} files."
            )
        
        # Refresh display
        self.update_results(self.manager.duplicate_groups)
        messagebox.showinfo(
            "Move Complete",
            f"Successfully moved {success_count} files to {destination}."
        )