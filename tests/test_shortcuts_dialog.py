"""
Unit tests for ShortcutsDialog
"""

import unittest
from PySide6.QtWidgets import QApplication
from satsort.ui.dialogs.shortcuts_dialog import ShortcutsDialog

app = QApplication.instance() or QApplication([])


class TestShortcutsDialog(unittest.TestCase):

    def test_shortcuts_dialog_instantiation(self):
        dlg = ShortcutsDialog()
        self.assertTrue(dlg.windowTitle().startswith("⌨️"))
        # Clean up
        dlg.close()


if __name__ == "__main__":
    unittest.main()
