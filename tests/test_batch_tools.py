"""
Unit tests for SatSort Batch Tools (Radios to end, Remove Scrambled, Normalize Names, Remove Duplicates)
"""

import unittest
from satsort.core.models import Channel, ChannelType, Polarization
from satsort.core.batch_tools import (
    move_radios_to_end,
    remove_scrambled_channels,
    normalize_channel_names,
    remove_duplicate_channels,
)


def _make_dummy_channel(
    name: str,
    ch_type: ChannelType = ChannelType.TV,
    freq: str = "12000",
    pol: Polarization = Polarization.HORIZONTAL,
    sid: str = "1",
    crypto: str = "FTA",
) -> Channel:
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
        nid="0001",
        tsid="0001",
        crypto=crypto,
        is_checked=False,
    )


class TestBatchTools(unittest.TestCase):

    def test_move_radios_to_end(self):
        channels = [
            _make_dummy_channel("TRT 1", ch_type=ChannelType.TV),
            _make_dummy_channel("KRAL FM", ch_type=ChannelType.RADIO),
            _make_dummy_channel("ATV HD", ch_type=ChannelType.TV),
            _make_dummy_channel("SUPER FM", ch_type=ChannelType.RADIO),
            _make_dummy_channel("SHOW TV", ch_type=ChannelType.TV),
        ]

        reordered, radio_count = move_radios_to_end(channels)
        self.assertEqual(radio_count, 2)
        names = [c.channel_name for c in reordered]
        self.assertEqual(names, ["TRT 1", "ATV HD", "SHOW TV", "KRAL FM", "SUPER FM"])

    def test_remove_scrambled_channels(self):
        channels = [
            _make_dummy_channel("TRT 1", crypto="FTA"),
            _make_dummy_channel("BEIN SPORTS 1", crypto="NDS"),
            _make_dummy_channel("ATV HD", crypto="FTA"),
            _make_dummy_channel("DIGITURK 4K", crypto="IRDE"),
        ]

        filtered, removed_count = remove_scrambled_channels(channels)
        self.assertEqual(removed_count, 2)
        names = [c.channel_name for c in filtered]
        self.assertEqual(names, ["TRT 1", "ATV HD"])

    def test_normalize_channel_names(self):
        channels = [
            _make_dummy_channel("  trt   1   hd  "),
            _make_dummy_channel("haber türk"),
            _make_dummy_channel("CNN TURK"),
        ]

        normalized, changed_count = normalize_channel_names(channels)
        self.assertEqual(changed_count, 2)
        names = [c.channel_name for c in normalized]
        self.assertEqual(names, ["TRT 1 HD", "HABER TÜRK", "CNN TURK"])

    def test_remove_duplicate_channels(self):
        channels = [
            _make_dummy_channel("TRT 1", freq="11958", pol=Polarization.VERTICAL, sid="101"),
            _make_dummy_channel("ATV", freq="12053", pol=Polarization.HORIZONTAL, sid="102"),
            _make_dummy_channel("TRT 1", freq="11958", pol=Polarization.VERTICAL, sid="101"),  # duplicate
            _make_dummy_channel("SHOW TV", freq="12209", pol=Polarization.HORIZONTAL, sid="103"),
            _make_dummy_channel("ATV", freq="12053", pol=Polarization.HORIZONTAL, sid="102"),  # duplicate
        ]

        deduped, dup_count = remove_duplicate_channels(channels)
        self.assertEqual(dup_count, 2)
        self.assertEqual(len(deduped), 3)
        names = [c.channel_name for c in deduped]
        self.assertEqual(names, ["TRT 1", "ATV", "SHOW TV"])


if __name__ == "__main__":
    unittest.main()
