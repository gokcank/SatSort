"""
SatSort - Toolbar Appearance and Compact Layout Test Suite
Verifies:
  1. Toolbar style persistence in AppConfig ('icon_only', 'text_beside_icon', 'text_under_icon').
  2. MainWindow toolbar correctly switches button styles and heights.
  3. Action check states match the active toolbar style.
"""

import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from satsort.core.config import config
from satsort.ui.main_window import MainWindow


class TestToolbarStyle(unittest.TestCase):
    """Test suite ensuring toolbar layout and compact appearance modes function properly."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.orig_style = config.get_toolbar_style()

    def tearDown(self):
        config.set_toolbar_style(self.orig_style)

    def test_config_toolbar_style_persistence(self):
        """Verifies get_toolbar_style and set_toolbar_style persistence."""
        config.set_toolbar_style("icon_only")
        self.assertEqual(config.get_toolbar_style(), "icon_only")

        config.set_toolbar_style("text_beside_icon")
        self.assertEqual(config.get_toolbar_style(), "text_beside_icon")

        config.set_toolbar_style("text_under_icon")
        self.assertEqual(config.get_toolbar_style(), "text_under_icon")

    def test_main_window_toolbar_style_modes(self):
        """Verifies MainWindow toolbar adapts button styles and action states."""
        window = MainWindow()

        # 1. Test Icon Only Mode
        window._set_toolbar_style("icon_only")
        self.assertEqual(window.toolbar.toolButtonStyle(), Qt.ToolButtonIconOnly)
        self.assertEqual(window.toolbar.height(), 36)
        self.assertTrue(window.act_tb_icon_only.isChecked())
        self.assertFalse(window.act_tb_text_under.isChecked())
        self.assertEqual(config.get_toolbar_style(), "icon_only")

        # 2. Test Text Beside Icon Mode
        window._set_toolbar_style("text_beside_icon")
        self.assertEqual(window.toolbar.toolButtonStyle(), Qt.ToolButtonTextBesideIcon)
        self.assertEqual(window.toolbar.height(), 36)
        self.assertTrue(window.act_tb_text_beside.isChecked())
        self.assertFalse(window.act_tb_icon_only.isChecked())
        self.assertEqual(config.get_toolbar_style(), "text_beside_icon")

        # 3. Test Text Under Icon Mode
        window._set_toolbar_style("text_under_icon")
        self.assertEqual(window.toolbar.toolButtonStyle(), Qt.ToolButtonTextUnderIcon)
        self.assertEqual(window.toolbar.height(), 48)
        self.assertTrue(window.act_tb_text_under.isChecked())
        self.assertFalse(window.act_tb_icon_only.isChecked())
        self.assertEqual(config.get_toolbar_style(), "text_under_icon")

        window.close()


if __name__ == "__main__":
    unittest.main()
