"""
SatSort - End-to-End Workflow & Integration Tests
"""

import os
import tempfile
import unittest

from satsort.core.models import Channel, ChannelType, Polarization
from satsort.core.parser import (
    parse_sdx_line,
    read_sdx_file,
    write_sdx_file,
    rename_channel_in_line,
    format_channel_to_sdx_line,
    validate_channel_name,
)
from satsort.i18n import i18n, t


class TestSatSortE2E(unittest.TestCase):
    def setUp(self):
        # Create 5 synthetic channels using format_channel_to_sdx_line for precision
        ch1 = Channel(satellite_name="TURKSAT 42E", channel_name="TRT 1 HD", channel_type=ChannelType.TV, broadcast_system="MPG2", frequency="120540000", polarization=Polarization.VERTICAL, symbol_rate="27500", fec="5/6", vpid="0100", apid="0101", pcrp="0100", sid="00001", nid="00001", tsid="00001", language="TUR", country_code="TR", language_code="TUR", crypto="----")
        ch2 = Channel(satellite_name="TURKSAT 42E", channel_name="TRT SPOR", channel_type=ChannelType.TV, broadcast_system="MPG2", frequency="120540000", polarization=Polarization.VERTICAL, symbol_rate="27500", fec="5/6", vpid="0102", apid="0103", pcrp="0102", sid="00002", nid="00001", tsid="00001", language="TUR", country_code="TR", language_code="TUR", crypto="----")
        ch3 = Channel(satellite_name="TURKSAT 42E", channel_name="ATV", channel_type=ChannelType.TV, broadcast_system="MPG2", frequency="120530000", polarization=Polarization.HORIZONTAL, symbol_rate="27500", fec="5/6", vpid="0200", apid="0201", pcrp="0200", sid="00003", nid="00001", tsid="00001", language="TUR", country_code="TR", language_code="TUR", crypto="----")
        ch4 = Channel(satellite_name="TURKSAT 42E", channel_name="KRAL FM", channel_type=ChannelType.RADIO, broadcast_system="MPG2", frequency="120540000", polarization=Polarization.VERTICAL, symbol_rate="27500", fec="5/6", vpid="0000", apid="0301", pcrp="0300", sid="00004", nid="00001", tsid="00001", language="TUR", country_code="TR", language_code="TUR", crypto="----")
        ch5 = Channel(satellite_name="TURKSAT 42E", channel_name="DATA CH", channel_type=ChannelType.DATA, broadcast_system="MPG2", frequency="120540000", polarization=Polarization.VERTICAL, symbol_rate="27500", fec="5/6", vpid="0000", apid="0000", pcrp="0400", sid="00005", nid="00001", tsid="00001", language="TUR", country_code="TR", language_code="TUR", crypto="----")

        self.channels = [ch1, ch2, ch3, ch4, ch5]
        self.raw_lines = [format_channel_to_sdx_line(ch) for ch in self.channels]
        # Store raw_lines on channels
        for ch, line in zip(self.channels, self.raw_lines):
            ch.raw_line = line

    def test_transponder_grouping(self):
        ch1 = self.channels[0]
        # Ch 1, 2, 4, 5 share the same transponder (12054, Vertical, 27500)
        matching = [ch for ch in self.channels if ch.transponder_key == ch1.transponder_key]
        self.assertEqual(len(matching), 4)
        self.assertEqual(matching[0].channel_name, "TRT 1 HD")
        self.assertEqual(matching[1].channel_name, "TRT SPOR")
        self.assertEqual(matching[2].channel_name, "KRAL FM")
        self.assertEqual(matching[3].channel_name, "DATA CH")

    def test_channel_reordering(self):
        clist = list(self.channels)
        # Move Ch 3 (ATV) from index 2 to index 0
        atv = clist.pop(2)
        clist.insert(0, atv)
        self.assertEqual(clist[0].channel_name, "ATV")
        self.assertEqual(clist[1].channel_name, "TRT 1 HD")

    def test_channel_rename_and_validation(self):
        valid, msg = validate_channel_name("HABERTURK HD")
        self.assertTrue(valid)

        new_line = rename_channel_in_line(self.raw_lines[0], "HABERTURK HD")
        parsed = parse_sdx_line(new_line)
        self.assertEqual(parsed.channel_name, "HABERTURK HD")
        self.assertEqual(parsed.frequency, "12054")
        self.assertEqual(parsed.polarization, Polarization.VERTICAL)

    def test_file_diff_comparison_logic(self):
        # List A: Ch1, Ch2, Ch3
        list_a = self.channels[:3]
        # List B: Ch2, Ch3, Ch4, Ch5 (Ch1 removed, Ch4 and Ch5 added)
        list_b = self.channels[1:]

        keys_a = {(ch.channel_name.lower(), ch.frequency, ch.polarization.value, ch.symbol_rate): ch for ch in list_a}
        keys_b = {(ch.channel_name.lower(), ch.frequency, ch.polarization.value, ch.symbol_rate): ch for ch in list_b}

        removed = [ch for key, ch in keys_a.items() if key not in keys_b]
        added = [ch for key, ch in keys_b.items() if key not in keys_a]

        self.assertEqual(len(removed), 1)
        self.assertEqual(removed[0].channel_name, "TRT 1 HD")

        self.assertEqual(len(added), 2)
        added_names = [ch.channel_name for ch in added]
        self.assertIn("KRAL FM", added_names)
        self.assertIn("DATA CH", added_names)

    def test_full_save_and_reload_cycle(self):
        with tempfile.NamedTemporaryFile(suffix=".sdx", delete=False) as tf:
            tmp_path = tf.name

        try:
            write_sdx_file(tmp_path, self.channels)
            reloaded = read_sdx_file(tmp_path)

            self.assertEqual(len(reloaded), 5)
            self.assertEqual(reloaded[0].channel_name, "TRT 1 HD")
            self.assertEqual(reloaded[0].channel_type, ChannelType.TV)
            self.assertEqual(reloaded[3].channel_name, "KRAL FM")
            self.assertEqual(reloaded[3].channel_type, ChannelType.RADIO)
            self.assertEqual(reloaded[4].channel_type, ChannelType.DATA)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_i18n_language_switching(self):
        i18n.set_language("Türkçe")
        self.assertEqual(t("T100"), "Menü")
        self.assertEqual(t("T101"), "SatcoDx Yükle")

        i18n.set_language("English")
        self.assertEqual(t("T100"), "Menu")
        self.assertEqual(t("T101"), "Load SatcoDx")

        i18n.set_language("Français")
        self.assertEqual(t("T100"), "Menu")
        self.assertEqual(t("T101"), "Charger un fichier SatcoDx")

    def test_batch_workflow_e2e(self):
        from satsort.core.batch_tools import move_radios_to_end, normalize_channel_names, remove_duplicate_channels
        # 1. Radios to end
        reordered, moved = move_radios_to_end(self.channels)
        self.assertEqual(moved, 1)
        self.assertEqual(reordered[-1].channel_name, "KRAL FM")

        # 2. Normalize names
        dirty_channels = [
            Channel(channel_name="   trt   1   hd  ", raw_line="SATCODX105" + " " * 122),
            Channel(channel_name="atv", raw_line="SATCODX105" + " " * 122),
        ]
        cleaned, changed = normalize_channel_names(dirty_channels)
        self.assertEqual(changed, 2)
        self.assertEqual(cleaned[0].channel_name, "TRT 1 HD")
        self.assertEqual(cleaned[1].channel_name, "ATV")

        # 3. Deduplicate
        dups = [self.channels[0], self.channels[1], self.channels[0]]
        deduped, count = remove_duplicate_channels(dups)
        self.assertEqual(count, 1)
        self.assertEqual(len(deduped), 2)

    def test_reference_sorting_workflow_e2e(self):
        from satsort.core.reference_sorter import sort_channels_by_reference
        target = [self.channels[2], self.channels[0], self.channels[1]]  # ATV, TRT1, TRT SPOR
        reference = [self.channels[0], self.channels[1], self.channels[2]]  # TRT1, TRT SPOR, ATV

        sorted_res, matched, unmatched = sort_channels_by_reference(target, reference)
        self.assertEqual(matched, 3)
        self.assertEqual(unmatched, 0)
        self.assertEqual([c.channel_name for c in sorted_res], ["TRT 1 HD", "TRT SPOR", "ATV"])

    def test_export_workflow_e2e(self):
        from satsort.core.exporter import export_to_csv, export_to_txt, export_to_m3u
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            txt_path = os.path.join(tmpdir, "test.txt")
            m3u_path = os.path.join(tmpdir, "test.m3u")

            export_to_csv(self.channels, csv_path)
            export_to_txt(self.channels, txt_path)
            export_to_m3u(self.channels, m3u_path)

            self.assertTrue(os.path.exists(csv_path))
            self.assertTrue(os.path.exists(txt_path))
            self.assertTrue(os.path.exists(m3u_path))


if __name__ == "__main__":
    unittest.main()
