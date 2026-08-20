"""
SatSort - Unit Tests for Core Parser and Serializer
"""

import os
import tempfile
import unittest

from satsort.core.models import Channel, ChannelType, Polarization
from satsort.core.parser import (
    clean_channel_name,
    format_channel_to_sdx_line,
    normalize_turkish_chars,
    parse_sdx_line,
    read_sdx_file,
    rename_channel_in_line,
    validate_channel_name,
    write_sdx_file,
)


class TestSatcoDxParser(unittest.TestCase):
    def setUp(self):
        # Create a canonical 132-character sample SatcoDX 105 line
        name_p1 = "TRT 1 HA"  # 8 chars (43..50)
        name_p2 = "BER              "  # 17 chars (115..131)
        self.sample_line = (
            "SATCODX105"  # 0..9 (10 chars)
            "TURKSAT 42E       "  # 10..27 (18 chars)
            "T"  # 28 (1 char)
            "MPG2"  # 29..32 (4 chars)
            "0"  # 33 (1 char, 0=Vertical)
            "12054"  # 34..38 (5 chars frequency)
            "0000"  # 39..42 (4 chars sequence)
            f"{name_p1}"  # 43..50 (8 chars)
            "0420"  # 51..54 (4 chars)
            "TUR"  # 55..57 (3 chars)
            "     ______"  # 58..68 (11 chars)
            "27500"  # 69..73 (5 chars symbol rate)
            "5"  # 74 (1 char, 5=5/6)
            "____________"  # 75..86 (12 chars)
            "00001"  # 87..91 (5 chars SID)
            "01000"  # 92..96 (5 chars VPID)
            "01010"  # 97..101 (5 chars APID)
            "___"  # 102..104 (3 chars PCRP)
            "----"  # 105..108 (4 chars crypto)
            "______"  # 109..114 (6 chars language)
            f"{name_p2}"  # 115..131 (17 chars name part 2)
        )

    def test_parse_standard_sdx_line(self):
        ch = parse_sdx_line(self.sample_line)
        self.assertIsNotNone(ch)
        self.assertEqual(ch.satellite_name, "TURKSAT 42E")
        self.assertEqual(ch.channel_name, "TRT 1 HABER")
        self.assertEqual(ch.channel_type, ChannelType.TV)
        self.assertEqual(ch.broadcast_system, "MPEG-2 (Motion Pictures Experts Group 2)")
        self.assertEqual(ch.frequency, "12054")
        self.assertEqual(ch.polarization, Polarization.VERTICAL)
        self.assertEqual(ch.symbol_rate, "27500")
        self.assertEqual(ch.fec, "5/6")
        self.assertEqual(ch.vpid, "01000")
        self.assertEqual(ch.apid, "01010")
        self.assertEqual(ch.sid, "00001")

    def test_channel_type_detection(self):
        # Radio channel
        radio_line = self.sample_line[:28] + "R" + self.sample_line[29:]
        ch = parse_sdx_line(radio_line)
        self.assertEqual(ch.channel_type, ChannelType.RADIO)

        # Data channel
        data_line = self.sample_line[:28] + "D" + self.sample_line[29:]
        ch = parse_sdx_line(data_line)
        self.assertEqual(ch.channel_type, ChannelType.DATA)

        # Package Transponder
        pkg_line = self.sample_line[:28] + "-" + self.sample_line[29:]
        ch = parse_sdx_line(pkg_line)
        self.assertEqual(ch.channel_type, ChannelType.PACKAGE)

    def test_polarization_detection(self):
        # Horizontal (1)
        h_line = self.sample_line[:33] + "1" + self.sample_line[34:]
        ch = parse_sdx_line(h_line)
        self.assertEqual(ch.polarization, Polarization.HORIZONTAL)

        # Vertical (0)
        v_line = self.sample_line[:33] + "0" + self.sample_line[34:]
        ch = parse_sdx_line(v_line)
        self.assertEqual(ch.polarization, Polarization.VERTICAL)

    def test_clean_control_characters(self):
        dirty_name = f"\x05TRT\x00 1\x05"
        self.assertEqual(clean_channel_name(dirty_name), "TRT 1")

    def test_rename_short_and_long_names(self):
        # Short name (<= 8 chars)
        short_line = rename_channel_in_line(self.sample_line, "ATV")
        ch_short = parse_sdx_line(short_line)
        self.assertEqual(ch_short.channel_name, "ATV")

        # Long name (> 8 chars, up to 16 chars)
        long_line = rename_channel_in_line(self.sample_line, "SHOW TV HD")
        ch_long = parse_sdx_line(long_line)
        self.assertEqual(ch_long.channel_name, "SHOW TV HD")

    def test_validate_channel_name(self):
        valid, _ = validate_channel_name("TRT SPOR")
        self.assertTrue(valid)

        empty, msg = validate_channel_name("   ")
        self.assertFalse(empty)
        self.assertIn("boş", msg.lower())

        too_long, msg = validate_channel_name("THIS NAME IS LONGER THAN 16 CHARS")
        self.assertFalse(too_long)
        self.assertIn("16", msg)

    def test_normalize_turkish_chars(self):
        turkish_text = "Şampiyon Işıklar Özgür Ülkü Çeşme Güneş"
        normalized = normalize_turkish_chars(turkish_text)
        self.assertEqual(normalized, "Sampiyon Isiklar Ozgur Ulku Cesme Gunes")

    def test_read_and_write_sdx_roundtrip(self):
        ch1 = parse_sdx_line(self.sample_line)
        ch2 = parse_sdx_line(rename_channel_in_line(self.sample_line, "KANAL D HD"))
        ch3 = parse_sdx_line(rename_channel_in_line(self.sample_line, "KRAL FM"))

        with tempfile.NamedTemporaryFile(suffix=".sdx", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            write_sdx_file(tmp_path, [ch1, ch2, ch3])

            # Check that file ends with 133-byte trailer block starting with null byte
            with open(tmp_path, "rb") as f:
                content = f.read()
                self.assertTrue(content.endswith(b"\x00" + b" " * 132))

            # Read back and verify all channels
            loaded_channels = read_sdx_file(tmp_path)
            self.assertEqual(len(loaded_channels), 3)
            self.assertEqual(loaded_channels[0].channel_name, "TRT 1 HABER")
            self.assertEqual(loaded_channels[1].channel_name, "KANAL D HD")
            self.assertEqual(loaded_channels[2].channel_name, "KRAL FM")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_empty_and_corrupt_lines(self):
        self.assertIsNone(parse_sdx_line(""))
        self.assertIsNone(parse_sdx_line("   "))
        self.assertIsNone(parse_sdx_line("SHORT"))


if __name__ == "__main__":
    unittest.main()
