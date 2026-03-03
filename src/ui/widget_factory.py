"""
LagerPro – WidgetFactory
========================
Statische Fabrikmethoden für alle wiederverwendbaren UI-Elemente.
Stellt sicher, dass Buttons, Labels, Cards etc. überall gleich aussehen.
"""

from PyQt5.QtWidgets import (
    QFrame, QLabel, QPushButton, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QDateEdit, QScrollArea,
    QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
    QHeaderView, QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont

from .colors import AppColors


class WidgetFactory:

    # ── Schatten ─────────────────────────────────
    @staticmethod
    def shadow(widget, blur: int = 18, color: str = "#00000022") -> QGraphicsDropShadowEffect:
        eff = QGraphicsDropShadowEffect()
        eff.setBlurRadius(blur)
        eff.setOffset(0, 4)
        eff.setColor(QColor(color))
        widget.setGraphicsEffect(eff)
        return eff

    # ── Card ─────────────────────────────────────
    @staticmethod
    def card(parent=None) -> QFrame:
        w = QFrame(parent)
        w.setObjectName("card")
        w.setStyleSheet("""
            QFrame#card {
                background: #ffffff;
                border-radius: 14px;
                border: 1px solid #d8e3f0;
            }
        """)
        WidgetFactory.shadow(w)
        return w

    # ── Label ─────────────────────────────────────
    @staticmethod
    def label(text: str, size: int = 13, bold: bool = False,
              color: str = AppColors.TEXT, parent=None) -> QLabel:
        l = QLabel(text, parent)
        f = QFont("Segoe UI", size)
        f.setBold(bold)
        l.setFont(f)
        l.setStyleSheet(f"color: {color}; background: transparent;")
        return l

    # ── Button ────────────────────────────────────
    @staticmethod
    def button(text: str, bg: str = AppColors.BLUE, fg: str = "#ffffff",
               size: int = 13, radius: int = 9) -> QPushButton:
        b = QPushButton(text)
        b.setFont(QFont("Segoe UI", size, QFont.Bold))
        b.setCursor(Qt.PointingHandCursor)
        b.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {fg};
                border-radius: {radius}px;
                padding: 9px 18px;
                border: none;
            }}
            QPushButton:hover {{ opacity: 0.85; }}
            QPushButton:pressed {{ padding-top: 11px; }}
        """)
        return b

    # ── Badge ─────────────────────────────────────
    @staticmethod
    def badge(text: str, bg: str = "#e8f0ff", fg: str = "#1a5dcf") -> QLabel:
        l = QLabel(text)
        l.setFont(QFont("Segoe UI", 11, QFont.Bold))
        l.setAlignment(Qt.AlignCenter)
        l.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 10px;
                padding: 3px 10px;
            }}
        """)
        l.setFixedHeight(24)
        return l

    # ── Text-Eingabe ──────────────────────────────
    @staticmethod
    def text_input(placeholder: str = "", parent=None) -> QLineEdit:
        e = QLineEdit(parent)
        e.setPlaceholderText(placeholder)
        e.setFont(QFont("Segoe UI", 12))
        e.setFixedHeight(38)
        e.setStyleSheet("""
            QLineEdit {
                background: #f4f7fb;
                border: 1.5px solid #d8e3f0;
                border-radius: 8px;
                padding: 0 12px;
                color: #1a2a4a;
            }
            QLineEdit:focus {
                border: 1.5px solid #1a6bff;
                background: white;
            }
        """)
        return e

    # ── Combo-Box ─────────────────────────────────
    @staticmethod
    def combo_box(items: list = None, parent=None) -> QComboBox:
        c = QComboBox(parent)
        c.setFont(QFont("Segoe UI", 12))
        c.setFixedHeight(38)
        c.setStyleSheet("""
            QComboBox {
                background: #f4f7fb;
                border: 1.5px solid #d8e3f0;
                border-radius: 8px;
                padding: 0 12px;
                color: #1a2a4a;
            }
            QComboBox:focus { border: 1.5px solid #1a6bff; }
            QComboBox::drop-down { border: none; width: 28px; }
        """)
        if items:
            c.addItems(items)
        return c

    # ── SpinBox (int) ─────────────────────────────
    @staticmethod
    def spin_box(min_val: int = 0, max_val: int = 99999, value: int = 0) -> QSpinBox:
        s = QSpinBox()
        s.setRange(min_val, max_val)
        s.setValue(value)
        s.setFont(QFont("Segoe UI", 12))
        s.setFixedHeight(38)
        s.setStyleSheet(
            "QSpinBox { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }")
        return s

    # ── SpinBox (float) ───────────────────────────
    @staticmethod
    def double_spin_box(min_val: float = 0.01, max_val: float = 99999.0,
                        value: float = 1.0, prefix: str = "€ ",
                        decimals: int = 2) -> QDoubleSpinBox:
        d = QDoubleSpinBox()
        d.setRange(min_val, max_val)
        d.setValue(value)
        d.setPrefix(prefix)
        d.setDecimals(decimals)
        d.setFont(QFont("Segoe UI", 12))
        d.setFixedHeight(38)
        d.setStyleSheet(
            "QDoubleSpinBox { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }")
        return d

    # ── Datum-Eingabe ─────────────────────────────
    @staticmethod
    def date_edit(date: QDate = None) -> QDateEdit:
        de = QDateEdit()
        de.setDate(date or QDate.currentDate())
        de.setCalendarPopup(True)
        de.setFont(QFont("Segoe UI", 12))
        de.setFixedHeight(38)
        de.setStyleSheet(
            "QDateEdit { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }")
        return de

    # ── Tabelle ───────────────────────────────────
    @staticmethod
    def table_widget(headers: list, min_height: int = 400) -> QTableWidget:
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.verticalHeader().setVisible(False)
        t.setShowGrid(False)
        t.setAlternatingRowColors(True)
        t.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        t.setMinimumHeight(min_height)
        t.setStyleSheet("""
            QTableWidget { background: transparent; border: none; outline: none; }
            QHeaderView::section {
                background: transparent; color: #7b8ea9; font-weight: bold;
                border: none; padding: 6px 8px; border-bottom: 2px solid #d8e3f0;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #f0f4f8; color: #1a2a4a; }
            QTableWidget::item:selected { background: #e8f0ff; color: #1a2a4a; }
            QTableWidget::item:alternate { background: #f8fafd; }
        """)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return t
