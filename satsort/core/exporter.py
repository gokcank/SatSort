"""
SatSort - Channel List Export Engine
Supports exporting channel data to CSV, readable TXT, and M3U playlist formats.
"""

from __future__ import annotations
import csv
from typing import List
from .models import Channel, ChannelType, Polarization


def export_to_csv(channels: List[Channel], file_path: str) -> None:
    """
    Exports channel list to a UTF-8 encoded CSV file with headers.
    """
    headers = [
        "No",
        "Channel Name",
        "Type",
        "Frequency",
        "Polarization",
        "Symbol Rate",
        "FEC",
        "SID",
        "VPID",
        "APID",
        "PCR PID",
        "Encryption",
        "Satellite",
    ]

    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for idx, ch in enumerate(channels, 1):
            pol_str = "V" if ch.polarization == Polarization.VERTICAL else ("H" if ch.polarization == Polarization.HORIZONTAL else "")
            type_str = "Radio" if ch.channel_type == ChannelType.RADIO else ("TV" if ch.channel_type == ChannelType.TV else ch.channel_type.value)
            crypto_str = "FTA" if not ch.is_encrypted else (ch.crypto.strip() or "Encrypted")

            writer.writerow([
                idx,
                ch.channel_name,
                type_str,
                ch.frequency,
                pol_str,
                ch.symbol_rate,
                ch.fec,
                ch.sid,
                ch.vpid,
                ch.apid,
                ch.pcrp,
                crypto_str,
                ch.satellite_name,
            ])


def export_to_txt(channels: List[Channel], file_path: str) -> None:
    """
    Exports channel list to a clean, formatted plain text table.
    """
    lines = []
    lines.append(f"{'No.':<5} | {'Kanal Adı / Channel Name':<28} | {'Tür':<6} | {'Frekans':<10} | {'Sembol':<7} | {'Şifre':<6} | {'Uydu':<15}")
    lines.append("-" * 90)

    for idx, ch in enumerate(channels, 1):
        pol_str = "V" if ch.polarization == Polarization.VERTICAL else "H"
        freq_pol = f"{ch.frequency} {pol_str}" if ch.frequency else ""
        type_str = "Radyo" if ch.channel_type == ChannelType.RADIO else "TV"
        crypto_str = "FTA" if not ch.is_encrypted else (ch.crypto.strip() or "Şifreli")

        name = ch.channel_name[:26]
        lines.append(
            f"{idx:<5} | {name:<28} | {type_str:<6} | {freq_pol:<10} | {ch.symbol_rate:<7} | {crypto_str:<6} | {ch.satellite_name[:15]:<15}"
        )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def export_to_m3u(channels: List[Channel], file_path: str) -> None:
    """
    Exports channel list to an extended M3U / M3U8 playlist with DVB parameter metadata.
    """
    lines = ["#EXTM3U"]

    for idx, ch in enumerate(channels, 1):
        group = "Radio" if ch.channel_type == ChannelType.RADIO else "TV"
        pol_str = "V" if ch.polarization == Polarization.VERTICAL else "H"
        lines.append(
            f'#EXTINF:-1 tvg-id="{ch.sid}" tvg-name="{ch.channel_name}" tvg-chno="{idx}" group-title="{group}",{ch.channel_name}'
        )
        # Standard DVB locator URI for media players (VLC, TVheadend, etc.)
        dvb_uri = f"dvb-s://frequency={ch.frequency}&polarization={pol_str}&symbol_rate={ch.symbol_rate}&service_id={ch.sid}"
        lines.append(dvb_uri)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
