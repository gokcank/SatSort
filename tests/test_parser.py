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
        # Create a canonical 127-character sample SatcoDX line
        name_p1 = "TRT 1 HA"  # 8 chars
        name_p2 = "BER         "  # 12 chars
        self.sample_line = (
            "0123456789"  # 0..9 (10 chars)
            "TURKSAT 42E       "  # 10..27 (18 chars)
            "T"  # 28 (1 char)
            "MPG2"  # 29..32 (4 chars)
            "120540000"  # 33..41 (9 chars)
            "0"  # 42 (1 char, 0=Vertical)
            f"{name_p1}"  # 43..50 (8 chars)
            f"{' ' * 18}"  # 51..68 (18 chars)
            "27500"  # 69..73 (5 chars)
            "5"  # 74 (1 char, 5=5/6)
            "0100"  # 75..78 (4 chars VPID)
            "0101"  # 79..82 (4 chars APID)
            "0100"  # 83..86 (4 chars PCRP)
            "00001"  # 87..91 (5 chars SID)
            "00001"  # 92..96 (5 chars NID)
            "00001"  # 97..101 (5 chars TSID)
            "TUR "  # 102..105 (4 chars)
            "TR"  # 106..107 (2 chars)
            "TUR"  # 108..110 (3 chars)
            "----"  # 111..114 (4 chars)
            f"{name_p2}"  # 115..126 (12 chars)
        )

    def test_parse_standard_sdx_line(self):
        ch = parse_sdx_line(self.sample_line)
        self.assertIsNotNone(ch)
        self.assertEqual(ch.satellite_name, "TURKSAT 42E")
        self.assertEqual(ch.channel_name, "TRT 1 HABER")
        self.assertEqual(ch.channel_type, ChannelType.TV)
        self.assertEqual(ch.broadcast_system, "MPEG-2 (Motion Pictures Experts Group 2)")
        self.assertEqual(ch.frequency, "120540000")
        self.assertEqual(ch.polarization, Polarization.VERTICAL)
        self.assertEqual(ch.symbol_rate, "27500")
        self.assertEqual(ch.fec, "5/6")
        self.assertEqual(ch.vpid, "0100")
        self.assertEqual(ch.apid, "0101")
        self.assertEqual(ch.pcrp, "0100")
        self.assertEqual(ch.sid, "00001")
        self.assertEqual(ch.nid, "00001")
        self.assertEqual(ch.tsid, "00001")
        self.assertEqual(ch.language, "TUR")
        self.assertEqual(ch.country_code, "TR")
        self.assertEqual(ch.language_code, "TUR")
        self.assertEqual(ch.crypto, "----")

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
        h_line = self.sample_line[:42] + "1" + self.sample_line[43:]
        ch = parse_sdx_line(h_line)
        self.assertEqual(ch.polarization, Polarization.HORIZONTAL)

        # Vertical (0)
        v_line = self.sample_line[:42] + "0" + self.sample_line[43:]
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

            # Check that file ends with null byte
            with open(tmp_path, "rb") as f:
                content = f.read()
                self.assertTrue(content.endswith(b"\x00"))

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
