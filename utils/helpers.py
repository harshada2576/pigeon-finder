"""
Utility Helper Functions
"""

import os
import time
from pathlib import Path
from send2trash import send2trash
import logging

logger = logging.getLogger(__name__)

def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def format_time(seconds):
    """Format time in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def safe_delete(file_path, use_trash=True):
    """Safely delete a file with error handling"""
    try:
        if use_trash:
            send2trash(file_path)
        else:
            os.remove(file_path)
        return True
    except Exception as e:
        logger.error(f"Failed to delete {file_path}: {e}")
        return False

def get_file_icon_path(extension):
    """Get appropriate icon for file type (placeholder)"""
    # This would typically map file extensions to icon paths
    # For now, return a generic icon path
    icon_map = {
        '.jpg': 'image.png',
        '.png': 'image.png',
        '.pdf': 'pdf.png',
        '.doc': 'document.png',
        '.docx': 'document.png',
        '.txt': 'text.png',
        '.mp4': 'video.png',
        '.mp3': 'audio.png'
    }
    return icon_map.get(extension.lower(), 'file.png')

def is_hidden_file(file_path):
    """Check if file is hidden"""
    name = Path(file_path).name
    return name.startswith('.') or has_hidden_attribute(file_path)

def has_hidden_attribute(file_path):
    """Check if file has hidden attribute (Windows)"""
    try:
        import ctypes
        if os.name == 'nt':  # Windows
            attrs = ctypes.windll.kernel32.GetFileAttributesW(file_path)
            return attrs != -1 and attrs & 2  # FILE_ATTRIBUTE_HIDDEN
    except:
        pass
    return False

def calculate_directory_size(directory):
    """Calculate total size of directory"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except OSError:
                continue
    return total_size

def get_file_type_category(extension):
    """Categorize file by type"""
    extension = extension.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
    document_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz'}
    
    if extension in image_extensions:
        return 'Image'
    elif extension in video_extensions:
        return 'Video'
    elif extension in audio_extensions:
        return 'Audio'
    elif extension in document_extensions:
        return 'Document'
    elif extension in archive_extensions:
        return 'Archive'
    else:
        return 'Other'