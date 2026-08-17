"""
SatSort - Modern Dark Theme & Stylesheet Definition
"""

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
    spacing: 6px;
    padding: 6px 10px;
}

QToolButton {
    background-color: #242b38;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #334155;
    border-color: #475569;
    color: #ffffff;
}

QToolButton:pressed {
    background-color: #1e293b;
}

QToolButton:disabled {
    background-color: #161b22;
    color: #64748b;
    border-color: #1e293b;
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


def apply_theme(app) -> None:
    """Applies the dark theme stylesheet to the Qt application."""
    app.setStyleSheet(DARK_THEME_QSS)
