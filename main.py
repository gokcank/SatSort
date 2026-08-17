#!/usr/bin/env python3
"""
SatSort - Linux Native SatcoDX Channel List Editor
Application Entry Point
"""

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from satsort.ui import MainWindow, apply_theme
from satsort.core.parser import read_sdx_file


def main() -> int:
    # High-DPI scaling attributes
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("SatSort")
    app.setOrganizationName("SatSort")
    app.setApplicationVersion("1.0.0")

    # Apply modern dark theme
    apply_theme(app)

    # Launch main window
    window = MainWindow()

    # If a file path is passed as command-line argument, open it
    if len(sys.argv) > 1:
        initial_file = sys.argv[1]
        if os.path.isfile(initial_file):
            try:
                channels = read_sdx_file(initial_file)
                window._current_file_path = initial_file
                window._all_channels = channels
                window.channel_table.set_channels(channels)
                window.setWindowTitle(f"SatSort - {os.path.basename(initial_file)}")
                window.lbl_file_info.setText(f"Açık Dosya: {initial_file}")
                if channels:
                    window.channel_table.selectRow(0)
            except Exception as e:
                print(f"Error opening initial file: {e}", file=sys.stderr)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
