"""
SatSort - Application Update Checker Test Suite
Verifies:
  1. Semantic version parsing and comparison logic.
  2. GitHub release check parsing and error handling.
  3. UpdateDialog UI states (New version available, already up to date, network error).
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import json
import urllib.error

from PySide6.QtWidgets import QApplication

from satsort.core.updater import (
    parse_semver,
    is_newer_version,
    check_for_updates,
    UpdateInfo,
    APT_UPDATE_COMMAND,
)
from satsort.ui.dialogs.update_dialog import UpdateDialog


class TestUpdater(unittest.TestCase):
    """Test suite for update checking logic and UI dialog."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_parse_semver(self):
        """Verifies clean extraction of version numbers."""
        self.assertEqual(parse_semver("v1.0.2"), (1, 0, 2))
        self.assertEqual(parse_semver("1.0.1"), (1, 0, 1))
        self.assertEqual(parse_semver("V2.1.0-beta"), (2, 1, 0))
        self.assertEqual(parse_semver("unknown"), (0,))

    def test_is_newer_version(self):
        """Verifies version comparisons."""
        self.assertTrue(is_newer_version("v1.0.2", "1.0.1"))
        self.assertTrue(is_newer_version("v1.1.0", "1.0.9"))
        self.assertTrue(is_newer_version("2.0.0", "1.9.9"))

        self.assertFalse(is_newer_version("v1.0.1", "1.0.1"))
        self.assertFalse(is_newer_version("v1.0.0", "1.0.1"))
        self.assertFalse(is_newer_version("0.9.8", "1.0.0"))

    @patch("urllib.request.urlopen")
    def test_check_for_updates_available(self, mock_urlopen):
        """Verifies update detection when GitHub reports newer release."""
        fake_response = io.BytesIO(json.dumps({
            "tag_name": "v9.9.9",
            "body": "Awesome new features and performance improvements.",
            "html_url": "https://github.com/gokcank/SatSort/releases/tag/v9.9.9"
        }).encode("utf-8"))
        fake_response.status = 200

        mock_urlopen.return_value.__enter__.return_value = fake_response

        info = check_for_updates()
        self.assertTrue(info.has_update)
        self.assertEqual(info.latest_version, "9.9.9")
        self.assertEqual(info.release_notes, "Awesome new features and performance improvements.")
        self.assertIsNone(info.error)

    @patch("urllib.request.urlopen")
    def test_check_for_updates_already_current(self, mock_urlopen):
        """Verifies status when currently running latest version."""
        from satsort import __version__
        fake_response = io.BytesIO(json.dumps({
            "tag_name": f"v{__version__}",
            "body": "Current version notes.",
            "html_url": "https://github.com/gokcank/SatSort/releases/latest"
        }).encode("utf-8"))
        fake_response.status = 200

        mock_urlopen.return_value.__enter__.return_value = fake_response

        info = check_for_updates()
        self.assertFalse(info.has_update)
        self.assertEqual(info.latest_version, __version__)
        self.assertIsNone(info.error)

    @patch("urllib.request.urlopen")
    def test_check_for_updates_network_error(self, mock_urlopen):
        """Verifies graceful handling of connection failures."""
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        info = check_for_updates()
        self.assertFalse(info.has_update)
        self.assertIsNotNone(info.error)
        self.assertIn("Connection refused", info.error)

    def test_update_dialog_ui_states(self):
        """Verifies UpdateDialog renders across update, up-to-date, and error states without crashing."""
        # 1. Update available state
        info_update = UpdateInfo(
            has_update=True,
            current_version="1.0.1",
            latest_version="1.1.0",
            release_notes="New UI improvements.",
            html_url="https://github.com/gokcank/SatSort/releases/v1.1.0",
        )
        dialog_update = UpdateDialog(precomputed_result=info_update)
        self.assertFalse(dialog_update.btn_action.isHidden())
        self.assertIn("1.1.0", dialog_update.status_title.text())
        dialog_update.close()

        # 2. Up to date state
        info_current = UpdateInfo(
            has_update=False,
            current_version="1.0.1",
            latest_version="1.0.1",
            release_notes="",
            html_url="https://github.com/gokcank/SatSort/releases/latest",
        )
        dialog_current = UpdateDialog(precomputed_result=info_current)
        self.assertTrue(dialog_current.btn_action.isHidden())
        dialog_current.close()

        # 3. Error state
        info_err = UpdateInfo(
            has_update=False,
            current_version="1.0.1",
            latest_version="1.0.1",
            release_notes="",
            html_url="https://github.com/gokcank/SatSort/releases",
            error="DNS resolution failed",
        )
        dialog_err = UpdateDialog(precomputed_result=info_err)
        self.assertIn("⚠️", dialog_err.icon_lbl.text())
        dialog_err.close()


if __name__ == "__main__":
    unittest.main()
