"""
Unit tests for SatSort AppConfig & Recent Files
"""

import os
import tempfile
import unittest
from pathlib import Path
from satsort.core.config import AppConfig


class TestAppConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name) / "satsort"
        self.config_file = self.config_dir / "config.json"
        
        self.cfg = AppConfig()
        self.cfg._config_dir = self.config_dir
        self.cfg._config_file = self.config_file
        self.cfg._data = {
            "language": "Türkçe",
            "theme": "dark",
            "auto_backup": True,
            "recent_files": [],
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_recent_files_add_and_get(self):
        # Create dummy temp files
        f1 = os.path.join(self.temp_dir.name, "list1.sdx")
        f2 = os.path.join(self.temp_dir.name, "list2.sdx")
        with open(f1, "w") as f: f.write("test")
        with open(f2, "w") as f: f.write("test")

        self.cfg.add_recent_file(f1)
        self.cfg.add_recent_file(f2)

        recent = self.cfg.get_recent_files()
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0], os.path.abspath(f2))
        self.assertEqual(recent[1], os.path.abspath(f1))

    def test_recent_files_deduplication(self):
        f1 = os.path.join(self.temp_dir.name, "list1.sdx")
        with open(f1, "w") as f: f.write("test")

        self.cfg.add_recent_file(f1)
        self.cfg.add_recent_file(f1)
        recent = self.cfg.get_recent_files()
        self.assertEqual(len(recent), 1)

    def test_recent_files_clear(self):
        f1 = os.path.join(self.temp_dir.name, "list1.sdx")
        with open(f1, "w") as f: f.write("test")
        self.cfg.add_recent_file(f1)
        self.assertEqual(len(self.cfg.get_recent_files()), 1)

        self.cfg.clear_recent_files()
        self.assertEqual(len(self.cfg.get_recent_files()), 0)

    def test_auto_backup_toggle(self):
        self.assertTrue(self.cfg.get_auto_backup())
        self.cfg.set_auto_backup(False)
        self.assertFalse(self.cfg.get_auto_backup())
        self.cfg.set_auto_backup(True)
        self.assertTrue(self.cfg.get_auto_backup())


if __name__ == "__main__":
    unittest.main()
