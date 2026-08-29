"""
SatSort - Theme Contrast and Component Styling Test Suite
Verifies that:
  1. Light theme and dark theme apply high-contrast colors to channel badges, sidebar labels, and search bar.
  2. Switching themes dynamically updates component styling and table items without errors.
"""

import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor

from satsort.core.models import Channel, ChannelType, Polarization
from satsort.ui.theme import apply_theme, get_current_theme
from satsort.ui.main_window import MainWindow
from satsort.ui.channel_table import ChannelTableWidget
from satsort.ui.sidebar import SidebarWidget
from satsort.ui.search_bar import SearchBarWidget


class TestThemeContrast(unittest.TestCase):
    """Test suite ensuring light and dark themes maintain sharp contrast across all widgets."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_channel_table_badges_contrast(self):
        """Verifies channel type badge colors adapt to light and dark theme contrasts."""
        ch_tv = Channel(channel_name="TRT 1", channel_type=ChannelType.TV, raw_line="SATCODX105" + " " * 122)
        ch_radio = Channel(channel_name="KRAL FM", channel_type=ChannelType.RADIO, raw_line="SATCODX105" + " " * 122)
        ch_data = Channel(channel_name="OTA Update", channel_type=ChannelType.DATA, raw_line="SATCODX105" + " " * 122)

        table = ChannelTableWidget()

        # 1. Test Light Theme
        apply_theme(self.app, "light")
        table.set_channels([ch_tv, ch_radio, ch_data])

        tv_color_light = table.item(0, ChannelTableWidget.COL_TYPE).foreground().color().name()
        radio_color_light = table.item(1, ChannelTableWidget.COL_TYPE).foreground().color().name()
        data_color_light = table.item(2, ChannelTableWidget.COL_TYPE).foreground().color().name()

        # Deep high-contrast colors on white background
        self.assertEqual(tv_color_light, "#0284c7")
        self.assertEqual(radio_color_light, "#7c3aed")
        self.assertEqual(data_color_light, "#047857")

        # 2. Test Dark Theme
        apply_theme(self.app, "dark")
        table.set_channels([ch_tv, ch_radio, ch_data])

        tv_color_dark = table.item(0, ChannelTableWidget.COL_TYPE).foreground().color().name()
        radio_color_dark = table.item(1, ChannelTableWidget.COL_TYPE).foreground().color().name()
        data_color_dark = table.item(2, ChannelTableWidget.COL_TYPE).foreground().color().name()

        # Pastel colors on dark background
        self.assertEqual(tv_color_dark, "#60a5fa")
        self.assertEqual(radio_color_dark, "#a78bfa")
        self.assertEqual(data_color_dark, "#34d399")

    def test_sidebar_and_search_object_names(self):
        """Verifies that sidebar and search widgets have proper object names for CSS theme inheritance."""
        sidebar = SidebarWidget()
        search = SearchBarWidget()

        self.assertEqual(sidebar.transponder_widget.list_widget.objectName(), "transponder_list")
        self.assertEqual(search._search_input.objectName(), "search_input")
        self.assertEqual(search._btn_prev.objectName(), "search_nav_btn")
        self.assertEqual(search._btn_next.objectName(), "search_nav_btn")
        self.assertEqual(search._btn_mark_all.objectName(), "search_mark_btn")
        self.assertEqual(search._count_label.objectName(), "search_count_badge")

    def test_theme_switch_in_main_window(self):
        """Verifies theme switching in MainWindow runs without errors and updates state."""
        window = MainWindow()

        # Switch to light
        window._set_theme("light")
        self.assertEqual(get_current_theme(), "light")
        self.assertTrue(window.act_light_theme.isChecked())
        self.assertFalse(window.act_dark_theme.isChecked())

        # Switch back to dark
        window._set_theme("dark")
        self.assertEqual(get_current_theme(), "dark")
        self.assertTrue(window.act_dark_theme.isChecked())
        self.assertFalse(window.act_light_theme.isChecked())

        window.close()


if __name__ == "__main__":
    unittest.main()
