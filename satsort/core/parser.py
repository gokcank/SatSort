"""
SatSort - Satellite Channel List Editor
Core Parser for SatcoDX (.sdx) Files
"""

from __future__ import annotations
import os
from typing import List, Optional

from .models import Channel, ChannelType, Polarization

# Broadcast System Mappings
BROADCAST_SYSTEM_MAP = {
    "ADR": "ADR (Astra Digital Radio)",
    "BMAC": "B-MAC (B-type Multiplexed Analogue Components)",
    "D2MC": "D2-MAC (Half-Bit-Rate Duo-Binary Multiplexed Analogue Components)",
    "DIC1": "Digicipher 1",
    "DIC2": "Digicipher 2",
    "ISDB": "ISDB (Integrated Services Digital Broadcasting)",
    "MPG1": "MPEG-1 (Motion Pictures Experts Group 1)",
    "MP15": "MPEG-1.5 (Motion Pictures Experts Group 1.5)",
    "MPG2": "MPEG-2 (Motion Pictures Experts Group 2)",
    "MPG4": "MPEG-4 (Motion Pictures Experts Group 4)",
    "MUSE": "MUSE (Multiple Subnyquist Encoding)",
    "NTSC": "NTSC (National Television Standards Committee)",
    "PAL": "PAL (Phase Alternation of Lines)",
    "SECM": "SECAM (Systeme Electronique Couleur Avec Memoire)",
}

# FEC Mappings
FEC_MAP = {
    "0": "-",
    "1": "1/2",
    "2": "2/3",
    "3": "3/4",
    "5": "5/6",
    "7": "7/8",
}


def clean_channel_name(text: str) -> str:
    """Removes special control characters like ENQ (\x05) and NUL (\x00) from channel names."""
    return text.replace("\x05", "").replace("\x00", "").strip()


def safe_substring(text: str, start: int, length: int) -> str:
    """Safely extracts substring with bounds checking, padding with spaces if text is shorter."""
    if len(text) < start + length:
        padded = text.ljust(start + length)
        return padded[start : start + length]
    return text[start : start + length]


def parse_sdx_line(line: str) -> Optional[Channel]:
    """
    Parses a single SatcoDX fixed-width formatted text line into a Channel object.
    
    Fixed-width byte specification:
      0..9    : Header / Index prefix
      10..27  : Satellite Name (18 chars)
      28      : Channel Type (1 char: T, R, D, -)
      29..32  : Broadcast System (4 chars)
      33..41  : Frequency (9 chars)
      42      : Polarization (1 char: 0=Vertical, 1=Horizontal)
      43..50  : Channel Name Part 1 (8 chars)
      51..68  : Additional Transponder data
      69..73  : Symbol Rate (5 chars)
      74      : FEC Code (1 char)
      75..78  : VPID (4 chars)
      79..82  : APID (4 chars)
      83..86  : PCRP (4 chars)
      87..91  : SID (5 chars)
      92..96  : NID (5 chars)
      97..101 : TSID (5 chars)
      102..104: Language (3 chars)
      105     : Separator / Reserved
      106..107: Country Code (2 chars)
      108..110: Language Code (3 chars)
      111..114: Crypto / Encryption Code (4 chars)
      115..126: Channel Name Part 2 (12 chars)
    """
    if not line or len(line.strip()) < 30:
        return None

    # Ensure minimum line length for slicing
    line_padded = line.ljust(127)

    # 1. Satellite Name
    satellite_name = safe_substring(line_padded, 10, 18).strip()

    # 2. Channel Type
    type_code = line_padded[28] if len(line_padded) > 28 else "-"
    channel_type = ChannelType.from_code(type_code)

    # 3. Broadcast System
    bcast_code = safe_substring(line_padded, 29, 4).strip()
    broadcast_system = BROADCAST_SYSTEM_MAP.get(bcast_code, bcast_code)

    # 4. Frequency
    frequency = safe_substring(line_padded, 33, 9).strip()

    # 5. Polarization
    pol_char = line_padded[42] if len(line_padded) > 42 else "0"
    polarization = Polarization.VERTICAL if pol_char == "0" else Polarization.HORIZONTAL

    # 6. Channel Name (Part 1 + Part 2)
    name_part1 = safe_substring(line_padded, 43, 8).strip()
    name_part2 = safe_substring(line_padded, 115, 12).strip()
    channel_name = clean_channel_name(name_part1 + name_part2)

    # 7. Symbol Rate & FEC
    symbol_rate = safe_substring(line_padded, 69, 5).strip()
    fec_char = line_padded[74] if len(line_padded) > 74 else "0"
    fec = FEC_MAP.get(fec_char, fec_char)

    # 8. PIDs
    vpid = safe_substring(line_padded, 75, 4).strip()
    apid = safe_substring(line_padded, 79, 4).strip()
    pcrp = safe_substring(line_padded, 83, 4).strip()
    sid = safe_substring(line_padded, 87, 5).strip()
    nid = safe_substring(line_padded, 92, 5).strip()
    tsid = safe_substring(line_padded, 97, 5).strip()

    # 9. Language & Regional Codes
    language = safe_substring(line_padded, 102, 3).strip()
    country_code = safe_substring(line_padded, 106, 2).strip()
    language_code = safe_substring(line_padded, 108, 3).strip()
    crypto = safe_substring(line_padded, 111, 4).strip()

    return Channel(
        raw_line=line.rstrip("\r\n"),
        satellite_name=satellite_name,
        channel_name=channel_name,
        channel_type=channel_type,
        broadcast_system=broadcast_system,
        frequency=frequency,
        polarization=polarization,
        symbol_rate=symbol_rate,
        fec=fec,
        vpid=vpid,
        apid=apid,
        pcrp=pcrp,
        sid=sid,
        nid=nid,
        tsid=tsid,
        language=language,
        country_code=country_code,
        language_code=language_code,
        crypto=crypto,
    )


def read_sdx_file(file_path: str, encoding: Optional[str] = None) -> List[Channel]:
    """
    Reads a .sdx file and returns a list of Channel objects.
    Tries multiple candidate encodings (cp1254, latin1, utf-8) to ensure non-ASCII characters are parsed properly.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    encodings_to_try = [encoding] if encoding else ["cp1254", "latin1", "utf-8", "iso-8859-9"]
    content: Optional[str] = None

    for enc in encodings_to_try:
        try:
            with open(file_path, "r", encoding=enc, errors="replace") as f:
                content = f.read()
            break
        except Exception:
            continue

    if content is None:
        with open(file_path, "r", encoding="latin1", errors="replace") as f:
            content = f.read()

    # Strip terminating null bytes
    content = content.replace("\x00", "")

    channels: List[Channel] = []
    lines = content.splitlines()

    for line in lines:
        if not line.strip():
            continue
        channel = parse_sdx_line(line)
        if channel:
            channels.append(channel)

    return channels
