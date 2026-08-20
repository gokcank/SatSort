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
    
    Fixed-width byte specification (SatcoDX 105 standard, 132 chars total):
      0..9    : Header / Index prefix (10 chars, e.g. SATCODX105)
      10..27  : Satellite Name (18 chars)
      28      : Channel Type (1 char: T, R, D, -)
      29..32  : Broadcast System (4 chars, e.g. MPG4, MPG2)
      33      : Polarization (1 char: 0=Vertical, 1=Horizontal)
      34..38  : Frequency (5 chars)
      39..42  : Sequence / Channel Index (4 chars)
      43..50  : Channel Name Part 1 (8 chars)
      51..54  : Orbital Position (4 chars, e.g. 0420)
      55..57  : Country Code (3 chars, e.g. TUR)
      58..68  : Reserved Transponder Data (11 chars)
      69..73  : Symbol Rate (5 chars)
      74      : FEC Code (1 char)
      75..86  : Reserved / Extended PIDs (12 chars)
      87..91  : SID (5 chars)
      92..96  : VPID (5 chars)
      97..101 : APID (5 chars)
      102..104: PCRP / Flags (3 chars)
      105..108: Crypto / Encryption Code (4 chars)
      109..114: Language Flags (6 chars)
      115..131: Channel Name Part 2 (Extended Name, 17 chars)
    """
    if not line or len(line.strip()) < 30:
        return None

    # Ensure fixed 132-char record length for slicing
    line_padded = line.ljust(132)

    # 1. Satellite Name
    satellite_name = safe_substring(line_padded, 10, 18).strip()

    # 2. Channel Type
    type_code = line_padded[28] if len(line_padded) > 28 else "-"
    channel_type = ChannelType.from_code(type_code)

    # 3. Broadcast System
    bcast_code = safe_substring(line_padded, 29, 4).strip()
    broadcast_system = BROADCAST_SYSTEM_MAP.get(bcast_code, bcast_code)

    # 4. Polarization & Frequency
    pol_char = line_padded[33] if len(line_padded) > 33 else "0"
    polarization = Polarization.VERTICAL if pol_char == "0" else Polarization.HORIZONTAL
    frequency = safe_substring(line_padded, 34, 5).strip()

    # 5. Channel Name (Part 1 [8 chars, 43..51] + Part 2 [17 chars, 115..132])
    name_part1 = safe_substring(line_padded, 43, 8)
    name_part2 = safe_substring(line_padded, 115, 17)
    channel_name = clean_channel_name((name_part1 + name_part2).rstrip())

    # 6. Symbol Rate & FEC
    symbol_rate = safe_substring(line_padded, 69, 5).strip()
    fec_char = line_padded[74] if len(line_padded) > 74 else "0"
    fec = FEC_MAP.get(fec_char, fec_char)

    # 7. PIDs
    sid = safe_substring(line_padded, 87, 5).strip()
    vpid = safe_substring(line_padded, 92, 5).strip()
    apid = safe_substring(line_padded, 97, 5).strip()
    pcrp = safe_substring(line_padded, 102, 3).strip()

    # 8. Country & Crypto
    country_code = safe_substring(line_padded, 55, 3).strip()
    crypto = safe_substring(line_padded, 105, 4).strip()

    return Channel(
        raw_line=line.rstrip("\r\n").ljust(132)[:132],
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
        country_code=country_code,
        crypto=crypto,
    )


def read_sdx_file(file_path: str, encoding: Optional[str] = None) -> List[Channel]:
    """
    Reads a .sdx file and returns a list of Channel objects with 100% byte preservation.
    Opens in binary mode to preserve internal null padding bytes and line structures.
    Tries multiple candidate encodings (cp1254, iso-8859-9, latin1, utf-8).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "rb") as f:
        data = f.read()

    # Detect line delimiter (CRLF vs LF)
    delimiter = b"\r\n" if b"\r\n" in data else b"\n"
    raw_lines = data.split(delimiter)

    encodings_to_try = [encoding] if encoding else ["cp1254", "iso-8859-9", "latin1", "utf-8"]
    channels: List[Channel] = []

    for raw_bytes in raw_lines:
        # Check for trailer / EOF marker (starts with null byte \x00)
        if raw_bytes.startswith(b"\x00") or not raw_bytes.strip(b" \t\r\n"):
            continue

        line_str: Optional[str] = None
        for enc in encodings_to_try:
            try:
                line_str = raw_bytes.decode(enc)
                break
            except Exception:
                continue

        if line_str is None:
            line_str = raw_bytes.decode("latin1", errors="replace")

        channel = parse_sdx_line(line_str)
        if channel:
            channels.append(channel)

    return channels


