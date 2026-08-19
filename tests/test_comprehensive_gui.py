"""
SatSort - Comprehensive End-to-End GUI & Core Deep-Test Suite
Simulates all user interactions, dialogs, drag & drop, search, and edge cases using QTest.
"""

import os
import tempfile
import unittest

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from satsort.core.models import Channel, ChannelType, Polarization
from satsort.core.parser import (
    parse_sdx_line,
    read_sdx_file,
    write_sdx_file,
    rename_channel_in_line,
    format_channel_to_sdx_line,
    validate_channel_name,
    normalize_turkish_chars,
)
from satsort.i18n import i18n, t
from satsort.ui import (
    MainWindow,
    apply_theme,
    toggle_theme,
    get_current_theme,
)
from satsort.ui.dialogs import (
    MovePositionDialog,
    RenameChannelDialog,
    ImportChannelsDialog,
    CompareFilesDialog,
    LanguageSelectionDialog,
    AboutDialog,
)


class TestComprehensiveSatSort(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        # Apply dark theme by default
        apply_theme(self.app, "dark")
        i18n.set_language("Türkçe")

        # Create window
        self.win = MainWindow()

        # Build realistic sample channel dataset across 3 transponders
        self.ch_trt1 = Channel(
            satellite_name="TURKSAT 42E",
            channel_name="TRT 1 HD",
            channel_type=ChannelType.TV,
            broadcast_system="MPG2",
            frequency="120540000",
            polarization=Polarization.VERTICAL,
            symbol_rate="27500",
            fec="5/6",
            vpid="0100",
            apid="0101",
            pcrp="0100",
            sid="00001",
            nid="00001",
            tsid="00001",
            language="TUR",
            country_code="TR",
            language_code="TUR",
            crypto="----",
        )
        self.ch_trthaber = Channel(
            satellite_name="TURKSAT 42E",
            channel_name="TRT HABER HD",
            channel_type=ChannelType.TV,
            broadcast_system="MPG2",
            frequency="120540000",
            polarization=Polarization.VERTICAL,
            symbol_rate="27500",
            fec="5/6",
            vpid="0102",
            apid="0103",
            pcrp="0102",
            sid="00002",
            nid="00001",
            tsid="00001",
            language="TUR",
            country_code="TR",
            language_code="TUR",
            crypto="----",
        )
        self.ch_atv = Channel(
            satellite_name="TURKSAT 42E",
            channel_name="ATV HD",
            channel_type=ChannelType.TV,
            broadcast_system="MPG2",
            frequency="120530000",
            polarization=Polarization.HORIZONTAL,
            symbol_rate="27500",
            fec="5/6",
            vpid="0200",
            apid="0201",
            pcrp="0200",
            sid="00003",
            nid="00001",
            tsid="00001",
            language="TUR",
            country_code="TR",
            language_code="TUR",
            crypto="----",
        )
        self.ch_kral = Channel(
            satellite_name="TURKSAT 42E",
            channel_name="KRAL FM",
            channel_type=ChannelType.RADIO,
            broadcast_system="MPG2",
            frequency="120540000",
            polarization=Polarization.VERTICAL,
            symbol_rate="27500",
            fec="5/6",
            vpid="0000",
            apid="0301",
            pcrp="0300",
            sid="00004",
            nid="00001",
            tsid="00001",
            language="TUR",
            country_code="TR",
            language_code="TUR",
            crypto="----",
        )
        self.ch_data = Channel(
            satellite_name="TURKSAT 42E",
            channel_name="DATA TEST",
            channel_type=ChannelType.DATA,
            broadcast_system="MPG2",
            frequency="120540000",
            polarization=Polarization.VERTICAL,
            symbol_rate="27500",
            fec="5/6",
            vpid="0000",
            apid="0000",
            pcrp="0400",
            sid="00005",
            nid="00001",
            tsid="00001",
            language="TUR",
            country_code="TR",
            language_code="TUR",
            crypto="----",
        )

        self.initial_channels = [
            self.ch_trt1,
            self.ch_trthaber,
            self.ch_atv,
            self.ch_kral,
            self.ch_data,
        ]
        self.win.channel_table.set_channels(self.initial_channels)

    def tearDown(self):
        self.win._set_dirty(False)
        self.win.close()

    # -------------------------------------------------------------
    # 1. CORE ENGINE & SDX FILE TESTS
    # -------------------------------------------------------------
    def test_sdx_fixed_width_exact_length(self):
        for ch in self.initial_channels:
            line = format_channel_to_sdx_line(ch)
            self.assertEqual(len(line), 127, f"Line length must be 127, got {len(line)}")
            parsed = parse_sdx_line(line)
            self.assertEqual(parsed.channel_name, ch.channel_name)
            self.assertEqual(parsed.channel_type, ch.channel_type)
            self.assertEqual(parsed.frequency, ch.frequency)

    def test_sdx_file_read_write_with_null_terminator(self):
        with tempfile.NamedTemporaryFile(suffix=".sdx", delete=False) as tf:
            tmp_path = tf.name

        try:
            write_sdx_file(tmp_path, self.initial_channels)

            # Check file ends with \0
            with open(tmp_path, "rb") as f:
                content = f.read()
                self.assertTrue(content.endswith(b"\x00"), "SDX file must terminate with null byte")

            loaded = read_sdx_file(tmp_path)
            self.assertEqual(len(loaded), 5)
            self.assertEqual([c.channel_name for c in loaded], ["TRT 1 HD", "TRT HABER HD", "ATV HD", "KRAL FM", "DATA TEST"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_long_channel_name_split_and_recombine(self):
        # 16-character channel name
        long_name = "HABERTURK HD 123"
        valid, msg = validate_channel_name(long_name)
        self.assertTrue(valid)

        ch = Channel(channel_name=long_name, frequency="120540000", polarization=Polarization.VERTICAL, symbol_rate="27500")
        line = format_channel_to_sdx_line(ch)
        self.assertEqual(len(line), 127)

        # Part 1 (chars 43..50, 8 chars)
        self.assertEqual(line[43:51], "HABERTUR")
        # Part 2 (chars 115..126, 12 chars)
        self.assertEqual(line[115:127], "K HD 123    ")

        parsed = parse_sdx_line(line)
        self.assertEqual(parsed.channel_name, long_name)

    # -------------------------------------------------------------
    # 2. GUI TABLE & SELECTION INTERACTIONS
    # -------------------------------------------------------------
    def test_table_row_count_and_selection(self):
        table = self.win.channel_table
        self.assertEqual(table.rowCount(), 5)

        table.selectRow(0)
        sel_ch = table.get_selected_channel()
        self.assertIsNotNone(sel_ch)
        self.assertEqual(sel_ch.channel_name, "TRT 1 HD")

    def test_close_file_clears_state(self):
        self.win._set_dirty(False)
        self.win.close_file()
        self.assertEqual(self.win.channel_table.rowCount(), 0)
        self.assertEqual(self.win.lbl_file_info.text(), "Hazır")
        self.assertIsNone(self.win._current_file_path)
        self.assertFalse(self.win._is_dirty)

    def test_unsaved_changes_dirty_tracking_and_guard(self):
        # Initial state on loaded file
        self.win._set_dirty(False)
        self.assertFalse(self.win._is_dirty)
        self.assertNotIn("*", self.win.windowTitle())

        # Modify channel name -> marks dirty
        self.win.channel_table.update_channel_name_at(0, "NEW TRT")
        self.assertTrue(self.win._is_dirty)
        self.assertIn("*", self.win.windowTitle())

        # Clean state when reset
        self.win._set_dirty(False)
        self.assertFalse(self.win._is_dirty)
        self.assertNotIn("*", self.win.windowTitle())

    def test_channel_move_up_down(self):
        table = self.win.channel_table
        table.selectRow(2)  # Select ATV HD
        self.assertEqual(table.get_selected_channel().channel_name, "ATV HD")

        # Move Up -> Should become index 1
        table.move_selected_up()
        channels = table.get_channels()
        self.assertEqual(channels[1].channel_name, "ATV HD")
        self.assertEqual(channels[2].channel_name, "TRT HABER HD")

        # Move Down -> Should return to index 2
        table.move_selected_down()
        channels = table.get_channels()
        self.assertEqual(channels[2].channel_name, "ATV HD")

    def test_channel_swap(self):
        table = self.win.channel_table
        # Swap index 0 (TRT 1 HD) and index 2 (ATV HD)
        table.swap_channels(0, 2)
        channels = table.get_channels()
        self.assertEqual(channels[0].channel_name, "ATV HD")
        self.assertEqual(channels[2].channel_name, "TRT 1 HD")

    def test_move_multiple_channels(self):
        table = self.win.channel_table
        # Initial: ["TRT 1 HD", "TRT HABER HD", "ATV HD", "KRAL FM", "DATA TEST"]
        # Move rows [0, 1] (TRT 1 HD, TRT HABER HD) to target index 4 (after ATV HD and KRAL FM)
        table.move_multiple_channels([0, 1], 4)
        names = [c.channel_name for c in table.get_channels()]
        self.assertEqual(names, ["ATV HD", "KRAL FM", "TRT 1 HD", "TRT HABER HD", "DATA TEST"])
        # Check order numbers in column 0
        self.assertEqual(table.item(0, table.COL_NO).text(), "1")
        self.assertEqual(table.item(2, table.COL_NO).text(), "3")

    def test_move_checked_channels(self):
        table = self.win.channel_table
        channels = table.get_channels()
        # Check ATV HD (idx 2) and KRAL FM (idx 3)
        channels[2].is_checked = True
        channels[3].is_checked = True
        table.set_channels(channels)

        # Move checked channels to target index 0
        table.move_checked_channels(0)
        new_channels = table.get_channels()
        self.assertEqual(new_channels[0].channel_name, "ATV HD")
        self.assertEqual(new_channels[1].channel_name, "KRAL FM")
        self.assertEqual(new_channels[2].channel_name, "TRT 1 HD")

    def test_delete_selected_and_checked(self):
        table = self.win.channel_table
        # Select row 4 (DATA TEST) and delete
        table.selectRow(4)
        table.delete_selected()
        self.assertEqual(table.rowCount(), 4)
        self.assertNotIn("DATA TEST", [c.channel_name for c in table.get_channels()])

        # Check KRAL FM and delete checked
        channels = table.get_channels()
        channels[2].is_checked = True  # ATV HD
        table.set_channels(channels)
        table.delete_checked()
        self.assertEqual(table.rowCount(), 3)
        self.assertNotIn("ATV HD", [c.channel_name for c in table.get_channels()])

    def test_smart_delete_prefers_checked_over_selected(self):
        table = self.win.channel_table
        # Table has 5 channels. Select row 0 (TRT 1 HD), but check row 2 (ATV HD)
        table.selectRow(0)
        channels = table.get_channels()
        channels[2].is_checked = True
        table.set_channels(channels)
        table.selectRow(0)

        # smart_delete should delete the checked channel (ATV HD), not the selected one (TRT 1 HD)
        deleted = table.smart_delete()
        self.assertEqual(deleted, 1)
        remaining = [c.channel_name for c in table.get_channels()]
        self.assertIn("TRT 1 HD", remaining)
        self.assertNotIn("ATV HD", remaining)

        # Now with no checked channels, smart_delete should delete selected row
        table.selectRow(0)
        deleted = table.smart_delete()
        self.assertEqual(deleted, 1)
        self.assertNotIn("TRT 1 HD", [c.channel_name for c in table.get_channels()])

    def test_toggle_all_checked_action(self):
        table = self.win.channel_table
        # Initially none checked
        self.assertFalse(table.is_all_checked())
        self.assertEqual(self.win.act_toggle_check.text(), "☑️ Tümünü İşaretle")

        # Toggle -> checks all 5 channels
        res = table.toggle_all_checked()
        self.assertTrue(res)
        self.assertTrue(table.is_all_checked())
        self.assertEqual(len(table.get_checked_channels()), table.rowCount())
        self.assertEqual(self.win.act_toggle_check.text(), "⚪ " + t("T108"))

        # Toggle again -> unchecks all
        res = table.toggle_all_checked()
        self.assertFalse(res)
        self.assertFalse(table.is_all_checked())
        self.assertEqual(len(table.get_checked_channels()), 0)
        self.assertEqual(self.win.act_toggle_check.text(), "☑️ Tümünü İşaretle")

    # -------------------------------------------------------------
    # 3. SEARCH BAR & LIVE FILTERING
    # -------------------------------------------------------------
    def test_search_and_confirmation(self):
        search_bar = self.win.search_bar
        table = self.win.channel_table

        # Search for "TRT"
        search_bar._search_input.setText("TRT")
        self.assertIn("1 / 2", search_bar._count_label.text())
        self.assertEqual(len(table.get_search_matches()), 2)
        self.assertEqual(table.get_current_match_index(), 0)

        # Confirm search (simulate Enter) -> marks 2 channels as checked
        self.win._on_search_confirmed("TRT")
        checked = table.get_checked_channels()
        self.assertEqual(len(checked), 2)
        self.assertEqual([c.channel_name for c in checked], ["TRT 1 HD", "TRT HABER HD"])

        # Clear search
        search_bar.clear()
        self.assertEqual(search_bar.get_text(), "")
        self.assertEqual(len(table.get_search_matches()), 0)

    def test_search_navigation_prev_next(self):
        search_bar = self.win.search_bar
        table = self.win.channel_table

        # Search for "HD" (matches TRT 1 HD (0), TRT HABER HD (1), ATV HD (2))
        search_bar._search_input.setText("HD")
        self.assertEqual(len(table.get_search_matches()), 3)
        self.assertEqual(table.get_current_match_index(), 0)
        self.assertEqual(table.get_selected_channel().channel_name, "TRT 1 HD")

        # Next match -> TRT HABER HD (idx 1)
        self.win._on_search_next()
        self.assertEqual(table.get_current_match_index(), 1)
        self.assertEqual(table.get_selected_channel().channel_name, "TRT HABER HD")
        self.assertIn("2 / 3", search_bar._count_label.text())

        # Next match -> ATV HD (idx 2)
        self.win._on_search_next()
        self.assertEqual(table.get_current_match_index(), 2)
        self.assertEqual(table.get_selected_channel().channel_name, "ATV HD")
        self.assertIn("3 / 3", search_bar._count_label.text())

        # Next match wraps around -> TRT 1 HD (idx 0)
        self.win._on_search_next()
        self.assertEqual(table.get_current_match_index(), 0)
        self.assertEqual(table.get_selected_channel().channel_name, "TRT 1 HD")

        # Prev match wraps backwards -> ATV HD (idx 2)
        self.win._on_search_prev()
        self.assertEqual(table.get_current_match_index(), 2)
        self.assertEqual(table.get_selected_channel().channel_name, "ATV HD")

    def test_drag_and_drop_after_search(self):
        search_bar = self.win.search_bar
        table = self.win.channel_table

        # Search for TRT and confirm
        search_bar._search_input.setText("TRT")
        self.win._on_search_confirmed("TRT")

        # Select row 0 (TRT 1 HD) and move it down to index 2
        table.selectRow(0)
        table.move_channel(0, 2)

        channels = table.get_channels()
        self.assertEqual(channels[2].channel_name, "TRT 1 HD")
        self.assertEqual(channels[0].channel_name, "TRT HABER HD")

    def test_search_preserves_existing_user_checked_channels(self):
        search_bar = self.win.search_bar
        table = self.win.channel_table

        # 1. User manually checks KRAL FM (idx 3)
        channels = table.get_channels()
        channels[3].is_checked = True
        table.set_channels(channels)
        self.assertEqual(len(table.get_checked_channels()), 1)
        self.assertEqual(table.get_checked_channels()[0].channel_name, "KRAL FM")

        # 2. Live typing "TRT" does NOT overwrite or clear KRAL FM
        search_bar._search_input.setText("TRT")
        self.assertEqual(len(table.get_checked_channels()), 1)
        self.assertEqual(table.get_checked_channels()[0].channel_name, "KRAL FM")

        # 3. Batch mark "TRT" -> adds TRT 1 HD and TRT HABER HD, KRAL FM is still checked!
        self.win._on_search_confirmed("TRT")
        checked_names = [c.channel_name for c in table.get_checked_channels()]
        self.assertEqual(len(checked_names), 3)
        self.assertIn("KRAL FM", checked_names)
        self.assertIn("TRT 1 HD", checked_names)
        self.assertIn("TRT HABER HD", checked_names)

        # 4. Clearing search bar does NOT uncheck any channels
        search_bar.clear()
        checked_names_after_clear = [c.channel_name for c in table.get_checked_channels()]
        self.assertEqual(len(checked_names_after_clear), 3)
        self.assertIn("KRAL FM", checked_names_after_clear)

    # -------------------------------------------------------------
    # 4. SIDEBAR & TRANSPONDER SYNCHRONIZATION
    # -------------------------------------------------------------
    def test_sidebar_transponder_sync(self):
        table = self.win.channel_table
        sidebar = self.win.sidebar

        # Select TRT 1 HD (Transponder: 12054 V 27500)
        table.selectRow(0)
        params = sidebar.params_widget
        self.assertEqual(params._value_labels["channel_name"].text(), "TRT 1 HD")
        self.assertEqual(params._value_labels["frequency"].text(), "120540000")
        self.assertEqual(params._value_labels["polarization"].text(), "Vertical")

        # Check transponder package list contains 4 channels (TRT 1, TRT HABER, KRAL FM, DATA TEST)
        tp_list = sidebar.transponder_widget.list_widget
        self.assertEqual(tp_list.count(), 4)

        # Simulate clicking on KRAL FM in transponder list
        kral_item = tp_list.item(2)
        sidebar.transponder_widget._on_item_clicked(kral_item)

        # Main table selection should automatically jump to row 3 (KRAL FM)
        self.assertEqual(table.currentRow(), 3)
        self.assertEqual(table.get_selected_channel().channel_name, "KRAL FM")

    def test_toggle_sidebar_visibility(self):
        self.win.toggle_sidebar(False)
        self.assertTrue(self.win.sidebar.isHidden())
        self.win.toggle_sidebar(True)
        self.assertFalse(self.win.sidebar.isHidden())

    # -------------------------------------------------------------
    # 5. DIALOGS WORKFLOW
    # -------------------------------------------------------------
    def test_move_position_dialog(self):
        dlg = MovePositionDialog("Taşı", 5, initial_pos=3)
        self.assertEqual(dlg.get_target_index(), 2)
        dlg.spin_box.setValue(1)
        self.assertEqual(dlg.get_target_index(), 0)

    def test_rename_channel_dialog_validation(self):
        dlg = RenameChannelDialog("TRT 1 HD")
        self.assertEqual(dlg.get_channel_name(), "TRT 1 HD")

        # Test valid name change
        dlg.txt_name.setText("TRT 1 4K")
        self.assertEqual(dlg.get_channel_name(), "TRT 1 4K")

    def test_compare_files_logic_in_dialog(self):
        current = [self.ch_trt1, self.ch_trthaber, self.ch_atv]
        dlg = CompareFilesDialog(current)

        # New file has ATV HD, KRAL FM, DATA TEST (TRT 1 & TRT HABER removed, KRAL FM & DATA TEST added)
        comparison = [self.ch_atv, self.ch_kral, self.ch_data]
        dlg._compute_differences(comparison)

        self.assertEqual(len(dlg._removed_channels), 2)
        self.assertEqual([c.channel_name for c in dlg._removed_channels], ["TRT 1 HD", "TRT HABER HD"])

        self.assertEqual(len(dlg._inserted_channels), 2)
        self.assertEqual([c.channel_name for c in dlg._inserted_channels], ["KRAL FM", "DATA TEST"])

    def test_language_selection_dialog(self):
        dlg = LanguageSelectionDialog()
        dlg.combo.setCurrentText("English")
        dlg._on_accept()
        self.assertEqual(i18n.current_language, "English")
        self.assertEqual(t("T100"), "Menu")

        # Switch back to Turkish
        i18n.set_language("Türkçe")
        self.assertEqual(t("T100"), "Menü")

    def test_about_dialog(self):
        dlg = AboutDialog()
        self.assertIsNotNone(dlg)

    # -------------------------------------------------------------
    # 6. THEMES & COLOR HIGHLIGHTING
    # -------------------------------------------------------------
    def test_theme_toggle_and_checked_row_colors(self):
        table = self.win.channel_table
        channels = table.get_channels()
        channels[0].is_checked = True
        table.set_channels(channels)

        # Dark theme checked row background
        self.win._set_theme("dark")
        self.assertEqual(get_current_theme(), "dark")
        bg_dark = table.item(0, 0).background().color().name()
        self.assertEqual(bg_dark, "#2e2608")

        # Light theme checked row background
        self.win._set_theme("light")
        self.assertEqual(get_current_theme(), "light")
        bg_light = table.item(0, 0).background().color().name()
        self.assertEqual(bg_light, "#fef3c7")

        # Switch back to dark
        self.win._set_theme("dark")


if __name__ == "__main__":
    unittest.main()
