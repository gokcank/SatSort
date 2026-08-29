"""
SatSort - Internationalization (i18n) Manager
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional


SUPPORTED_LANGUAGES = ["Türkçe", "English", "Deutsch", "Français", "Español"]

LANGUAGE_CODES = {
    "Türkçe": "TR",
    "English": "EN",
    "Deutsch": "DE",
    "Français": "FR",
    "Español": "ES",
}

LANGUAGE_ENDONYMS = {
    "Türkçe": "Türkçe",
    "English": "English",
    "Deutsch": "Deutsch",
    "Français": "Français",
    "Español": "Español",
}


def detect_system_language() -> str:
    """
    Detects user's operating system language.
    Maps:
      tr_* -> 'Türkçe'
      de_* -> 'Deutsch'
      fr_* -> 'Français'
      es_* -> 'Español'
      fallback / others -> 'English'
    """
    locale_name = ""
    try:
        from PySide6.QtCore import QLocale
        locale_name = QLocale.system().name()
    except Exception:
        pass
    
    if not locale_name:
        locale_name = os.environ.get("LC_ALL") or os.environ.get("LANG") or ""

    locale_name = locale_name.lower()
    if locale_name.startswith("tr"):
        return "Türkçe"
    elif locale_name.startswith("de"):
        return "Deutsch"
    elif locale_name.startswith("fr"):
        return "Français"
    elif locale_name.startswith("es"):
        return "Español"
    else:
        return "English"


class I18nManager:
    """Manages multi-language translations and user locale preferences."""

    def __init__(self, default_language: Optional[str] = None, config_file: Optional[Path] = None) -> None:
        self._translations: Dict[str, Dict[str, str]] = {}
        self._callbacks: List[Callable[[str], None]] = []
        self._config_file = config_file or (Path.home() / ".config" / "satsort" / "config.json")
        self._config_dir = self._config_file.parent
        self._persist_preferences: bool = True
        
        self._load_translations()
        
        # Determine language: preference > detected system locale > default
        initial_lang = default_language or detect_system_language()
        self._current_language: str = initial_lang
        self._load_user_preference()

    def _load_translations(self) -> None:
        """Loads translations from the bundled translations.json file."""
        possible_paths = [
            Path(__file__).parent / "translations.json",
            Path(getattr(sys, "_MEIPASS", "")) / "satsort" / "i18n" / "translations.json",
            Path(getattr(sys, "_MEIPASS", "")) / "translations.json",
            Path("/usr/share/satsort/translations.json"),
        ]
        for p in possible_paths:
            if p and p.is_file():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data:
                            self._translations = data
                            return
                except Exception:
                    pass
        self._translations = {}

    def _load_user_preference(self) -> None:
        """Loads user language preference from ~/.config/satsort/config.json if available."""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    saved_lang = data.get("language")
                    if saved_lang and saved_lang in self._translations:
                        self._current_language = saved_lang
            except Exception:
                pass

    def _save_user_preference(self) -> None:
        """Persists user language preference to ~/.config/satsort/config.json."""
        if not self._persist_preferences:
            return
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            config_data = {}
            if self._config_file.exists():
                try:
                    with open(self._config_file, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                except Exception:
                    config_data = {}
            
            config_data["language"] = self._current_language
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_language_code(self, language: Optional[str] = None) -> str:
        """Returns short code for language (e.g. 'TR', 'EN', 'DE', 'FR', 'ES')."""
        lang = language or self._current_language
        return LANGUAGE_CODES.get(lang, "EN")

    def get_language_endonym(self, language: Optional[str] = None) -> str:
        """Returns native name (endonym) of the language."""
        lang = language or self._current_language
        return LANGUAGE_ENDONYMS.get(lang, lang)

    def get_supported_languages(self) -> List[str]:
        """Returns the list of all available languages."""
        return list(self._translations.keys())

    @property
    def current_language(self) -> str:
        return self._current_language

    def set_language(self, language: str) -> bool:
        """Switches the active language and notifies all registered listener callbacks."""
        if language in self._translations:
            self._current_language = language
            self._save_user_preference()
            self._notify_listeners()
            return True
        return False

    def register_language_changed_callback(self, callback: Callable[[str], None]) -> None:
        """Registers a callback function to be called whenever language changes."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def _notify_listeners(self) -> None:
        for cb in self._callbacks:
            try:
                cb(self._current_language)
            except Exception:
                pass

    def get_text(self, key: str, language: Optional[str] = None, default: Optional[str] = None) -> str:
        """
        Retrieves localized string for key in current or specified language.
        Falls back to English or key itself if missing.
        """
        lang = language or self._current_language
        lang_dict = self._translations.get(lang, {})
        if key in lang_dict:
            return lang_dict[key]
        
        # Fallback to English
        en_dict = self._translations.get("English", {})
        if key in en_dict:
            return en_dict[key]
            
        return default if default is not None else key

    def t(self, key: str, default: Optional[str] = None) -> str:
        """Short alias for get_text."""
        return self.get_text(key, default=default)


# Global singleton instance
i18n = I18nManager()
t = i18n.t
