"""
SatSort - Comprehensive i18n & Language Selector Test Suite
Verifies:
  1. System locale detection with multiple simulated environments (TR, DE, FR, ES, EN, JA, fallback).
  2. Language codes ('TR', 'EN', 'DE', 'FR', 'ES') and native endonyms.
  3. User preference persistence priority over system locale.
  4. Isolation: ensuring test runs never pollute or overwrite user's real ~/.config/satsort/config.json.
  5. Status bar quick language button and dynamic UI retranslation synchronization.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from satsort.i18n.manager import (
    I18nManager,
    detect_system_language,
    SUPPORTED_LANGUAGES,
    LANGUAGE_CODES,
    LANGUAGE_ENDONYMS,
)
from satsort.ui.main_window import MainWindow


class TestI18nSystem(unittest.TestCase):
    """Dedicated test program for all i18n detection, persistence and UI selector capabilities."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_config_path = Path(self.temp_dir.name) / "config.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_system_locale_detection(self):
        """Tests that detect_system_language properly identifies languages and falls back to English."""
        test_cases = [
            ("tr_TR.UTF-8", "Türkçe"),
            ("tr_CY", "Türkçe"),
            ("de_DE.UTF-8", "Deutsch"),
            ("de_AT", "Deutsch"),
            ("fr_FR.UTF-8", "Français"),
            ("fr_CA", "Français"),
            ("es_ES.UTF-8", "Español"),
            ("es_MX", "Español"),
            ("en_US.UTF-8", "English"),
            ("en_GB", "English"),
            ("ja_JP.UTF-8", "English"),  # Unsupported locale falls back to international standard (English)
            ("ru_RU.UTF-8", "English"),
            ("", "English"),
        ]

        for env_lang, expected_lang in test_cases:
            with patch.dict(os.environ, {"LANG": env_lang, "LC_ALL": env_lang}):
                with patch("PySide6.QtCore.QLocale.system") as mock_qlocale:
                    mock_qlocale.return_value.name.return_value = env_lang
                    detected = detect_system_language()
                    self.assertEqual(
                        detected,
                        expected_lang,
                        f"Failed for locale '{env_lang}': expected '{expected_lang}', got '{detected}'",
                    )

    def test_language_codes_and_endonyms(self):
        """Verifies language codes and native endonym mappings for all supported languages."""
        mgr = I18nManager(config_file=self.temp_config_path)

        for lang in SUPPORTED_LANGUAGES:
            code = mgr.get_language_code(lang)
            endonym = mgr.get_language_endonym(lang)
            self.assertIn(code, ["TR", "EN", "DE", "FR", "ES"])
            self.assertEqual(endonym, lang)

        # Fallback for unknown language
        self.assertEqual(mgr.get_language_code("UnknownLang"), "EN")
        self.assertEqual(mgr.get_language_endonym("UnknownLang"), "UnknownLang")

    def test_user_preference_priority_over_system_locale(self):
        """Verifies that an existing user preference in config.json takes precedence over system locale."""
        # Write user preference as "Español" into temporary config
        with open(self.temp_config_path, "w", encoding="utf-8") as f:
            json.dump({"language": "Español"}, f)

        # Simulate system locale as German ("de_DE")
        with patch.dict(os.environ, {"LANG": "de_DE.UTF-8"}):
            with patch("PySide6.QtCore.QLocale.system") as mock_qlocale:
                mock_qlocale.return_value.name.return_value = "de_DE"
                mgr = I18nManager(config_file=self.temp_config_path)
                self.assertEqual(mgr.current_language, "Español")

    def test_default_detection_when_no_config_exists(self):
        """Verifies that when no config exists, system locale is automatically used."""
        with patch.dict(os.environ, {"LANG": "de_DE.UTF-8"}):
            with patch("PySide6.QtCore.QLocale.system") as mock_qlocale:
                mock_qlocale.return_value.name.return_value = "de_DE"
                mgr = I18nManager(config_file=self.temp_config_path)
                self.assertEqual(mgr.current_language, "Deutsch")

    def test_persistence_isolation_flag(self):
        """Verifies that _persist_preferences=False prevents writing changes to disk."""
        mgr = I18nManager(config_file=self.temp_config_path)
        mgr._persist_preferences = False
        mgr.set_language("Français")

        self.assertEqual(mgr.current_language, "Français")
        self.assertFalse(self.temp_config_path.exists())

    def test_status_bar_quick_language_button_and_sync(self):
        """Verifies that MainWindow status bar has the quick language button and reacts dynamically."""
        # Use isolated manager
        from satsort.i18n import i18n
        orig_persist = i18n._persist_preferences
        orig_lang = i18n.current_language
        i18n._persist_preferences = False

        try:
            window = MainWindow()

            # 1. Check button existence, vector icon, and initial code
            self.assertTrue(hasattr(window, "btn_lang"))
            self.assertFalse(window.btn_lang.icon().isNull())
            current_code = i18n.get_language_code()
            self.assertEqual(window.btn_lang.text(), f"{current_code} ▾")

            # 2. Check status bar menu actions count and endonyms
            actions = window.status_lang_menu.actions()
            self.assertEqual(len(actions), len(SUPPORTED_LANGUAGES))
            for act in actions:
                self.assertTrue(any(lang in act.text() for lang in SUPPORTED_LANGUAGES))

            # 3. Switch language dynamically to English
            i18n.set_language("English")
            self.assertEqual(window.btn_lang.text(), "EN ▾")
            self.assertEqual(window.menu_file.title(), "Menu")

            # 4. Switch language dynamically to Deutsch
            i18n.set_language("Deutsch")
            self.assertEqual(window.btn_lang.text(), "DE ▾")
            self.assertEqual(window.menu_file.title(), "Menu")

            # 5. Switch back to Türkçe
            i18n.set_language("Türkçe")
            self.assertEqual(window.btn_lang.text(), "TR ▾")
            self.assertEqual(window.menu_file.title(), "Menü")

            window.close()
        finally:
            i18n._persist_preferences = orig_persist
            i18n.set_language(orig_lang)


if __name__ == "__main__":
    unittest.main()
