"""
Custom Styles and Theme Configuration
"""

class Styles:
    """Centralized style configuration for the application"""
    
    # Color scheme
    COLOR_PRIMARY = "#2E86AB"
    COLOR_PRIMARY_DARK = "#1C5D7A"
    COLOR_SECONDARY = "#A23B72"
    COLOR_SECONDARY_DARK = "#7A2C56"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_WARNING = "#FF9800"
    COLOR_DANGER = "#F44336"
    COLOR_DANGER_DARK = "#D32F2F"
    
    # Neutral colors
    COLOR_BACKGROUND = "#F5F5F5"
    COLOR_SURFACE = "#FFFFFF"
    COLOR_TEXT_PRIMARY = "#212121"
    COLOR_TEXT_SECONDARY = "#757575"
    COLOR_BORDER = "#E0E0E0"
    COLOR_GROUP_HEADER = "#E8F4FD"
    
    # Font configurations
    FONT_FAMILY = "Segoe UI"
    
    FONT_HEADING = (FONT_FAMILY, 20, "bold")
    FONT_SUBHEADING = (FONT_FAMILY, 16, "bold")
    FONT_BOLD = (FONT_FAMILY, 12, "bold")
    FONT_NORMAL = (FONT_FAMILY, 12)
    FONT_SMALL = (FONT_FAMILY, 11)
    FONT_SMALL_BOLD = (FONT_FAMILY, 11, "bold")
    FONT_BUTTON = (FONT_FAMILY, 12, "bold")
    
    @classmethod
    def configure_ctk_theme(cls):
        """Configure customtkinter theme"""
        import customtkinter as ctk
        
        # This would be called during application startup
        # to apply custom theme settings
        pass
    
    @classmethod
    def get_color_palette(cls):
        """Get the complete color palette"""
        return {
            'primary': cls.COLOR_PRIMARY,
            'primary_dark': cls.COLOR_PRIMARY_DARK,
            'secondary': cls.COLOR_SECONDARY,
            'secondary_dark': cls.COLOR_SECONDARY_DARK,
            'success': cls.COLOR_SUCCESS,
            'warning': cls.COLOR_WARNING,
            'danger': cls.COLOR_DANGER,
            'danger_dark': cls.COLOR_DANGER_DARK,
            'background': cls.COLOR_BACKGROUND,
            'surface': cls.COLOR_SURFACE,
            'text_primary': cls.COLOR_TEXT_PRIMARY,
            'text_secondary': cls.COLOR_TEXT_SECONDARY,
            'border': cls.COLOR_BORDER
        }