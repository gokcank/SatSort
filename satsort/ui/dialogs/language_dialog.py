"""
SatSort - Language Selection Dialog (Form6)
"""

from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QTextEdit,
    QPushButton,
)

from ...i18n import i18n, t


class LanguageSelectionDialog(QDialog):
    """Dialog for choosing the application interface language and viewing translator credits."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("T168"))  # Dil - Language
        self.setFixedSize(380, 260)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Label
        lbl = QLabel(t("T169") + ":")  # Bir Dil Seçiniz / Select a Language
        lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(lbl)

        # Language dropdown
        self.combo = QComboBox()
        self.combo.addItems(i18n.get_supported_languages())
        self.combo.setCurrentText(i18n.current_language)
        self.combo.currentIndexChanged.connect(self._on_language_selected)
        layout.addWidget(self.combo)

        # Translator Info Box
        self.txt_info = QTextEdit()
        self.txt_info.setReadOnly(True)
        self.txt_info.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                color: #94a3b8;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.txt_info)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_ok = QPushButton(t("T147"))  # Tamam / OK
        self.btn_ok.clicked.connect(self._on_accept)
        btn_layout.addWidget(self.btn_ok)

        self.btn_cancel = QPushButton(t("T107"))  # Kapat
        self.btn_cancel.setProperty("class", "secondary")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        self._on_language_selected(self.combo.currentIndex())

    def _on_language_selected(self, index: int) -> None:
        selected_lang = self.combo.currentText()
        translator = i18n.get_text("Translator", language=selected_lang)
        info = i18n.get_text("TranslatorInfo", language=selected_lang)
        self.txt_info.setPlainText(f"{translator}\n\n{info}")

    def _on_accept(self) -> None:
        selected_lang = self.combo.currentText()
        i18n.set_language(selected_lang)
        self.accept()
