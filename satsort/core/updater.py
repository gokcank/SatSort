"""
SatSort - Application Update Checker
Checks GitHub Releases API for newer versions of SatSort.
"""

from __future__ import annotations
import json
import re
import urllib.request
from dataclasses import dataclass
from typing import Optional, Tuple

from .. import __version__

GITHUB_API_LATEST_RELEASE = "https://api.github.com/repos/gokcank/SatSort/releases/latest"
APT_UPDATE_COMMAND = "sudo apt update && sudo apt install satsort"


@dataclass
class UpdateInfo:
    has_update: bool
    current_version: str
    latest_version: str
    release_notes: str
    html_url: str
    error: Optional[str] = None


def parse_semver(ver_str: str) -> Tuple[int, ...]:
    """Extracts numeric semver components from string, ignoring 'v' prefix."""
    cleaned = ver_str.strip().lstrip("vV")
    nums = re.findall(r"\d+", cleaned)
    if not nums:
        return (0,)
    return tuple(int(n) for n in nums)


def is_newer_version(latest_tag: str, current_ver: str) -> bool:
    """Returns True if latest_tag represents a strictly higher version than current_ver."""
    latest_parts = parse_semver(latest_tag)
    current_parts = parse_semver(current_ver)
    return latest_parts > current_parts


def check_for_updates(timeout_seconds: float = 6.0) -> UpdateInfo:
    """
    Queries GitHub API to determine if a newer version of SatSort has been released.
    Handles network timeouts and GitHub API rate limits gracefully.
    """
    req = urllib.request.Request(
        GITHUB_API_LATEST_RELEASE,
        headers={
            "User-Agent": f"SatSort-App/{__version__} (Linux)",
            "Accept": "application/vnd.github.v3+json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            if response.status != 200:
                return UpdateInfo(
                    has_update=False,
                    current_version=__version__,
                    latest_version=__version__,
                    release_notes="",
                    html_url="https://github.com/gokcank/SatSort/releases",
                    error=f"HTTP {response.status}",
                )

            data = json.loads(response.read().decode("utf-8"))
            latest_tag = data.get("tag_name", "").strip()
            latest_ver = latest_tag.lstrip("vV")
            release_notes = data.get("body", "").strip()
            html_url = data.get("html_url", "https://github.com/gokcank/SatSort/releases/latest")

            has_update = is_newer_version(latest_tag, __version__)
            return UpdateInfo(
                has_update=has_update,
                current_version=__version__,
                latest_version=latest_ver or latest_tag,
                release_notes=release_notes,
                html_url=html_url,
                error=None,
            )
    except urllib.error.URLError as e:
        return UpdateInfo(
            has_update=False,
            current_version=__version__,
            latest_version=__version__,
            release_notes="",
            html_url="https://github.com/gokcank/SatSort/releases",
            error=str(e.reason),
        )
    except Exception as e:
        return UpdateInfo(
            has_update=False,
            current_version=__version__,
            latest_version=__version__,
            release_notes="",
            html_url="https://github.com/gokcank/SatSort/releases",
            error=str(e),
        )
