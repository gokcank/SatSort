"""
SatSort - Application Configuration & Preferences Manager
Manages persistence in ~/.config/satsort/config.json
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class AppConfig:
    """Manages persistent application settings, recent files, and preferences."""

    _instance: Optional[AppConfig] = None

    def __init__(self) -> None:
        self._config_dir = Path.home() / ".config" / "satsort"
        self._config_file = self._config_dir / "config.json"
        self._data: Dict[str, Any] = {
            "language": "Türkçe",
            "theme": "dark",
            "auto_backup": True,
            "recent_files": [],
        }
        self.load()

    @classmethod
    def get_instance(cls) -> AppConfig:
        if cls._instance is None:
            cls._instance = AppConfig()
        return cls._instance

    def load(self) -> None:
        """Loads configuration from JSON file."""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        self._data.update(saved)
            except Exception:
                pass

    def save(self) -> None:
        """Saves configuration to JSON file."""
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    # --- Recent Files ---
    def get_recent_files(self) -> List[str]:
        """Returns list of recent file paths, filtering out non-existent files."""
        files = self._data.get("recent_files", [])
        if not isinstance(files, list):
            files = []
        # Filter existing files
        valid_files = [f for f in files if isinstance(f, str) and os.path.exists(f)]
        if len(valid_files) != len(files):
            self._data["recent_files"] = valid_files
            self.save()
        return valid_files

    def add_recent_file(self, file_path: str) -> None:
        """Adds a file path to the recent files list (max 10, most recent first)."""
        abs_path = os.path.abspath(file_path)
        recent = self._data.get("recent_files", [])
        if not isinstance(recent, list):
            recent = []

        # Remove duplicate if already present
        if abs_path in recent:
            recent.remove(abs_path)

        recent.insert(0, abs_path)
        self._data["recent_files"] = recent[:10]
        self.save()

    def remove_recent_file(self, file_path: str) -> None:
        """Removes a specific file path from recent files."""
        abs_path = os.path.abspath(file_path)
        recent = self._data.get("recent_files", [])
        if abs_path in recent:
            recent.remove(abs_path)
            self._data["recent_files"] = recent
            self.save()

    def clear_recent_files(self) -> None:
        """Clears all recent files."""
        self._data["recent_files"] = []
        self.save()

    # --- Auto Backup ---
    def get_auto_backup(self) -> bool:
        """Returns whether auto-backup is enabled."""
        return bool(self._data.get("auto_backup", True))

    def set_auto_backup(self, enabled: bool) -> None:
        """Sets whether auto-backup is enabled."""
        self._data["auto_backup"] = bool(enabled)
        self.save()

    # --- Language & Theme ---
    def get_language(self) -> str:
        return str(self._data.get("language", "Türkçe"))

    def set_language(self, lang: str) -> None:
        self._data["language"] = lang
        self.save()

    def get_theme(self) -> str:
        return str(self._data.get("theme", "dark"))

    def set_theme(self, theme: str) -> None:
        self._data["theme"] = theme
        self.save()


config = AppConfig.get_instance()
