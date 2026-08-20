"""
SatSort - Batch Processing & Cleaning Tools
Pure logic tools for channel list manipulation and cleanup.
"""

from __future__ import annotations
import re
from typing import List, Tuple, Set
from .models import Channel, ChannelType, Polarization
from .parser import rename_channel_in_line


def move_radios_to_end(channels: List[Channel]) -> Tuple[List[Channel], int]:
    """
    Moves all Radio channels (channel_type == ChannelType.RADIO) to the end of the channel list,
    preserving relative ordering of TV channels and Radio channels.
    Returns (new_channel_list, count_of_radios_moved).
    """
    tv_channels = [c for c in channels if c.channel_type != ChannelType.RADIO]
    radio_channels = [c for c in channels if c.channel_type == ChannelType.RADIO]

    if not radio_channels or not tv_channels:
        return list(channels), 0

    reordered = tv_channels + radio_channels
    return reordered, len(radio_channels)


def remove_scrambled_channels(channels: List[Channel]) -> Tuple[List[Channel], int]:
    """
    Filters out scrambled/encrypted channels (is_encrypted == True).
    Returns (filtered_channel_list, count_of_removed_channels).
    """
    fta_channels = []
    removed_count = 0

    for ch in channels:
        if ch.is_encrypted:
            removed_count += 1
        else:
            fta_channels.append(ch)

    return fta_channels, removed_count


def normalize_channel_names(channels: List[Channel]) -> Tuple[List[Channel], int]:
    """
    Normalizes channel names:
    - Collapses multiple whitespace into single space
    - Strips leading and trailing whitespace
    - Converts Turkish lowercase characters to uppercase standard
    Returns (updated_channel_list, count_of_modified_channels).
    """
    tr_upper_map = {
        'i': 'İ',
        'ı': 'I',
        'ğ': 'Ğ',
        'ü': 'Ü',
        'ş': 'Ş',
        'ö': 'Ö',
        'ç': 'Ç',
    }

    def turkish_upper(s: str) -> str:
        res = []
        for char in s:
            if char in tr_upper_map:
                res.append(tr_upper_map[char])
            else:
                res.append(char.upper())
        return "".join(res)

    updated_channels = []
    changed_count = 0

    for ch in channels:
        original_name = ch.channel_name
        cleaned = re.sub(r"\s+", " ", original_name).strip()
        cleaned_upper = turkish_upper(cleaned)

        if cleaned_upper != original_name:
            changed_count += 1
            new_raw = rename_channel_in_line(ch.raw_line, cleaned_upper) if ch.raw_line else ch.raw_line
            new_ch = Channel(
                raw_line=new_raw,
                satellite_name=ch.satellite_name,
                channel_name=cleaned_upper,
                channel_type=ch.channel_type,
                broadcast_system=ch.broadcast_system,
                frequency=ch.frequency,
                polarization=ch.polarization,
                symbol_rate=ch.symbol_rate,
                fec=ch.fec,
                vpid=ch.vpid,
                apid=ch.apid,
                pcrp=ch.pcrp,
                sid=ch.sid,
                nid=ch.nid,
                tsid=ch.tsid,
                language=ch.language,
                country_code=ch.country_code,
                language_code=ch.language_code,
                crypto=ch.crypto,
                is_checked=ch.is_checked,
                is_modified=True,
            )
            updated_channels.append(new_ch)
        else:
            updated_channels.append(ch)

    return updated_channels, changed_count


def remove_duplicate_channels(channels: List[Channel]) -> Tuple[List[Channel], int]:
    """
    Removes duplicate channel entries based on (satellite, frequency, polarization, sid)
    or matching (channel_name, frequency, polarization).
    Preserves the first occurrence and removes subsequent duplicates.
    Returns (deduplicated_list, count_of_removed_duplicates).
    """
    seen_keys: Set[Tuple[str, str, str, str]] = set()
    deduped: List[Channel] = []
    duplicate_count = 0

    for ch in channels:
        sid_str = ch.sid.strip() if ch.sid else ""
        if sid_str and sid_str != "0":
            key = (
                ch.satellite_name.strip().upper(),
                ch.frequency.strip(),
                ch.polarization.value,
                sid_str,
            )
        else:
            key = (
                ch.satellite_name.strip().upper(),
                ch.frequency.strip(),
                ch.polarization.value,
                ch.channel_name.strip().upper(),
            )

        if key in seen_keys:
            duplicate_count += 1
        else:
            seen_keys.add(key)
            deduped.append(ch)

    return deduped, duplicate_count

