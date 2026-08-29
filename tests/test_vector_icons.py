"""
SatSort - Vector SVG Icons Test Suite
Verifies:
  1. All vector SVG icons render valid, non-null QIcon instances.
  2. get_icon adapts color based on active theme (light vs dark).
  3. Action titles across MainWindow are clean of emoji prefixes.
"""

import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from satsort.ui.icons import get_icon, SVG_PATHS, get_default_color
from satsort.ui.theme import apply_theme
from satsort.ui.main_window import MainWindow


class TestVectorIcons(unittest.TestCase):
    """Test suite ensuring vector SVG icons render properly and emojis are removed."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_all_svg_icons_valid(self):
        """Verifies each icon key in SVG_PATHS produces a valid, non-null QIcon."""
        for icon_name in SVG_PATHS.keys():
            icon = get_icon(icon_name, size=24)
            self.assertIsInstance(icon, QIcon)
            self.assertFalse(icon.isNull(), f"Icon '{icon_name}' produced a null QIcon")

    def test_theme_color_adaptation(self):
        """Verifies default icon color changes with active theme."""
        apply_theme(self.app, "light")
        self.assertEqual(get_default_color(), "#0284c7")

        apply_theme(self.app, "dark")
        self.assertEqual(get_default_color(), "#38bdf8")

    def test_main_window_actions_have_no_emoji_prefixes(self):
        """Verifies MainWindow menu actions no longer have emoji prefixes in their text."""
        window = MainWindow()

        emojis = ["📁", "💾", "🕒", "📄", "📝", "📺", "🎯", "📻", "🔒", "🔤", "🔍", "🔗", "🌙", "☀️", "🌐", "📐", "☑️", "ℹ️", "⌨️", "🐛", "⭐", "🔄", "🗑️"]

        actions_to_check = [
            window.act_open,
            window.act_save,
            window.act_export_csv,
            window.act_export_txt,
            window.act_export_m3u,
            window.act_move_to,
            window.act_move_radios_end,
            window.act_remove_scrambled,
            window.act_normalize_names,
            window.act_remove_duplicates,
            window.act_ref_sort,
            window.act_dark_theme,
            window.act_light_theme,
            window.act_toggle_auto_backup,
            window.act_about,
            window.act_shortcuts,
            window.act_report_issue,
            window.act_github_repo,
            window.act_check_updates,
        ]

        for act in actions_to_check:
            text = act.text()
            for emoji in emojis:
                self.assertNotIn(emoji, text, f"Action text '{text}' still contains emoji '{emoji}'")

        window.close()


if __name__ == "__main__":
    unittest.main()
