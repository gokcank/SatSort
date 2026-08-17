"""
SatSort - Satellite Channel List Editor
Core Data Models
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class ChannelType(str, Enum):
    TV = "Television Channel"
    RADIO = "Radio Channel"
    DATA = "Data Transmission"
    PACKAGE = "Package Transponder"
    UNKNOWN = "Unknown"

    @classmethod
    def from_code(cls, code: str) -> "ChannelType":
        mapping = {
            "T": cls.TV,
            "R": cls.RADIO,
            "D": cls.DATA,
            "-": cls.PACKAGE,
        }
        return mapping.get(code.upper(), cls.UNKNOWN)

    @property
    def short_code(self) -> str:
        mapping = {
            ChannelType.TV: "T",
            ChannelType.RADIO: "R",
            ChannelType.DATA: "D",
            ChannelType.PACKAGE: "-",
            ChannelType.UNKNOWN: "?",
        }
        return mapping.get(self, "?")


class Polarization(str, Enum):
    VERTICAL = "Vertical"
    HORIZONTAL = "Horizontal"
    UNKNOWN = "Unknown"

    @classmethod
    def from_code(cls, code: str) -> "Polarization":
        if code == "0":
            return cls.VERTICAL
        elif code == "1":
            return cls.HORIZONTAL
        return cls.UNKNOWN

    @property
    def code(self) -> str:
        if self == Polarization.VERTICAL:
            return "0"
        elif self == Polarization.HORIZONTAL:
            return "1"
        return " "


@dataclass
class Channel:
    """Represents a single satellite channel record in SatcoDX format."""
    
    # Raw original line from .sdx file
    raw_line: str = ""
    
    # Main channel attributes
    satellite_name: str = ""
    channel_name: str = ""
    channel_type: ChannelType = ChannelType.UNKNOWN
    broadcast_system: str = ""
    frequency: str = ""
    polarization: Polarization = Polarization.UNKNOWN
    symbol_rate: str = ""
    fec: str = ""
    
    # PID parameters
    vpid: str = ""
    apid: str = ""
    pcrp: str = ""
    sid: str = ""
    nid: str = ""
    tsid: str = ""
    
    # Regional & encryption
    language: str = ""
    country_code: str = ""
    language_code: str = ""
    crypto: str = ""
    
    # UI state flags
    is_checked: bool = False
    is_modified: bool = False
    
    @property
    def transponder_key(self) -> Tuple[str, str, str]:
        """Returns a unique key identifying the transponder package (Frequency, Polarization, SymbolRate)."""
        return (
            self.frequency.strip(),
            self.polarization.value,
            self.symbol_rate.strip(),
        )

    @property
    def is_encrypted(self) -> bool:
        """Checks if the channel has encryption flags set."""
        return bool(self.crypto.strip() and self.crypto.strip() != "0" and self.crypto.strip() != "----")

    def clone(self) -> "Channel":
        """Creates a shallow copy of the channel object."""
        return Channel(
            raw_line=self.raw_line,
            satellite_name=self.satellite_name,
            channel_name=self.channel_name,
            channel_type=self.channel_type,
            broadcast_system=self.broadcast_system,
            frequency=self.frequency,
            polarization=self.polarization,
            symbol_rate=self.symbol_rate,
            fec=self.fec,
            vpid=self.vpid,
            apid=self.apid,
            pcrp=self.pcrp,
            sid=self.sid,
            nid=self.nid,
            tsid=self.tsid,
            language=self.language,
            country_code=self.country_code,
            language_code=self.language_code,
            crypto=self.crypto,
            is_checked=self.is_checked,
            is_modified=self.is_modified,
        )
