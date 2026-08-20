"""
SatSort - Reference List Sorter Core Engine
Applies sorting order from a reference .sdx file to a target channel list.
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Optional, Set
from .models import Channel, Polarization


def sort_channels_by_reference(
    target_channels: List[Channel],
    reference_channels: List[Channel],
) -> Tuple[List[Channel], int, int]:
    """
    Reorders `target_channels` according to the sequence in `reference_channels`.

    Matching Hierarchy:
    1. Exact Name match (normalized uppercase) & Frequency match
    2. Exact SID + Frequency + Polarization match
    3. Exact Name match only (normalized uppercase)

    Unmatched target channels are appended to the end of the list in their original relative order.

    Returns:
        (sorted_channels, matched_count, unmatched_count)
    """
    if not target_channels or not reference_channels:
        return list(target_channels), 0, len(target_channels)

    # Normalize name helper
    def norm_name(n: str) -> str:
        return "".join(n.strip().upper().split())

    # Build lookup structures from target channels
    # Pool of available target channels to match
    available_target_indices: Set[int] = set(range(len(target_channels)))
    
    # 1. Map (norm_name, freq) -> list of target indices
    name_freq_map: Dict[Tuple[str, str], List[int]] = {}
    # 2. Map (sid, freq, pol) -> list of target indices
    tech_map: Dict[Tuple[str, str, str], List[int]] = {}
    # 3. Map norm_name -> list of target indices
    name_map: Dict[str, List[int]] = {}

    for idx, ch in enumerate(target_channels):
        n = norm_name(ch.channel_name)
        f = ch.frequency.strip()
        p = ch.polarization.value
        s = ch.sid.strip()

        name_freq_map.setdefault((n, f), []).append(idx)
        if s and s != "0":
            tech_map.setdefault((s, f, p), []).append(idx)
        name_map.setdefault(n, []).append(idx)

    sorted_result: List[Channel] = []
    matched_target_indices: Set[int] = set()

    # Iterate through reference channels in order
    for ref_ch in reference_channels:
        rn = norm_name(ref_ch.channel_name)
        rf = ref_ch.frequency.strip()
        rp = ref_ch.polarization.value
        rs = ref_ch.sid.strip()

        matched_idx: Optional[int] = None

        # Priority 1: Match Name + Frequency
        if (rn, rf) in name_freq_map:
            for idx in name_freq_map[(rn, rf)]:
                if idx in available_target_indices:
                    matched_idx = idx
                    break

        # Priority 2: Match SID + Frequency + Polarization
        if matched_idx is None and rs and rs != "0" and (rs, rf, rp) in tech_map:
            for idx in tech_map[(rs, rf, rp)]:
                if idx in available_target_indices:
                    matched_idx = idx
                    break

        # Priority 3: Match Name only
        if matched_idx is None and rn in name_map:
            for idx in name_map[rn]:
                if idx in available_target_indices:
                    matched_idx = idx
                    break

        if matched_idx is not None:
            available_target_indices.remove(matched_idx)
            matched_target_indices.add(matched_idx)
            sorted_result.append(target_channels[matched_idx])

    # Append remaining unmatched target channels at the end
    unmatched_channels: List[Channel] = []
    for idx, ch in enumerate(target_channels):
        if idx not in matched_target_indices:
            unmatched_channels.append(ch)
            sorted_result.append(ch)

    matched_count = len(matched_target_indices)
    unmatched_count = len(unmatched_channels)

    return sorted_result, matched_count, unmatched_count
