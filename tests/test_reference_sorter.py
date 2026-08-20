"""
Unit tests for SatSort Reference List Sorter
"""

import unittest
from satsort.core.models import Channel, ChannelType, Polarization
from satsort.core.reference_sorter import sort_channels_by_reference


def _make_dummy(name: str, freq: str = "12000", pol: Polarization = Polarization.HORIZONTAL, sid: str = "1") -> Channel:
    return Channel(
        raw_line="SATCODX105" + " " * 122,
        satellite_name="TURKSAT 42.0E",
        channel_name=name,
        channel_type=ChannelType.TV,
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


class TestReferenceSorter(unittest.TestCase):

    def test_reference_sorting_basic(self):
        # Target channels (new unsorted list from TV scan)
        target = [
            _make_dummy("SHOW TV", freq="12209", sid="3"),
            _make_dummy("TRT 1 HD", freq="11958", sid="1"),
            _make_dummy("ATV HD", freq="12053", sid="2"),
            _make_dummy("NEW LOCAL CH", freq="12500", sid="99"),  # Not in reference
        ]

        # Reference channels (user's preferred order: TRT 1, ATV, SHOW)
        reference = [
            _make_dummy("TRT 1 HD", freq="11958", sid="1"),
            _make_dummy("ATV HD", freq="12053", sid="2"),
            _make_dummy("SHOW TV", freq="12209", sid="3"),
        ]

        sorted_res, matched, unmatched = sort_channels_by_reference(target, reference)

        self.assertEqual(matched, 3)
        self.assertEqual(unmatched, 1)

        names = [c.channel_name for c in sorted_res]
        # Should be ordered per reference, and new local channel at end
        self.assertEqual(names, ["TRT 1 HD", "ATV HD", "SHOW TV", "NEW LOCAL CH"])

    def test_reference_sorting_name_match_whitespace_insensitive(self):
        target = [
            _make_dummy("  TRT 1 HD  ", freq="11958"),
            _make_dummy("ATV HD", freq="12053"),
        ]
        reference = [
            _make_dummy("ATV HD", freq="12053"),
            _make_dummy("TRT 1 HD", freq="11958"),
        ]

        sorted_res, matched, unmatched = sort_channels_by_reference(target, reference)
        self.assertEqual(matched, 2)
        self.assertEqual(unmatched, 0)
        self.assertEqual([c.channel_name for c in sorted_res], ["ATV HD", "  TRT 1 HD  "])


if __name__ == "__main__":
    unittest.main()
