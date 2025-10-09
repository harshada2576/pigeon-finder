"""
Statistics Panel with Visualizations
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('TkAgg')
from .styles import Styles

class StatsPanel(ctk.CTkFrame):
    """Panel for displaying detailed statistics and visualizations"""
    
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
            text="Run a scan to see detailed statistics and visualizations.",
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
        self.create_file_type_chart()
        self.create_space_usage_chart()
        
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
        
        for i, (label, value) in enumerate(stats):
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
    
    def create_file_type_chart(self):
        """Create file type distribution chart"""
        if not self.stats_data.get('file_types'):
            return
            
        chart_frame = ctk.CTkFrame(self.scrollable_frame)
        chart_frame.pack(fill="x", padx=5, pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="Duplicate File Types",
            font=Styles.FONT_SUBHEADING
        )
        title_label.pack(pady=10)
        
        # Create matplotlib figure
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        file_types = self.stats_data['file_types']
        
        # Prepare data for chart
        labels = []
        counts = []
        
        # Select top 8 file types by count without using sorted()
        items = list(file_types.items())
        top_items = []
        while items and len(top_items) < 8:
            # find max item
            max_idx = 0
            for idx in range(1, len(items)):
                if items[idx][1] > items[max_idx][1]:
                    max_idx = idx
            top_items.append(items.pop(max_idx))

        for ext, count in top_items:
            labels.append(ext if ext else 'No Extension')
            counts.append(count)
        
        # Create pie chart
        colors = plt.cm.Set3(range(len(labels)))
        wedges, texts, autotexts = ax.pie(
            counts, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        
        # Style the chart
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Distribution of Duplicate File Types', pad=20)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)
    
    def create_space_usage_chart(self):
        """Create space usage visualization"""
        if not self.stats_data.get('wasted_space', 0) > 0:
            return
            
        chart_frame = ctk.CTkFrame(self.scrollable_frame)
        chart_frame.pack(fill="x", padx=5, pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="Space Usage Analysis",
            font=Styles.FONT_SUBHEADING
        )
        title_label.pack(pady=10)
        
        # Create matplotlib figure
        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        wasted_gb = self.stats_data['wasted_space'] / (1024**3)
        categories = ['Wasted Space', 'Usable Space']
        sizes = [wasted_gb, 100 - wasted_gb]  # Simplified visualization
        
        # Create bar chart
        bars = ax.bar(categories, sizes, color=[Styles.COLOR_DANGER, Styles.COLOR_SUCCESS])
        
        # Add value labels on bars
        for bar, value in zip(bars, sizes):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Percentage (%)')
        ax.set_ylim(0, 110)
        ax.set_title('Storage Space Utilization')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)