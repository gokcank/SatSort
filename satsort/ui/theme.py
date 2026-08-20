"""
SatSort - Theme Definitions (Dark & Light) & Theme Manager
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path.home() / ".config" / "satsort" / "config.json"

DARK_THEME_QSS = """
/* Global Window & Font */
QMainWindow, QDialog, QWidget {
    background-color: #1a1d24;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Ubuntu', 'DejaVu Sans', sans-serif;
    font-size: 13px;
}

/* Menu Bar & Menus */
QMenuBar {
    background-color: #14171d;
    color: #cbd5e1;
    border-bottom: 1px solid #2d3748;
    padding: 3px 6px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #2d3748;
    color: #ffffff;
}

QMenu {
    background-color: #1e222b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 16px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #3b82f6;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #334155;
    margin: 4px 8px;
}

/* ToolBar */
QToolBar {
    background-color: #14171d;
    border-bottom: 1px solid #2d3748;
    spacing: 2px;
    padding: 0px 4px;
}

QToolBar::separator {
    width: 1px;
    background-color: #334155;
    margin: 6px 3px;
}

QToolButton {
    background-color: transparent;
    color: #94a3b8;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 1px 4px;
    margin: 0px 1px;
    font-size: 10.5px;
    font-weight: 500;
    min-width: 48px;
    max-width: 90px;
}

QToolButton:hover {
    background-color: #1e222b;
    border-color: #334155;
    color: #f8fafc;
}

QToolButton:pressed, QToolButton:checked {
    background-color: rgba(59, 130, 246, 0.2);
    border: 1px solid #3b82f6;
    color: #f8fafc;
}

QToolButton:disabled {
    background-color: transparent;
    color: #475569;
    border-color: transparent;
}

/* Buttons */
QPushButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #2563eb;
}

QPushButton:pressed {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #334155;
    color: #94a3b8;
}

QPushButton.secondary {
    background-color: #334155;
    color: #e2e8f0;
}

QPushButton.secondary:hover {
    background-color: #475569;
}

/* Input Fields & Search */
QLineEdit, QSpinBox, QComboBox {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #3b82f6;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #3b82f6;
}

/* Tables & Tree Views */
QTableWidget, QTableView, QTreeWidget, QListView {
    background-color: #14171d;
    color: #f1f5f9;
    border: 1px solid #2d3748;
    border-radius: 8px;
    gridline-color: #1e293b;
    selection-background-color: #1e3a8a;
    selection-color: #ffffff;
    outline: none;
}

QTableWidget::item, QTableView::item {
    padding: 6px 8px;
    border-bottom: 1px solid #1e2533;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #1e3a8a;
    color: #ffffff;
}

QTableWidget::item:hover, QTableView::item:hover {
    background-color: #222938;
}

QHeaderView::section {
    background-color: #0f131a;
    color: #94a3b8;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #232d3f;
    border-bottom: 2px solid #334155;
    font-weight: bold;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #14171d;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #14171d;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #334155;
    min-width: 20px;
    border-radius: 5px;
}

/* Status Bar */
QStatusBar {
    background-color: #14171d;
    color: #94a3b8;
    border-top: 1px solid #2d3748;
    padding: 4px 8px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 6px;
    background-color: #1a1d24;
}

QTabBar::tab {
    background-color: #14171d;
    color: #94a3b8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1a1d24;
    color: #60a5fa;
    border-bottom: 2px solid #3b82f6;
    font-weight: bold;
}

/* GroupBox & Cards */
QGroupBox {
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 14px;
    font-weight: 600;
    color: #94a3b8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background-color: #1a1d24;
}
"""

LIGHT_THEME_QSS = """
/* Global Window & Font */
QMainWindow, QDialog, QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', 'Ubuntu', 'DejaVu Sans', sans-serif;
    font-size: 13px;
}

/* Menu Bar & Menus */
QMenuBar {
    background-color: #f1f5f9;
    color: #334155;
    border-bottom: 1px solid #cbd5e1;
    padding: 3px 6px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #e2e8f0;
    color: #0f172a;
}

QMenu {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 16px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #3b82f6;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #e2e8f0;
    margin: 4px 8px;
}

/* ToolBar */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    spacing: 2px;
    padding: 0px 4px;
}

QToolBar::separator {
    width: 1px;
    background-color: #cbd5e1;
    margin: 6px 3px;
}

QToolButton {
    background-color: transparent;
    color: #64748b;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 1px 4px;
    margin: 0px 1px;
    font-size: 10.5px;
    font-weight: 500;
    min-width: 48px;
    max-width: 90px;
}

QToolButton:hover {
    background-color: #f1f5f9;
    border-color: #cbd5e1;
    color: #0f172a;
}

QToolButton:pressed, QToolButton:checked {
    background-color: #dbeafe;
    border: 1px solid #3b82f6;
    color: #1d4ed8;
}

QToolButton:disabled {
    background-color: transparent;
    color: #94a3b8;
    border-color: transparent;
}

/* Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
}

QPushButton.secondary {
    background-color: #e2e8f0;
    color: #334155;
}

QPushButton.secondary:hover {
    background-color: #cbd5e1;
}

/* Input Fields & Search */
QLineEdit, QSpinBox, QComboBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #3b82f6;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #2563eb;
}

/* Tables & Tree Views */
QTableWidget, QTableView, QTreeWidget, QListView {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    selection-background-color: #bfdbfe;
    selection-color: #1e3a8a;
    outline: none;
}

QTableWidget::item, QTableView::item {
    padding: 6px 8px;
    border-bottom: 1px solid #f1f5f9;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #bfdbfe;
    color: #1e3a8a;
}

QTableWidget::item:hover, QTableView::item:hover {
    background-color: #f8fafc;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #e2e8f0;
    border-bottom: 2px solid #cbd5e1;
    font-weight: bold;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #f1f5f9;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f1f5f9;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    min-width: 20px;
    border-radius: 5px;
}

/* Status Bar */
QStatusBar {
    background-color: #f1f5f9;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
    padding: 4px 8px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background-color: #f8fafc;
}

QTabBar::tab {
    background-color: #e2e8f0;
    color: #64748b;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #f8fafc;
    color: #2563eb;
    border-bottom: 2px solid #2563eb;
    font-weight: bold;
}

/* GroupBox & Cards */
QGroupBox {
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 14px;
    font-weight: 600;
    color: #475569;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background-color: #f8fafc;
}
"""

_current_theme = "dark"


def get_current_theme() -> str:
    """Returns the name of the active theme ('dark' or 'light')."""
    return _current_theme


def load_theme_preference() -> str:
    """Loads the saved theme from ~/.config/satsort/config.json."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                theme = data.get("theme")
                if theme in ("dark", "light"):
                    return theme
        except Exception:
            pass
    return "dark"


def save_theme_preference(theme: str) -> None:
    """Saves the active theme preference to ~/.config/satsort/config.json."""
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data["theme"] = theme
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def apply_theme(app, theme: Optional[str] = None) -> None:
    """Applies either dark or light theme to the application and saves preference."""
    global _current_theme
    selected = theme or load_theme_preference()
    _current_theme = selected

    if selected == "light":
        app.setStyleSheet(LIGHT_THEME_QSS)
    else:
        app.setStyleSheet(DARK_THEME_QSS)

    save_theme_preference(selected)


def toggle_theme(app) -> str:
    """Toggles between dark and light themes and returns the new theme name."""
    global _current_theme
    new_theme = "light" if _current_theme == "dark" else "dark"
    apply_theme(app, new_theme)
    return new_theme
