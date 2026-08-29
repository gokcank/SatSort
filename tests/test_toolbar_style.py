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

    def test_menu_and_toolbar_categorization(self):
        """Verifies View menu hierarchy and ergonomic Toolbar button layout."""
        window = MainWindow()

        # 1. View Menu existence and content
        self.assertTrue(hasattr(window, "menu_view"))
        self.assertEqual(window.menu_view.title(), "Görünüm")
        self.assertIn(window.act_toggle_sidebar, window.menu_view.actions())

        # 2. Toolbar action composition
        toolbar_actions = window.toolbar.actions()
        self.assertIn(window.act_open, toolbar_actions)
        self.assertIn(window.act_save, toolbar_actions)
        self.assertIn(window.act_move_to, toolbar_actions)
        self.assertIn(window.act_move_up, toolbar_actions)
        self.assertIn(window.act_move_down, toolbar_actions)
        self.assertIn(window.act_del_sel, toolbar_actions)
        self.assertIn(window.act_toggle_check, toolbar_actions)
        self.assertIn(window.act_compare, toolbar_actions)
        self.assertIn(window.act_toggle_sidebar, toolbar_actions)

        # 3. act_close_list removed from toolbar (safe from accidental clicks)
        self.assertNotIn(window.act_close_list, toolbar_actions)

        window.close()


if __name__ == "__main__":
    unittest.main()
