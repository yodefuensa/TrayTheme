#!/usr/bin/env python3
"""
Config module - Handles persistent configuration using JSON.
Manages user preferences like automatic theme, last theme, etc.
"""
import json
import os
from typing import Any, Dict, Optional
from datetime import datetime


class ConfigManager:
    """Manages application configuration with JSON persistence."""
    
    def __init__(self) -> None:
        """Initialize the config manager."""
        self.config_dir: str = os.path.expanduser("~/.config/tray-theme")
        self.config_file: str = os.path.join(self.config_dir, "config.json")
        self.default_config: Dict[str, Any] = {
            "automatic_theme": True,
            "last_theme": "dia",
            "last_change": None,
        }
        self._ensure_config_exists()
    
    def _ensure_config_exists(self) -> None:
        """Ensure config directory and file exist."""
        os.makedirs(self.config_dir, exist_ok=True)
        
        if not os.path.exists(self.config_file):
            self._write_config(self.default_config)
    
    def _read_config(self) -> Dict[str, Any]:
        """
        Read configuration from JSON file.
        
        Returns:
            dict: Configuration dictionary.
        """
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist (safe read)
                return {**self.default_config, **config}
        except (json.JSONDecodeError, IOError):
            # Return defaults if file is corrupted or missing
            return self.default_config.copy()
    
    def _write_config(self, config: Dict[str, Any]) -> None:
        """
        Write configuration to JSON file.
        
        Args:
            config: Configuration dictionary to save.
        """
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error escribiendo configuración: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key doesn't exist.
            
        Returns:
            Configuration value or default.
        """
        config = self._read_config()
        return config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and save it.
        
        Args:
            key: Configuration key.
            value: Value to set.
        """
        config = self._read_config()
        config[key] = value
        self._write_config(config)
    
    def set_multiple(self, updates: Dict[str, Any]) -> None:
        """
        Set multiple configuration values at once.
        
        Args:
            updates: Dictionary of key-value pairs to update.
        """
        config = self._read_config()
        config.update(updates)
        self._write_config(config)
    
    def get_automatic_theme(self) -> bool:
        """Get automatic theme preference."""
        return self.get("automatic_theme", True)
    
    def set_automatic_theme(self, enabled: bool) -> None:
        """Set automatic theme preference."""
        self.set("automatic_theme", enabled)
    
    def get_last_theme(self) -> str:
        """Get last used theme."""
        return self.get("last_theme", "dia")
    
    def set_last_theme(self, theme: str) -> None:
        """
        Set last used theme and update timestamp.
        
        Args:
            theme: Theme name ('dia' or 'noche').
        """
        self.set_multiple({
            "last_theme": theme,
            "last_change": datetime.now().isoformat()
        })
    
    def get_last_change(self) -> Optional[str]:
        """Get timestamp of last theme change."""
        return self.get("last_change")
