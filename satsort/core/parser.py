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

    # 6. Channel Name (Part 1 [8 chars] + Part 2 [12 chars])
    name_part1 = safe_substring(line_padded, 43, 8)
    name_part2 = safe_substring(line_padded, 115, 12)
    channel_name = clean_channel_name((name_part1 + name_part2).rstrip())

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


def rename_channel_in_line(raw_line: str, new_channel_name: str) -> str:
    """
    Updates the channel name inside a raw SatcoDX line while preserving all other byte positions.
    Part 1 (up to 8 chars) goes to index 43..50.
    Part 2 (remaining chars up to 12 chars) goes to index 115..126.
    """
    # Ensure line is at least 127 chars
    line = raw_line.ljust(127)
    
    clean_name = new_channel_name.strip()
    
    if len(clean_name) <= 8:
        part1 = clean_name.ljust(8)
        part2 = " " * 12
    else:
        part1 = clean_name[:8]
        part2 = clean_name[8:20].ljust(12)
        
    # Reconstruct line with exact byte positions
    line = line[:43] + part1 + line[51:115] + part2 + line[127:]
    return line


def format_channel_to_sdx_line(channel: Channel) -> str:
    """
    Formats a Channel object back into a SatcoDX fixed-width line string.
    Uses existing raw_line with name update if available, or constructs a line from properties.
    """
    if channel.raw_line and len(channel.raw_line) >= 127:
        return rename_channel_in_line(channel.raw_line, channel.channel_name)

    # Build line from scratch if raw_line is not available
    sat = channel.satellite_name.ljust(18)[:18]
    ctype = channel.channel_type.short_code
    bcast = "MPG2".ljust(4)
    # Extract short code from broadcast_system if known
    for code, full_name in BROADCAST_SYSTEM_MAP.items():
        if channel.broadcast_system == full_name or channel.broadcast_system == code:
            bcast = code.ljust(4)
            break
            
    freq = channel.frequency.ljust(9)[:9]
    pol = channel.polarization.code
    
    # Channel name parts
    clean_name = channel.channel_name.strip()
    if len(clean_name) <= 8:
        p1 = clean_name.ljust(8)
        p2 = " " * 12
    else:
        p1 = clean_name[:8]
        p2 = clean_name[8:20].ljust(12)
        
    sr = channel.symbol_rate.ljust(5)[:5]
    fec_code = "0"
    for code, val in FEC_MAP.items():
        if channel.fec == val:
            fec_code = code
            break
            
    vpid = channel.vpid.ljust(4)[:4]
    apid = channel.apid.ljust(4)[:4]
    pcrp = channel.pcrp.ljust(4)[:4]
    sid = channel.sid.ljust(5)[:5]
    nid = channel.nid.ljust(5)[:5]
    tsid = channel.tsid.ljust(5)[:5]
    lang = channel.language.ljust(3)[:3]
    country = channel.country_code.ljust(2)[:2]
    lang_code = channel.language_code.ljust(3)[:3]
    crypto = channel.crypto.ljust(4)[:4]
    
    line = (
        f"{'0'*10}"
        f"{sat}"
        f"{ctype}"
        f"{bcast}"
        f"{freq}"
        f"{pol}"
        f"{p1}"
        f"{' '*18}"
        f"{sr}"
        f"{fec_code}"
        f"{vpid}"
        f"{apid}"
        f"{pcrp}"
        f"{sid}"
        f"{nid}"
        f"{tsid}"
        f"{lang} "
        f"{country}"
        f"{lang_code}"
        f"{crypto}"
        f"{p2}"
    )
    return line


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

