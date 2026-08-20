"""
Unit tests for SatSort Exporter (CSV, TXT, M3U)
"""

import unittest
import tempfile
import os
from satsort.core.models import Channel, ChannelType, Polarization
from satsort.core.exporter import export_to_csv, export_to_txt, export_to_m3u


def _make_dummy(name: str, ch_type: ChannelType = ChannelType.TV, freq: str = "11958", pol: Polarization = Polarization.VERTICAL, sid: str = "101") -> Channel:
    return Channel(
        raw_line="SATCODX105" + " " * 122,
        satellite_name="TURKSAT 42.0E",
        channel_name=name,
        channel_type=ch_type,
        broadcast_system="MPG4",
        frequency=freq,
        polarization=pol,
        symbol_rate="27500",
        fec="3/4",
        vpid="0100",
        apid="0101",
        pcrp="0100",
        sid=sid,
        crypto="FTA",
    )


class TestExporter(unittest.TestCase):

    def setUp(self):
        self.channels = [
            _make_dummy("TRT 1 HD", ChannelType.TV, "11958", Polarization.VERTICAL, "101"),
            _make_dummy("KRAL FM", ChannelType.RADIO, "12015", Polarization.HORIZONTAL, "102"),
        ]

    def test_export_to_csv(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
            temp_path = tf.name

        try:
            export_to_csv(self.channels, temp_path)
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("TRT 1 HD", content)
            self.assertIn("KRAL FM", content)
            self.assertIn("11958", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_export_to_txt(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
            temp_path = tf.name

        try:
            export_to_txt(self.channels, temp_path)
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("TRT 1 HD", content)
            self.assertIn("KRAL FM", content)
            self.assertIn("11958 V", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_export_to_m3u(self):
        with tempfile.NamedTemporaryFile(suffix=".m3u", delete=False) as tf:
            temp_path = tf.name

        try:
            export_to_m3u(self.channels, temp_path)
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertTrue(content.startswith("#EXTM3U"))
            self.assertIn('tvg-name="TRT 1 HD"', content)
            self.assertIn("dvb-s://frequency=11958", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
