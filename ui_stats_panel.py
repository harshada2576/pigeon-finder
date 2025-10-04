"""
Statistics Panel
"""

import customtkinter as ctk
from ui_styles import Styles

class StatsPanel(ctk.CTkFrame):
    """Panel for displaying statistics"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.stats_data = {}
        self.optimization_stats = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the statistics panel UI"""
        # Create scrollable frame for stats
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial message
        self.initial_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Run a scan to see detailed statistics.",
            font=Styles.FONT_NORMAL,
            text_color=Styles.COLOR_TEXT_SECONDARY
        )
        self.initial_label.pack(pady=50)
        
    def update_stats(self, duplicate_stats, optimization_stats):
        """Update statistics display"""
        self.stats_data = duplicate_stats
        self.optimization_stats = optimization_stats
        
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not duplicate_stats:
            self.show_no_data()
            return
        
        # Create statistics sections
        self.create_summary_section()
        self.create_optimization_section()
        
    def show_no_data(self):
        """Show message when no data is available"""
        label = ctk.CTkLabel(
            self.scrollable_frame,
            text="No duplicate data available. Run a scan to see statistics.",
            font=Styles.FONT_NORMAL,
            text_color=Styles.COLOR_TEXT_SECONDARY
        )
        label.pack(pady=50)
    
    def create_summary_section(self):
        """Create summary statistics section"""
        summary_frame = ctk.CTkFrame(self.scrollable_frame)
        summary_frame.pack(fill="x", padx=5, pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            summary_frame,
            text="Duplicate Summary",
            font=Styles.FONT_SUBHEADING
        )
        title_label.pack(pady=10)
        
        # Stats grid
        stats_grid = ctk.CTkFrame(summary_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=10)
        
        stats = [
            ("Total Duplicate Groups", f"{self.stats_data['total_groups']}"),
            ("Total Duplicate Files", f"{self.stats_data['total_duplicates']}"),
            ("Wasted Space", f"{self.stats_data['wasted_space'] / (1024**3):.2f} GB"),
            ("Potential Space Saved", f"{self.stats_data['wasted_space'] / (1024**3):.2f} GB")
        ]
        
        for label, value in stats:
            row = ctk.CTkFrame(stats_grid, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=label, font=Styles.FONT_NORMAL).pack(side="left")
            ctk.CTkLabel(
                row, 
                text=value, 
                font=Styles.FONT_BOLD,
                text_color=Styles.COLOR_PRIMARY
            ).pack(side="right")
    
    def create_optimization_section(self):
        """Create optimization statistics section"""
        opt_frame = ctk.CTkFrame(self.scrollable_frame)
        opt_frame.pack(fill="x", padx=5, pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            opt_frame,
            text="Pigeonhole Principle Optimization",
            font=Styles.FONT_SUBHEADING
        )
        title_label.pack(pady=10)
        
        # Optimization stats
        stats_grid = ctk.CTkFrame(opt_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=10)
        
        files_processed = self.optimization_stats.get('files_processed', 0)
        comparisons_saved = self.optimization_stats.get('hash_computations_saved', 0)
        comparisons_made = self.optimization_stats.get('comparisons_made', 0)
        
        if files_processed > 0:
            efficiency = (comparisons_saved / (files_processed * (files_processed - 1) // 2)) * 100
        else:
            efficiency = 0
        
        stats = [
            ("Files Processed", f"{files_processed}"),
            ("Hash Computations Saved", f"{comparisons_saved}"),
            ("Efficiency Gain", f"{efficiency:.1f}%"),
            ("Smart Comparisons Made", f"{comparisons_made}")
        ]
        
        for label, value in stats:
            row = ctk.CTkFrame(stats_grid, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=label, font=Styles.FONT_NORMAL).pack(side="left")
            ctk.CTkLabel(
                row, 
                text=value, 
                font=Styles.FONT_BOLD,
                text_color=Styles.COLOR_SUCCESS
            ).pack(side="right")
        
        # Efficiency explanation
        explanation = ctk.CTkLabel(
            opt_frame,
            text="The Pigeonhole Principle groups files by size first, \n"
                 "dramatically reducing the number of hash computations needed.",
            font=Styles.FONT_SMALL,
            text_color=Styles.COLOR_TEXT_SECONDARY,
            justify="center"
        )
        explanation.pack(pady=10)