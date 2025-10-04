"""
Configuration Management
"""

import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for application settings"""
    
    def __init__(self, config_file="pigeon_finder_config.json"):
        self.config_file = Path.home() / ".pigeonfinder" / config_file
        self.config_data = self.load_defaults()
        self.load()
    
    def load_defaults(self):
        """Load default configuration"""
        return {
            'ui': {
                'theme': 'system',
                'window_size': [1200, 800],
                'sidebar_width': 250
            },
            'scanning': {
                'default_algorithm': 'md5',
                'chunk_size': 8192,
                'min_file_size': 0,
                'use_quick_scan': True
            },
            'behavior': {
                'confirm_deletions': True,
                'use_recycle_bin': True,
                'auto_save_results': False
            },
            'recent_directories': [],
            'excluded_directories': [
                'System Volume Information',
                '$Recycle.Bin',
                '.git',
                '.svn',
                '__pycache__'
            ]
        }
    
    def load(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self._deep_update(self.config_data, loaded_config)
                logger.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")
    
    def save(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()
    
    def add_recent_directory(self, directory):
        """Add directory to recent directories list"""
        recent = self.get('recent_directories', [])
        
        # Remove if already exists
        if directory in recent:
            recent.remove(directory)
        
        # Add to beginning
        recent.insert(0, directory)
        
        # Keep only last 10
        recent = recent[:10]
        
        self.set('recent_directories', recent)
    
    def _deep_update(self, original, update):
        """Recursively update a nested dictionary"""
        for key, value in update.items():
            if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value