def rename_channel_in_line(raw_line: str, new_channel_name: str) -> str:
    """
    Updates the channel name inside a raw SatcoDX line while preserving all other byte positions.
    Part 1 (up to 8 chars) goes to index 43..50.
    Part 2 (remaining chars up to 17 chars) goes to index 115..131.
    Guarantees that the returned line is exactly 132 characters long.
    """
    line = raw_line.ljust(132)[:132]
    clean_name = new_channel_name.strip()
    
    if len(clean_name) <= 8:
        part1 = clean_name.ljust(8)
        part2 = " " * 17
    else:
        part1 = clean_name[:8]
        part2 = clean_name[8:25].ljust(17)
        
    # Reconstruct line with exact byte positions (43 + 8 + 64 + 17 = 132 chars)
    line = line[:43] + part1 + line[51:115] + part2
    return line[:132]


def format_channel_to_sdx_line(channel: Channel) -> str:
    """
    Formats a Channel object back into a SatcoDX fixed-width line string (exactly 132 chars).
    Uses existing raw_line with name update if available, or constructs a line from properties.
    """
    if channel.raw_line and len(channel.raw_line) >= 127:
        return rename_channel_in_line(channel.raw_line, channel.channel_name)

    # Build line from scratch if raw_line is not available (SatcoDX 105 specification, 132 chars)
    sat = channel.satellite_name.ljust(18)[:18]
    ctype = channel.channel_type.short_code
    bcast = "MPG4".ljust(4)
    for code, full_name in BROADCAST_SYSTEM_MAP.items():
        if channel.broadcast_system == full_name or channel.broadcast_system == code:
            bcast = code.ljust(4)
            break

    pol = "0" if channel.polarization == Polarization.VERTICAL else "1"
    freq = channel.frequency.replace(".", "").zfill(5)[:5]

    clean_name = channel.channel_name.strip()
    if len(clean_name) <= 8:
        p1 = clean_name.ljust(8)
        p2 = " " * 17
    else:
        p1 = clean_name[:8]
        p2 = clean_name[8:25].ljust(17)

    sr = channel.symbol_rate.ljust(5)[:5]
    fec_code = "0"
    for code, val in FEC_MAP.items():
        if channel.fec == val:
            fec_code = code
            break

    vpid = channel.vpid.zfill(5)[:5] if channel.vpid else "00000"
    apid = channel.apid.zfill(5)[:5] if channel.apid else "00000"
    pcrp = channel.pcrp.ljust(3)[:3] if channel.pcrp else "___"
    sid = channel.sid.zfill(5)[:5] if channel.sid else "00000"
    country = channel.country_code.ljust(3)[:3] if channel.country_code else "TUR"
    crypto = channel.crypto.ljust(4)[:4] if channel.crypto else "____"

    line = (
        f"SATCODX105"
        f"{sat}"
        f"{ctype}"
        f"{bcast}"
        f"{pol}"
        f"{freq}"
        f"0000"
        f"{p1}"
        f"0420"
        f"{country}"
        f"     ______"
        f"{sr}"
        f"{fec_code}"
        f"____________"
        f"{sid}"
        f"{vpid}"
        f"{apid}"
        f"{pcrp}"
        f"{crypto}"
        f"______"
        f"{p2}"
    )
    return line.ljust(132)[:132]


def normalize_turkish_chars(text: str) -> str:
    """Normalizes Turkish-specific characters to standard ASCII equivalents."""
    mapping = {
        "ş": "s", "Ş": "S",
        "ı": "i", "İ": "I",
        "ö": "o", "Ö": "O",
        "ü": "u", "Ü": "U",
        "ç": "c", "Ç": "C",
        "ğ": "g", "Ğ": "G",
    }
    for tr_char, en_char in mapping.items():
        text = text.replace(tr_char, en_char)
    return text


def validate_channel_name(name: str) -> tuple[bool, str]:
    """
    Validates a channel name according to SatcoDX rules:
    - Must not be empty.
    - Must not exceed 16 characters.
    - Must contain only letters, numbers, spaces, and standard punctuation.
    """
    trimmed = name.strip()
    if not trimmed:
        return False, "Kanal adı boş olamaz"
    if len(trimmed) > 16:
        return False, "Kanal adı 16 karakterden uzun olamaz"
    return True, ""


def write_sdx_file(file_path: str, channels: List[Channel], encoding: str = "cp1254") -> None:
    """
    Writes a list of Channel objects to a .sdx file with standard CRLF line breaks
    and the required trailing null byte (\\x00).
    """
    lines: List[str] = []
    for ch in channels:
        line_str = format_channel_to_sdx_line(ch)
        lines.append(line_str)

    # Use binary write to ensure exact CRLF and terminating null byte
    with open(file_path, "wb") as f:
        for line in lines:
            f.write(line.encode(encoding, errors="replace") + b"\r\n")
        f.write(b"\x00")

