"""
LagerPro Software – PyQt5 Dashboard (Enhanced)
================================================
Features:
  - CSV Export (Artikel, Bestellungen, Lagerbestand)
  - Bestellungen speichern & als PDF drucken
  - Neue Artikel bestellen (Formular)
  - Detailansichten für alle Seiten

Installation:
    pip install PyQt5 reportlab

Ausführen:
    python lagerpro_app.py
"""

import sys
import csv
import os
import json
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy, QStackedWidget,
    QLineEdit, QMessageBox, QGraphicsDropShadowEffect, QDialog,
    QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QFileDialog, QDialogButtonBox, QGroupBox, QTabWidget, QDateEdit,
    QSplitter, QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt5.QtCore import Qt, QSize, QDate, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import (
    QColor, QFont, QPalette, QLinearGradient, QPainter, QBrush,
    QPen, QPolygon, QIcon, QPixmap, QPainterPath
)

# ──────────────────────────────────────────────
# COLOR PALETTE
# ──────────────────────────────────────────────
C_SIDEBAR       = "#0c2145"
C_SIDEBAR_DARK  = "#071428"
C_SIDEBAR_ACT   = "#1e4080"
C_BLUE          = "#1a6bff"
C_ORANGE        = "#ff8c00"
C_GREEN         = "#28c76f"
C_RED           = "#ea5455"
C_YELLOW        = "#ff9f43"
C_PAGE          = "#eef2f9"
C_CARD          = "#ffffff"
C_TEXT          = "#1a2a4a"
C_MUTED         = "#7b8ea9"
C_BORDER        = "#d8e3f0"

# ──────────────────────────────────────────────
# DATA STORE (in-memory, persistent via JSON)
# ──────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "lagerpro_data.json")

def load_data():
    default = {
        "artikel": [
            {"id": "ABC123", "name": "Bio Vollmilch 1L", "kategorie": "Molkereiprodukte", "bestand": 145, "min_bestand": 50, "preis": 1.29, "lieferant": "Lokaler Bauer", "mhd": "2025-03-15"},
            {"id": "ASE476", "name": "H-Milch 1L", "kategorie": "Molkereiprodukte", "bestand": 320, "min_bestand": 100, "preis": 0.99, "lieferant": "Zentrallager", "mhd": "2025-06-30"},
            {"id": "NE1789", "name": "H-Milch 0,5L", "kategorie": "Molkereiprodukte", "bestand": 12, "min_bestand": 50, "preis": 0.79, "lieferant": "Zentrallager", "mhd": "2025-02-28"},
            {"id": "ABC133", "name": "Bio Orangensaft 1L", "kategorie": "Getränke", "bestand": 450, "min_bestand": 80, "preis": 2.49, "lieferant": "Getränke GmbH", "mhd": "2025-09-01"},
            {"id": "DEF446", "name": "TK Pizza Salami", "kategorie": "Tiefkühlprodukte", "bestand": 120, "min_bestand": 30, "preis": 3.99, "lieferant": "Zentrallager", "mhd": "2025-12-01"},
            {"id": "CH1799", "name": "Tomaten (1kg)", "kategorie": "Obst & Gemüse", "bestand": 20, "min_bestand": 40, "preis": 1.99, "lieferant": "Lokale Erzeuger", "mhd": "2025-02-26"},
        ],
        "bestellungen": [
            {"id": "#567213", "datum": "2025-02-20", "lieferant": "Lokaler Bauer", "artikel": "Bio Vollmilch 1L", "menge": 200, "status": "Unterwegs", "gesamt": 258.00},
            {"id": "#567132", "datum": "2025-02-19", "lieferant": "Obst & Gemüse", "artikel": "Tomaten (1kg)", "menge": 100, "status": "Unterwegs", "gesamt": 199.00},
            {"id": "#567099", "datum": "2025-02-18", "lieferant": "Pfandflaschen", "artikel": "Pfandflaschen Palette", "menge": 5, "status": "Anrufen", "gesamt": 75.00},
            {"id": "#566988", "datum": "2025-02-17", "lieferant": "Zentrallager", "artikel": "H-Milch 1L", "menge": 500, "status": "Geliefert", "gesamt": 495.00},
        ],
        "lieferanten": [
            {"name": "Zentrallager", "kontakt": "info@zentrallager.de", "telefon": "089-12345", "lieferungen": 134},
            {"name": "Lokaler Bauer", "kontakt": "hof@lokalbauer.de", "telefon": "08141-9876", "lieferungen": 89},
            {"name": "Getränke GmbH", "kontakt": "order@getraenke.de", "telefon": "030-55678", "lieferungen": 76},
            {"name": "Lokale Erzeuger", "kontakt": "info@lokal.de", "telefon": "089-44321", "lieferungen": 121},
        ]
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return default

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

APP_DATA = load_data()


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def shadow(widget, blur=18, color="#00000022"):
    eff = QGraphicsDropShadowEffect()
    eff.setBlurRadius(blur)
    eff.setOffset(0, 4)
    eff.setColor(QColor(color))
    widget.setGraphicsEffect(eff)
    return eff


def card(parent=None):
    w = QFrame(parent)
    w.setObjectName("card")
    w.setStyleSheet("""
        QFrame#card {
            background: #ffffff;
            border-radius: 14px;
            border: 1px solid #d8e3f0;
        }
    """)
    shadow(w)
    return w


def label(text, size=13, bold=False, color=C_TEXT, parent=None):
    l = QLabel(text, parent)
    f = QFont("Segoe UI", size)
    f.setBold(bold)
    l.setFont(f)
    l.setStyleSheet(f"color: {color}; background: transparent;")
    return l


def btn(text, bg=C_BLUE, fg="#ffffff", size=13, radius=9):
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
        QPushButton:hover {{
            opacity: 0.85;
        }}
        QPushButton:pressed {{
            padding-top: 11px;
        }}
    """)
    return b


def badge(text, bg="#e8f0ff", fg="#1a5dcf"):
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


def styled_input(placeholder="", parent=None):
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


def styled_combo(items=None, parent=None):
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


# ──────────────────────────────────────────────
# CSV EXPORT
# ──────────────────────────────────────────────
def export_csv(data, headers, title="Export", parent=None):
    path, _ = QFileDialog.getSaveFileName(parent, f"CSV exportieren – {title}", f"{title}.csv", "CSV Dateien (*.csv)")
    if not path:
        return
    try:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data)
        QMessageBox.information(parent, "Export erfolgreich", f"Datei gespeichert:\n{path}")
    except Exception as e:
        QMessageBox.critical(parent, "Exportfehler", str(e))


# ──────────────────────────────────────────────
# PDF GENERATION
# ──────────────────────────────────────────────
def generate_order_pdf(bestellung, parent=None):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        QMessageBox.warning(parent, "reportlab fehlt",
            "Bitte installieren Sie reportlab:\n\npip install reportlab")
        return

    path, _ = QFileDialog.getSaveFileName(parent, "Bestellung als PDF speichern",
        f"Bestellung_{bestellung['id'].replace('#','')}.pdf", "PDF Dateien (*.pdf)")
    if not path:
        return

    try:
        doc = SimpleDocTemplate(path, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []

        # Header
        title_style = ParagraphStyle("title", parent=styles["Title"],
            fontSize=22, textColor=colors.HexColor("#0c2145"), spaceAfter=6)
        story.append(Paragraph("🤖 LAGERPRO – Bestellschein", title_style))

        sub_style = ParagraphStyle("sub", parent=styles["Normal"],
            fontSize=10, textColor=colors.HexColor("#7b8ea9"), spaceAfter=20)
        story.append(Paragraph(f"Erstellt am: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr", sub_style))
        story.append(Spacer(1, 0.3*cm))

        # Info table
        info_data = [
            ["Bestell-ID:", bestellung.get("id","–")],
            ["Datum:", bestellung.get("datum","–")],
            ["Lieferant:", bestellung.get("lieferant","–")],
            ["Artikel:", bestellung.get("artikel","–")],
            ["Menge:", str(bestellung.get("menge","–"))],
            ["Status:", bestellung.get("status","–")],
            ["Gesamtbetrag:", f"€ {bestellung.get('gesamt', 0):.2f}"],
        ]
        info_table = Table(info_data, colWidths=[5*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 11),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#0c2145")),
            ("TEXTCOLOR", (1,0), (1,-1), colors.HexColor("#1a2a4a")),
            ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#f4f7fb"), colors.white]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#d8e3f0")),
            ("ROUNDEDCORNERS", [4,4,4,4]),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 1*cm))

        # Footer
        footer_style = ParagraphStyle("footer", parent=styles["Normal"],
            fontSize=9, textColor=colors.HexColor("#7b8ea9"))
        story.append(Paragraph("LagerPro Software – Automatisch generierter Bestellschein", footer_style))

        doc.build(story)
        QMessageBox.information(parent, "PDF erstellt", f"PDF gespeichert:\n{path}")

    except Exception as e:
        QMessageBox.critical(parent, "PDF Fehler", str(e))


# ──────────────────────────────────────────────
# GRADIENT WIDGET
# ──────────────────────────────────────────────
class GradientWidget(QWidget):
    def __init__(self, c1, c2, radius=14, parent=None):
        super().__init__(parent)
        self.c1, self.c2 = QColor(c1), QColor(c2)
        self.radius = radius

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, self.c1)
        grad.setColorAt(1, self.c2)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        p.fillPath(path, QBrush(grad))


# ──────────────────────────────────────────────
# MINI LINE CHART
# ──────────────────────────────────────────────
class LineChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(170)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.series1 = [85, 60, 75, 40, 55, 35, 30]
        self.series2 = [95, 80, 85, 65, 75, 55, 50]
        self.labels  = ["Apr", "8", "11", "22", "22", "25", "25"]

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 34, 16, 10, 30
        cw = W - pad_l - pad_r
        ch = H - pad_t - pad_b

        def to_px(idx, val):
            x = pad_l + idx * cw / (len(self.series1) - 1)
            y = pad_t + val * ch / 120
            return int(x), int(y)

        p.setPen(QPen(QColor("#f0f4f8"), 1))
        for i in range(5):
            yy = pad_t + i * ch // 4
            p.drawLine(pad_l, yy, W - pad_r, yy)

        y_labels = ["12k", "3k", "2k", "1k", "0"]
        p.setPen(QPen(QColor(C_MUTED)))
        p.setFont(QFont("Segoe UI", 8))
        for i, yl in enumerate(y_labels):
            yy = pad_t + i * ch // 4
            p.drawText(0, yy + 4, 30, 14, Qt.AlignRight, yl)

        def draw_area(series, color):
            pts = [to_px(i, v) for i, v in enumerate(series)]
            path = QPainterPath()
            path.moveTo(pts[0][0], pts[0][1])
            for x, y in pts[1:]:
                path.lineTo(x, y)
            path.lineTo(pts[-1][0], H - pad_b)
            path.lineTo(pts[0][0], H - pad_b)
            path.closeSubpath()
            c = QColor(color)
            c.setAlpha(40)
            p.fillPath(path, QBrush(c))

        draw_area(self.series1, C_BLUE)
        draw_area(self.series2, C_GREEN)

        def draw_line(series, color):
            pts = [to_px(i, v) for i, v in enumerate(series)]
            pen = QPen(QColor(color), 2)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            p.setPen(pen)
            for i in range(len(pts) - 1):
                p.drawLine(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
            p.setBrush(QBrush(QColor(color)))
            for x, y in pts:
                p.drawEllipse(x - 3, y - 3, 6, 6)

        draw_line(self.series1, C_BLUE)
        draw_line(self.series2, C_GREEN)

        p.setPen(QPen(QColor(C_MUTED)))
        p.setFont(QFont("Segoe UI", 8))
        for i, xl in enumerate(self.labels):
            x = pad_l + i * cw // (len(self.labels) - 1) - 10
            p.drawText(x, H - pad_b + 6, 24, 16, Qt.AlignCenter, xl)


# ──────────────────────────────────────────────
# KPI CARD
# ──────────────────────────────────────────────
class KpiCard(GradientWidget):
    def __init__(self, title, value, icon_char, c1, c2, on_click=None, parent=None):
        super().__init__(c1, c2, parent=parent)
        self.setFixedHeight(100)
        self.on_click = on_click
        shadow(self)
        self.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 14, 22, 14)

        left = QVBoxLayout()
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 11))
        t.setStyleSheet("color: rgba(255,255,255,200); background: transparent;")
        v = QLabel(value)
        v.setFont(QFont("Segoe UI", 36, QFont.Black))
        v.setStyleSheet("color: white; background: transparent;")
        left.addWidget(t)
        left.addWidget(v)

        ic = QLabel(icon_char)
        ic.setFont(QFont("Segoe UI", 34))
        ic.setStyleSheet("color: rgba(255,255,255,80); background: transparent;")
        ic.setAlignment(Qt.AlignCenter)

        lay.addLayout(left)
        lay.addStretch()
        lay.addWidget(ic)

    def mousePressEvent(self, e):
        if self.on_click:
            self.on_click()


# ──────────────────────────────────────────────
# ARTIKEL DETAIL DIALOG
# ──────────────────────────────────────────────
class ArtikelDetailDialog(QDialog):
    def __init__(self, artikel, parent=None):
        super().__init__(parent)
        self.artikel = artikel
        self.setWindowTitle(f"Artikeldetail – {artikel['name']}")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"background: {C_PAGE};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        # Title
        lay.addWidget(label(artikel["name"], 18, bold=True))

        c = card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)
        fl.setLabelAlignment(Qt.AlignRight)

        fields = [
            ("Artikel-ID:", artikel["id"]),
            ("Kategorie:", artikel["kategorie"]),
            ("Aktueller Bestand:", f"{artikel['bestand']} Stück"),
            ("Mindestbestand:", f"{artikel['min_bestand']} Stück"),
            ("Preis:", f"€ {artikel['preis']:.2f}"),
            ("Lieferant:", artikel["lieferant"]),
            ("MHD:", artikel["mhd"]),
        ]
        for lbl, val in fields:
            l = label(lbl, 12, bold=True, color=C_MUTED)
            v = label(val, 12)
            fl.addRow(l, v)

        lay.addWidget(c)

        # Bestand indicator
        ratio = artikel["bestand"] / max(artikel["min_bestand"], 1)
        if ratio < 0.5:
            status_text, status_bg, status_fg = "⚠ Kritisch niedrig", "#ffeaea", "#c0392b"
        elif ratio < 1.0:
            status_text, status_bg, status_fg = "⚠ Unter Mindestbestand", "#fff4e0", "#b86200"
        else:
            status_text, status_bg, status_fg = "✅ Bestand OK", "#e8faf2", "#1a8a52"

        status_lbl = badge(status_text, status_bg, status_fg)
        status_lbl.setFixedHeight(32)
        lay.addWidget(status_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        b_bestell = btn("📦 Nachbestellen", C_BLUE)
        b_bestell.clicked.connect(lambda: self._nachbestellen())
        b_csv = btn("📊 CSV Export", C_GREEN)
        b_csv.clicked.connect(lambda: export_csv([artikel],
            ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"],
            f"Artikel_{artikel['id']}", self))
        b_close = btn("Schließen", bg="#e0e7f0", fg=C_TEXT)
        b_close.clicked.connect(self.close)
        btn_row.addWidget(b_bestell)
        btn_row.addWidget(b_csv)
        btn_row.addStretch()
        btn_row.addWidget(b_close)
        lay.addLayout(btn_row)

    def _nachbestellen(self):
        dlg = NeueBestellungDialog(pre_artikel=self.artikel, parent=self)
        dlg.exec_()


# ──────────────────────────────────────────────
# NEUE BESTELLUNG DIALOG
# ──────────────────────────────────────────────
class NeueBestellungDialog(QDialog):
    def __init__(self, pre_artikel=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neue Bestellung aufgeben")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background: {C_PAGE};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        lay.addWidget(label("📦 Neue Bestellung", 18, bold=True))

        c = card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        # Lieferant
        lieferanten = [l["name"] for l in APP_DATA.get("lieferanten", [])]
        self.cb_lieferant = styled_combo(lieferanten)

        # Artikel
        artikel_namen = [a["name"] for a in APP_DATA.get("artikel", [])]
        self.cb_artikel = styled_combo(artikel_namen)
        if pre_artikel:
            idx = artikel_namen.index(pre_artikel["name"]) if pre_artikel["name"] in artikel_namen else 0
            self.cb_artikel.setCurrentIndex(idx)
            lief = pre_artikel.get("lieferant","")
            if lief in lieferanten:
                self.cb_lieferant.setCurrentIndex(lieferanten.index(lief))

        # Menge
        self.sp_menge = QSpinBox()
        self.sp_menge.setRange(1, 99999)
        self.sp_menge.setValue(100)
        self.sp_menge.setFont(QFont("Segoe UI", 12))
        self.sp_menge.setFixedHeight(38)
        self.sp_menge.setStyleSheet("""
            QSpinBox { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }
        """)

        # Preis
        self.sp_preis = QDoubleSpinBox()
        self.sp_preis.setRange(0.01, 999999.99)
        self.sp_preis.setValue(100.00)
        self.sp_preis.setPrefix("€ ")
        self.sp_preis.setDecimals(2)
        self.sp_preis.setFont(QFont("Segoe UI", 12))
        self.sp_preis.setFixedHeight(38)
        self.sp_preis.setStyleSheet("""
            QDoubleSpinBox { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }
        """)
        if pre_artikel:
            self.sp_preis.setValue(pre_artikel.get("preis", 1.0) * 100)

        # Datum
        self.de_datum = QDateEdit()
        self.de_datum.setDate(QDate.currentDate())
        self.de_datum.setCalendarPopup(True)
        self.de_datum.setFont(QFont("Segoe UI", 12))
        self.de_datum.setFixedHeight(38)
        self.de_datum.setStyleSheet("""
            QDateEdit { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }
        """)

        # Status
        self.cb_status = styled_combo(["Unterwegs", "Ausstehend", "Anrufen", "Geliefert", "Storniert"])

        # Notizen
        self.te_notiz = QTextEdit()
        self.te_notiz.setPlaceholderText("Optionale Notizen zur Bestellung...")
        self.te_notiz.setFont(QFont("Segoe UI", 12))
        self.te_notiz.setFixedHeight(80)
        self.te_notiz.setStyleSheet("""
            QTextEdit { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:8px; }
        """)

        fl.addRow(label("Lieferant:", 12, bold=True, color=C_MUTED), self.cb_lieferant)
        fl.addRow(label("Artikel:", 12, bold=True, color=C_MUTED), self.cb_artikel)
        fl.addRow(label("Menge:", 12, bold=True, color=C_MUTED), self.sp_menge)
        fl.addRow(label("Gesamtbetrag:", 12, bold=True, color=C_MUTED), self.sp_preis)
        fl.addRow(label("Datum:", 12, bold=True, color=C_MUTED), self.de_datum)
        fl.addRow(label("Status:", 12, bold=True, color=C_MUTED), self.cb_status)
        fl.addRow(label("Notizen:", 12, bold=True, color=C_MUTED), self.te_notiz)
        lay.addWidget(c)

        # Buttons
        btn_row = QHBoxLayout()
        b_save = btn("💾 Bestellung speichern", C_GREEN)
        b_save.clicked.connect(self._save)
        b_pdf = btn("🖨 Speichern & PDF", C_BLUE)
        b_pdf.clicked.connect(lambda: self._save(print_pdf=True))
        b_cancel = btn("Abbrechen", bg="#e0e7f0", fg=C_TEXT)
        b_cancel.clicked.connect(self.reject)
        btn_row.addWidget(b_save)
        btn_row.addWidget(b_pdf)
        btn_row.addStretch()
        btn_row.addWidget(b_cancel)
        lay.addLayout(btn_row)

    def _save(self, print_pdf=False):
        new_id = f"#{len(APP_DATA['bestellungen'])+1:06d}"
        bestellung = {
            "id": new_id,
            "datum": self.de_datum.date().toString("yyyy-MM-dd"),
            "lieferant": self.cb_lieferant.currentText(),
            "artikel": self.cb_artikel.currentText(),
            "menge": self.sp_menge.value(),
            "status": self.cb_status.currentText(),
            "gesamt": round(self.sp_preis.value(), 2),
            "notiz": self.te_notiz.toPlainText(),
        }
        APP_DATA["bestellungen"].append(bestellung)
        save_data(APP_DATA)

        if print_pdf:
            generate_order_pdf(bestellung, self)
        else:
            QMessageBox.information(self, "Gespeichert",
                f"Bestellung {new_id} wurde erfolgreich gespeichert!")
        self.accept()


# ──────────────────────────────────────────────
# BESTELLUNG DETAIL DIALOG
# ──────────────────────────────────────────────
class BestellungDetailDialog(QDialog):
    def __init__(self, bestellung, parent=None):
        super().__init__(parent)
        self.bestellung = bestellung
        self.setWindowTitle(f"Bestelldetail – {bestellung['id']}")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background: {C_PAGE};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        lay.addWidget(label(f"Bestellung {bestellung['id']}", 18, bold=True))

        c = card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        status = bestellung.get("status", "–")
        status_colors = {
            "Unterwegs": ("#fff4e0", "#b86200"),
            "Geliefert": ("#e8faf2", "#1a8a52"),
            "Anrufen":   ("#ffeaea", "#c0392b"),
            "Ausstehend":("#e8f0ff", "#1a5dcf"),
            "Storniert": ("#f0f0f0", "#666"),
        }
        bg, fg = status_colors.get(status, ("#eee","#333"))

        fields = [
            ("Bestell-ID:", bestellung.get("id","–")),
            ("Datum:", bestellung.get("datum","–")),
            ("Lieferant:", bestellung.get("lieferant","–")),
            ("Artikel:", bestellung.get("artikel","–")),
            ("Menge:", str(bestellung.get("menge","–"))),
            ("Gesamtbetrag:", f"€ {bestellung.get('gesamt',0):.2f}"),
            ("Notizen:", bestellung.get("notiz","–") or "–"),
        ]
        for lbl, val in fields:
            fl.addRow(label(lbl, 12, bold=True, color=C_MUTED), label(val, 12))

        status_badge = badge(f"Status: {status}", bg, fg)
        status_badge.setFixedHeight(32)
        fl.addRow(label("Status:", 12, bold=True, color=C_MUTED), status_badge)
        lay.addWidget(c)

        # Buttons
        btn_row = QHBoxLayout()
        b_pdf = btn("🖨 Als PDF drucken", C_BLUE)
        b_pdf.clicked.connect(lambda: generate_order_pdf(bestellung, self))
        b_csv = btn("📊 CSV Export", C_GREEN)
        b_csv.clicked.connect(lambda: export_csv([bestellung],
            ["id","datum","lieferant","artikel","menge","status","gesamt"],
            f"Bestellung_{bestellung['id'].replace('#','')}", self))
        b_close = btn("Schließen", bg="#e0e7f0", fg=C_TEXT)
        b_close.clicked.connect(self.close)
        btn_row.addWidget(b_pdf)
        btn_row.addWidget(b_csv)
        btn_row.addStretch()
        btn_row.addWidget(b_close)
        lay.addLayout(btn_row)


# ──────────────────────────────────────────────
# TABLE HELPER
# ──────────────────────────────────────────────
def make_table(headers, rows, badge_cols=None):
    t = QTableWidget(len(rows), len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QTableWidget.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectRows)
    t.setAlternatingRowColors(False)
    t.verticalHeader().setVisible(False)
    t.setFocusPolicy(Qt.StrongFocus)
    t.setShowGrid(False)
    t.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    t.setStyleSheet("""
        QTableWidget {
            background: transparent;
            border: none;
            outline: none;
        }
        QHeaderView::section {
            background: transparent;
            color: #7b8ea9;
            font-size: 11px;
            font-weight: bold;
            border: none;
            padding: 4px 8px 8px 8px;
            border-bottom: 1px solid #d8e3f0;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #f0f4f8;
            color: #1a2a4a;
        }
        QTableWidget::item:selected {
            background: #e8f0ff;
            color: #1a2a4a;
        }
    """)
    badge_cols = badge_cols or {}
    for r, row in enumerate(rows):
        t.setRowHeight(r, 42)
        for c, val in enumerate(row):
            if c in badge_cols:
                bg, fg = badge_cols[c](val)
                cell_w = QWidget()
                hl = QHBoxLayout(cell_w)
                hl.setContentsMargins(4, 4, 4, 4)
                hl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                b = badge(val, bg, fg)
                hl.addWidget(b)
                hl.addStretch()
                t.setCellWidget(r, c, cell_w)
            else:
                item = QTableWidgetItem(str(val))
                item.setFont(QFont("Segoe UI", 12))
                if c == 0:
                    item.setFont(QFont("Segoe UI", 12, QFont.Medium))
                t.setItem(r, c, item)

    t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    total = sum(t.rowHeight(r) for r in range(len(rows)))
    t.setFixedHeight(total + t.horizontalHeader().height() + 4)
    return t


# ──────────────────────────────────────────────
# SUPPLIER CARD
# ──────────────────────────────────────────────
def supplier_card(title, suppliers):
    c = card()
    lay = QVBoxLayout(c)
    lay.setContentsMargins(20, 18, 20, 18)
    lay.setSpacing(0)

    hdr = QHBoxLayout()
    hdr.addWidget(label(title, 14, bold=True))
    hdr.addStretch()
    lay.addLayout(hdr)
    lay.addSpacing(10)

    for icon, name, sub, count in suppliers:
        row = QHBoxLayout()
        ico = QLabel(icon)
        ico.setFont(QFont("Segoe UI", 22))
        ico.setFixedSize(38, 38)
        ico.setAlignment(Qt.AlignCenter)
        ico.setStyleSheet("background: #f0f4ff; border-radius: 8px;")

        info = QVBoxLayout()
        info.setSpacing(1)
        info.addWidget(label(name, 12, bold=True))
        if sub:
            info.addWidget(label(sub, 10, color=C_MUTED))

        cnt = label(str(count), 16, bold=True)

        row.addWidget(ico)
        row.addSpacing(10)
        row.addLayout(info)
        row.addStretch()
        row.addWidget(cnt)

        frame = QFrame()
        frame.setStyleSheet("QFrame { border-bottom: 1px solid #f0f4f8; }")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(0, 8, 0, 8)
        fl.addLayout(row)
        lay.addWidget(frame)

    b = btn("Lieferanten verwalten", bg="transparent", fg=C_BLUE, radius=9)
    b.setStyleSheet(b.styleSheet() + f"QPushButton {{ border: 2px solid {C_BLUE}; }}")
    b.clicked.connect(lambda: QMessageBox.information(None, "Lieferanten", "Lieferantenverwaltung wird geöffnet."))
    lay.addSpacing(10)
    lay.addWidget(b)
    return c


# ──────────────────────────────────────────────
# DASHBOARD PAGE
# ──────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C_PAGE};")
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet(f"background: {C_PAGE};")
        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(20)

        root.addWidget(label("Dashboard", 22, bold=True))

        # KPI ROW
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_row.addWidget(KpiCard("Kritische MHDs", "47", "⚠", "#1a6bff", "#0d4fcf",
            on_click=lambda: QMessageBox.information(self, "MHDs", "47 Artikel mit kritischem MHD.\nBitte umgehend prüfen!")))
        kpi_row.addWidget(KpiCard("Fehlartikel (Regal leer)", "12", "🚚", "#ff8c00", "#e06b00",
            on_click=lambda: QMessageBox.information(self, "Fehlartikel", "12 Artikel mit leerem Regal.\nSofort nachbestellen!")))
        kpi_row.addWidget(KpiCard("Wareneingang Heute", "6", "📦", "#28c76f", "#1a9e55",
            on_click=lambda: QMessageBox.information(self, "Wareneingang", "6 Lieferungen heute eingegangen.")))
        root.addLayout(kpi_row)

        # MAIN GRID
        grid = QHBoxLayout()
        grid.setSpacing(20)
        grid.setAlignment(Qt.AlignTop)
        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        left_col.setAlignment(Qt.AlignTop)

        # Card 1 – Aktuelle Lieferungen
        c1 = card()
        c1l = QVBoxLayout(c1)
        c1l.setContentsMargins(20, 18, 20, 18)
        hdr1 = QHBoxLayout()
        hdr1.addWidget(label("Aktuelle Lieferungen", 14, bold=True))
        hdr1.addStretch()
        a_btn = QPushButton("›")
        a_btn.setFlat(True)
        a_btn.setFont(QFont("Segoe UI", 16))
        a_btn.setStyleSheet(f"color: {C_BLUE}; background: transparent; border: none;")
        a_btn.setCursor(Qt.PointingHandCursor)
        a_btn.clicked.connect(lambda: QMessageBox.information(self, "Lieferungen", "Alle aktuellen Lieferungen."))
        hdr1.addWidget(a_btn)
        c1l.addLayout(hdr1)

        def lief_badge(val):
            m = {"Verziegt": ("#e8faf2","#1a8a52"), "Berailget": ("#fff4e0","#b86200"), "Anrufen": ("#ffeaea","#c0392b")}
            return m.get(val, ("#eee","#333"))

        t1 = make_table(
            ["Lieferant", "Status", "Versendet"],
            [["Zentrallager (Kette Nord-West)", "", "Verziegt"],
             ["Lokaler Bauer (Milch & Eier)", "", "Berailget"],
             ["Getränke GmbH", "", "Anrufen"]],
            badge_cols={2: lief_badge}
        )
        c1l.addWidget(t1)
        left_col.addWidget(c1)

        # Card 2 – Bestellungen
        c2 = card()
        c2l = QVBoxLayout(c2)
        c2l.setContentsMargins(20, 18, 20, 18)
        hdr2 = QHBoxLayout()
        hdr2.addWidget(label("Aktuelle Bestellungen", 14, bold=True))
        hdr2.addStretch()
        new_order_btn = btn("+ Neue Bestellung", bg=C_GREEN, size=11)
        new_order_btn.setFixedHeight(32)
        new_order_btn.clicked.connect(lambda: self._neue_bestellung())
        hdr2.addWidget(new_order_btn)
        c2l.addLayout(hdr2)

        def status_badge(val):
            m = {"Unterwegs": ("#fff4e0","#b86200"), "Anrufen": ("#ffeaea","#c0392b"),
                 "Geliefert": ("#e8faf2","#1a8a52")}
            return m.get(val, ("#eee","#333"))

        # Build rows from data
        best_rows = [[b["id"], b["lieferant"], b["status"]] for b in APP_DATA["bestellungen"][:4]]
        t2 = make_table(["Order-ID", "Lieferant", "Status"], best_rows, badge_cols={2: status_badge})
        t2.cellDoubleClicked.connect(lambda r, c: self._open_bestellung_detail(r))
        c2l.addWidget(t2)
        c2l.addWidget(label("Doppelklick für Details", 10, color=C_MUTED))

        b2 = btn("Alle Bestellungen anzeigen")
        b2.clicked.connect(lambda: QMessageBox.information(self, "Bestellungen", "Wechseln Sie zur Bestellungsseite für die vollständige Übersicht."))
        c2l.addSpacing(10)
        c2l.addWidget(b2)
        left_col.addWidget(c2)

        # Card 3 – Lagerbestand & MHD
        c3 = card()
        c3l = QVBoxLayout(c3)
        c3l.setContentsMargins(20, 18, 20, 18)
        hdr3 = QHBoxLayout()
        hdr3.addWidget(label("Lagerbestand & MHD", 14, bold=True))
        hdr3.addStretch()
        csv_btn = btn("📊 CSV", bg=C_MUTED, size=11)
        csv_btn.setFixedHeight(30)
        csv_btn.clicked.connect(lambda: export_csv(APP_DATA["artikel"],
            ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"],
            "Lagerbestand", self))
        hdr3.addWidget(csv_btn)
        c3l.addLayout(hdr3)

        def mhd_badge(val):
            if "REDUZIEREN" in val:
                return ("#fff8e1","#a07000")
            if "Tage" in val:
                for part in val.split():
                    try:
                        num = int(part)
                        return ("#e8faf2","#1a8a52") if num >= 14 else ("#fff4e0","#b86200")
                    except ValueError:
                        continue
            return ("#ffeaea","#c0392b")

        for art in APP_DATA["artikel"][:3]:
            mhd_str = art["mhd"]
            try:
                mhd_date = datetime.datetime.strptime(mhd_str, "%Y-%m-%d").date()
                diff = (mhd_date - datetime.date.today()).days
                if diff < 3:
                    mhd_display = "⚡ REDUZIEREN"
                elif diff < 14:
                    mhd_display = f"⚠ {diff} Tage"
                else:
                    mhd_display = f"✅ {diff} Tage"
            except:
                mhd_display = mhd_str

            row_w = QWidget()
            row_w.setStyleSheet("border-bottom: 1px solid #f0f4f8;")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 8, 0, 8)
            rl.addWidget(label(art["name"], 12, bold=True))
            rl.addWidget(label(art["id"], 11, color=C_MUTED))
            rl.addStretch()
            bg, fg = mhd_badge(mhd_display)
            rl.addWidget(badge(mhd_display, bg, fg))
            rl.addSpacing(10)
            eb = btn("Detail", bg=C_BLUE, size=11)
            eb.setFixedHeight(28)
            eb.clicked.connect(lambda _, a=art: ArtikelDetailDialog(a, self).exec_())
            rl.addWidget(eb)
            c3l.addWidget(row_w)

        b3 = btn("Alle Artikel anzeigen")
        b3.clicked.connect(lambda: QMessageBox.information(self, "Lagerbestand", "Wechseln Sie zur Lagerbestandsseite."))
        c3l.addSpacing(10)
        c3l.addWidget(b3)
        left_col.addWidget(c3)
        left_col.addStretch()

        # RIGHT COLUMN
        right_col = QVBoxLayout()
        right_col.setSpacing(20)
        right_col.setAlignment(Qt.AlignTop)

        cc = card()
        cl = QVBoxLayout(cc)
        cl.setContentsMargins(20, 18, 20, 14)
        cl.addWidget(label("Bestandsübersicht", 14, bold=True))
        chart = LineChart()
        cl.addWidget(chart)
        legend_row = QHBoxLayout()
        for col, name in [(C_BLUE,"Lagerbestand"),(C_ORANGE,"Bestellungen"),(C_GREEN,"Einlagerungen")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{col}; background:transparent;")
            dot.setFont(QFont("Segoe UI", 14))
            legend_row.addWidget(dot)
            legend_row.addWidget(label(name, 10, color=C_MUTED))
            legend_row.addSpacing(8)
        legend_row.addStretch()
        cl.addLayout(legend_row)
        right_col.addWidget(cc)

        right_col.addWidget(supplier_card("Top Lieferanten", [
            ("🏭", "Zentrallager", "134 Lieferungen", 128),
            ("📦", "Pfandflaschen Paletten", "", 76),
        ]))

        right_col.addStretch()

        left_widget = QWidget()
        left_widget.setLayout(left_col)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        right_widget = QWidget()
        right_widget.setLayout(right_col)
        right_widget.setFixedWidth(330)

        grid.addWidget(left_widget)
        grid.addWidget(right_widget)
        root.addLayout(grid)

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _neue_bestellung(self):
        dlg = NeueBestellungDialog(parent=self)
        dlg.exec_()

    def _open_bestellung_detail(self, row):
        if row < len(APP_DATA["bestellungen"]):
            dlg = BestellungDetailDialog(APP_DATA["bestellungen"][row], self)
            dlg.exec_()


# ──────────────────────────────────────────────
# LAGERBESTAND PAGE
# ──────────────────────────────────────────────
class LagerbestandPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C_PAGE};")
        self._build()

    def _build(self):
        # Clear existing layout
        if self.layout():
            QWidget().setLayout(self.layout())

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet(f"background: {C_PAGE};")
        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        hdr.addWidget(label("📦 Lagerbestand", 22, bold=True))
        hdr.addStretch()
        b_new = btn("+ Neuer Artikel", bg=C_GREEN)
        b_new.clicked.connect(self._neuer_artikel)
        b_csv = btn("📊 CSV Export", bg=C_MUTED)
        b_csv.clicked.connect(lambda: export_csv(APP_DATA["artikel"],
            ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"],
            "Lagerbestand", self))
        hdr.addWidget(b_new)
        hdr.addWidget(b_csv)
        root.addLayout(hdr)

        # Search
        self.search_box = styled_input("🔍 Artikel suchen...")
        self.search_box.textChanged.connect(self._filter)
        root.addWidget(self.search_box)

        # Table card
        c = card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Kategorie", "Bestand", "Mindest", "Preis", "Lieferant", "Aktionen"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setStyleSheet("""
            QTableWidget { background: transparent; border: none; outline: none; }
            QHeaderView::section {
                background: transparent; color: #7b8ea9; font-weight: bold;
                border: none; padding: 6px 8px; border-bottom: 2px solid #d8e3f0;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #f0f4f8; color: #1a2a4a; }
            QTableWidget::item:selected { background: #e8f0ff; color: #1a2a4a; }
            QTableWidget::item:alternate { background: #f8fafd; }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 200)
        self.table.setMinimumHeight(400)
        cl.addWidget(self.table)
        root.addWidget(c)

        self._populate_table(APP_DATA["artikel"])
        scroll.setWidget(inner)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)

    def _populate_table(self, artikel_list):
        self.table.setRowCount(len(artikel_list))
        for r, art in enumerate(artikel_list):
            self.table.setRowHeight(r, 46)
            self.table.setItem(r, 0, QTableWidgetItem(art["id"]))
            self.table.setItem(r, 1, QTableWidgetItem(art["name"]))
            self.table.setItem(r, 2, QTableWidgetItem(art["kategorie"]))

            # Bestand with color
            bestand_item = QTableWidgetItem(str(art["bestand"]))
            if art["bestand"] < art["min_bestand"]:
                bestand_item.setForeground(QColor(C_RED))
                bestand_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            else:
                bestand_item.setForeground(QColor(C_GREEN))
            self.table.setItem(r, 3, bestand_item)

            self.table.setItem(r, 4, QTableWidgetItem(str(art["min_bestand"])))
            self.table.setItem(r, 5, QTableWidgetItem(f"€ {art['preis']:.2f}"))
            self.table.setItem(r, 6, QTableWidgetItem(art["lieferant"]))

            # Action buttons
            btn_w = QWidget()
            btn_lay = QHBoxLayout(btn_w)
            btn_lay.setContentsMargins(4, 2, 4, 2)
            btn_lay.setSpacing(4)

            b_detail = QPushButton("Detail")
            b_detail.setFont(QFont("Segoe UI", 10, QFont.Bold))
            b_detail.setFixedHeight(28)
            b_detail.setCursor(Qt.PointingHandCursor)
            b_detail.setStyleSheet(f"QPushButton {{ background:{C_BLUE}; color:white; border-radius:6px; padding:0 8px; border:none; }} QPushButton:hover {{ opacity:0.8; }}")
            b_detail.clicked.connect(lambda _, a=art: ArtikelDetailDialog(a, self).exec_())

            b_bestell = QPushButton("Bestellen")
            b_bestell.setFont(QFont("Segoe UI", 10, QFont.Bold))
            b_bestell.setFixedHeight(28)
            b_bestell.setCursor(Qt.PointingHandCursor)
            b_bestell.setStyleSheet(f"QPushButton {{ background:{C_GREEN}; color:white; border-radius:6px; padding:0 8px; border:none; }}")
            b_bestell.clicked.connect(lambda _, a=art: NeueBestellungDialog(pre_artikel=a, parent=self).exec_())

            btn_lay.addWidget(b_detail)
            btn_lay.addWidget(b_bestell)
            btn_lay.addStretch()
            self.table.setCellWidget(r, 7, btn_w)

    def _filter(self, text):
        filtered = [a for a in APP_DATA["artikel"]
                    if text.lower() in a["name"].lower() or text.lower() in a["id"].lower()]
        self._populate_table(filtered)

    def _neuer_artikel(self):
        dlg = NeuerArtikelDialog(self)
        if dlg.exec_():
            self._populate_table(APP_DATA["artikel"])


# ──────────────────────────────────────────────
# NEUER ARTIKEL DIALOG
# ──────────────────────────────────────────────
class NeuerArtikelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neuen Artikel anlegen")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"background: {C_PAGE};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        lay.addWidget(label("🏷 Neuer Artikel", 18, bold=True))

        c = card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        self.f_name = styled_input("Artikelname")
        self.f_id = styled_input("Artikel-ID (z.B. ABC123)")
        self.f_kat = styled_combo(["Molkereiprodukte","Getränke","Obst & Gemüse","Tiefkühlprodukte","Backwaren","Sonstiges"])
        self.f_bestand = QSpinBox(); self.f_bestand.setRange(0,99999); self.f_bestand.setFont(QFont("Segoe UI",12)); self.f_bestand.setFixedHeight(38)
        self.f_bestand.setStyleSheet("QSpinBox { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }")
        self.f_min = QSpinBox(); self.f_min.setRange(0,99999); self.f_min.setValue(20); self.f_min.setFont(QFont("Segoe UI",12)); self.f_min.setFixedHeight(38)
        self.f_min.setStyleSheet("QSpinBox { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }")
        self.f_preis = QDoubleSpinBox(); self.f_preis.setRange(0.01,99999); self.f_preis.setPrefix("€ "); self.f_preis.setDecimals(2); self.f_preis.setFont(QFont("Segoe UI",12)); self.f_preis.setFixedHeight(38)
        self.f_preis.setStyleSheet("QDoubleSpinBox { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }")
        lieferanten = [l["name"] for l in APP_DATA.get("lieferanten",[])]
        self.f_lief = styled_combo(lieferanten)
        self.f_mhd = QDateEdit(); self.f_mhd.setDate(QDate.currentDate().addDays(30)); self.f_mhd.setCalendarPopup(True); self.f_mhd.setFont(QFont("Segoe UI",12)); self.f_mhd.setFixedHeight(38)
        self.f_mhd.setStyleSheet("QDateEdit { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; }")

        fl.addRow(label("Name:", 12, bold=True, color=C_MUTED), self.f_name)
        fl.addRow(label("ID:", 12, bold=True, color=C_MUTED), self.f_id)
        fl.addRow(label("Kategorie:", 12, bold=True, color=C_MUTED), self.f_kat)
        fl.addRow(label("Bestand:", 12, bold=True, color=C_MUTED), self.f_bestand)
        fl.addRow(label("Mindestbestand:", 12, bold=True, color=C_MUTED), self.f_min)
        fl.addRow(label("Preis:", 12, bold=True, color=C_MUTED), self.f_preis)
        fl.addRow(label("Lieferant:", 12, bold=True, color=C_MUTED), self.f_lief)
        fl.addRow(label("MHD:", 12, bold=True, color=C_MUTED), self.f_mhd)
        lay.addWidget(c)

        btn_row = QHBoxLayout()
        b_save = btn("💾 Speichern", C_GREEN)
        b_save.clicked.connect(self._save)
        b_cancel = btn("Abbrechen", bg="#e0e7f0", fg=C_TEXT)
        b_cancel.clicked.connect(self.reject)
        btn_row.addWidget(b_save)
        btn_row.addStretch()
        btn_row.addWidget(b_cancel)
        lay.addLayout(btn_row)

    def _save(self):
        if not self.f_name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Artikelname eingeben!")
            return
        if not self.f_id.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Artikel-ID eingeben!")
            return
        new_art = {
            "id": self.f_id.text().strip(),
            "name": self.f_name.text().strip(),
            "kategorie": self.f_kat.currentText(),
            "bestand": self.f_bestand.value(),
            "min_bestand": self.f_min.value(),
            "preis": self.f_preis.value(),
            "lieferant": self.f_lief.currentText(),
            "mhd": self.f_mhd.date().toString("yyyy-MM-dd"),
        }
        APP_DATA["artikel"].append(new_art)
        save_data(APP_DATA)
        QMessageBox.information(self, "Gespeichert", f"Artikel '{new_art['name']}' wurde angelegt!")
        self.accept()


# ──────────────────────────────────────────────
# BESTELLUNGEN PAGE
# ──────────────────────────────────────────────
class BestellungenPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C_PAGE};")
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet(f"background: {C_PAGE};")
        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        hdr.addWidget(label("🛒 Bestellungen", 22, bold=True))
        hdr.addStretch()
        b_new = btn("+ Neue Bestellung", bg=C_GREEN)
        b_new.clicked.connect(self._neue_bestellung)
        b_csv = btn("📊 CSV Export", bg=C_MUTED)
        b_csv.clicked.connect(lambda: export_csv(APP_DATA["bestellungen"],
            ["id","datum","lieferant","artikel","menge","status","gesamt"],
            "Bestellungen", self))
        hdr.addWidget(b_new)
        hdr.addWidget(b_csv)
        root.addLayout(hdr)

        # Filter
        filter_row = QHBoxLayout()
        self.search_b = styled_input("🔍 Bestell-ID oder Lieferant suchen...")
        self.search_b.textChanged.connect(self._filter)
        self.status_filter = styled_combo(["Alle Status", "Unterwegs", "Ausstehend", "Geliefert", "Anrufen", "Storniert"])
        self.status_filter.currentTextChanged.connect(self._filter)
        filter_row.addWidget(self.search_b, 2)
        filter_row.addWidget(self.status_filter, 1)
        root.addLayout(filter_row)

        # Table card
        c = card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Datum", "Lieferant", "Artikel", "Menge", "Gesamt", "Status", "Aktionen"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setMinimumHeight(400)
        self.table.setStyleSheet("""
            QTableWidget { background: transparent; border: none; outline: none; }
            QHeaderView::section {
                background: transparent; color: #7b8ea9; font-weight: bold;
                border: none; padding: 6px 8px; border-bottom: 2px solid #d8e3f0;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #f0f4f8; color: #1a2a4a; }
            QTableWidget::item:selected { background: #e8f0ff; color: #1a2a4a; }
            QTableWidget::item:alternate { background: #f8fafd; }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 200)
        cl.addWidget(self.table)
        root.addWidget(c)

        self._populate_table(APP_DATA["bestellungen"])
        scroll.setWidget(inner)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)

    def _populate_table(self, data):
        self.table.setRowCount(len(data))
        status_colors = {
            "Unterwegs": ("#fff4e0","#b86200"),
            "Geliefert": ("#e8faf2","#1a8a52"),
            "Anrufen":   ("#ffeaea","#c0392b"),
            "Ausstehend":("#e8f0ff","#1a5dcf"),
            "Storniert": ("#f0f0f0","#666"),
        }
        for r, b_data in enumerate(data):
            self.table.setRowHeight(r, 46)
            self.table.setItem(r, 0, QTableWidgetItem(b_data.get("id","–")))
            self.table.setItem(r, 1, QTableWidgetItem(b_data.get("datum","–")))
            self.table.setItem(r, 2, QTableWidgetItem(b_data.get("lieferant","–")))
            self.table.setItem(r, 3, QTableWidgetItem(b_data.get("artikel","–")))
            self.table.setItem(r, 4, QTableWidgetItem(str(b_data.get("menge","–"))))
            self.table.setItem(r, 5, QTableWidgetItem(f"€ {b_data.get('gesamt',0):.2f}"))

            # Status badge
            status = b_data.get("status","–")
            bg, fg = status_colors.get(status, ("#eee","#333"))
            cell_w = QWidget()
            hl = QHBoxLayout(cell_w)
            hl.setContentsMargins(4,4,4,4)
            hl.addWidget(badge(status, bg, fg))
            hl.addStretch()
            self.table.setCellWidget(r, 6, cell_w)

            # Action buttons
            btn_w = QWidget()
            btn_lay = QHBoxLayout(btn_w)
            btn_lay.setContentsMargins(4,2,4,2)
            btn_lay.setSpacing(4)

            b_detail = QPushButton("Detail")
            b_detail.setFont(QFont("Segoe UI", 10, QFont.Bold))
            b_detail.setFixedHeight(28)
            b_detail.setCursor(Qt.PointingHandCursor)
            b_detail.setStyleSheet(f"QPushButton {{background:{C_BLUE};color:white;border-radius:6px;padding:0 8px;border:none;}}")
            b_detail.clicked.connect(lambda _, d=b_data: BestellungDetailDialog(d, self).exec_())

            b_pdf = QPushButton("🖨 PDF")
            b_pdf.setFont(QFont("Segoe UI", 10, QFont.Bold))
            b_pdf.setFixedHeight(28)
            b_pdf.setCursor(Qt.PointingHandCursor)
            b_pdf.setStyleSheet(f"QPushButton {{background:{C_ORANGE};color:white;border-radius:6px;padding:0 8px;border:none;}}")
            b_pdf.clicked.connect(lambda _, d=b_data: generate_order_pdf(d, self))

            btn_lay.addWidget(b_detail)
            btn_lay.addWidget(b_pdf)
            btn_lay.addStretch()
            self.table.setCellWidget(r, 7, btn_w)

    def _filter(self):
        text = self.search_b.text().lower()
        status_f = self.status_filter.currentText()
        filtered = [b for b in APP_DATA["bestellungen"]
                    if (text in b.get("id","").lower() or text in b.get("lieferant","").lower() or text in b.get("artikel","").lower())
                    and (status_f == "Alle Status" or b.get("status","") == status_f)]
        self._populate_table(filtered)

    def _neue_bestellung(self):
        dlg = NeueBestellungDialog(parent=self)
        if dlg.exec_():
            self._populate_table(APP_DATA["bestellungen"])


# ──────────────────────────────────────────────
# NAV BUTTON
# ──────────────────────────────────────────────
class NavButton(QPushButton):
    def __init__(self, icon_char, text, active=False, parent=None):
        super().__init__(parent)
        self.active = active
        self.setText(f"  {icon_char}  {text}")
        self.setFont(QFont("Segoe UI", 13))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._apply_style()

    def _apply_style(self):
        if self.active:
            self.setStyleSheet("""
                QPushButton {
                    background: #1e4080; color: white; border: none;
                    border-left: 3px solid #1a6bff;
                    text-align: left; padding-left: 14px; border-radius: 0px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent; color: rgba(255,255,255,160);
                    border: none; border-left: 3px solid transparent;
                    text-align: left; padding-left: 14px; border-radius: 0px;
                }
                QPushButton:hover { background: #122a52; color: white; }
                QPushButton:pressed { background: #1e4080; }
            """)


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
class Sidebar(GradientWidget):
    def __init__(self, on_nav, parent=None):
        super().__init__(C_SIDEBAR, C_SIDEBAR_DARK, radius=0, parent=parent)
        self.setFixedWidth(210)
        self.on_nav = on_nav
        self.nav_buttons = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        logo_w = QWidget()
        logo_w.setFixedHeight(80)
        logo_w.setStyleSheet("background: transparent;")
        ll = QHBoxLayout(logo_w)
        ll.setContentsMargins(12, 10, 12, 10)

        robot = QLabel("🤖")
        robot.setFont(QFont("Segoe UI", 30))
        robot.setStyleSheet("background: transparent;")

        txt_w = QWidget()
        txt_w.setStyleSheet("background: transparent;")
        tv = QVBoxLayout(txt_w)
        tv.setContentsMargins(0, 0, 0, 0)
        tv.setSpacing(0)
        name = QLabel('<span style="color:#5bc8ff">LAGER</span><span style="color:#ffb830">PRO</span>')
        name.setFont(QFont("Segoe UI", 15, QFont.Black))
        name.setTextFormat(Qt.RichText)
        name.setStyleSheet("background: transparent;")
        sub = QLabel("SOFTWARE ⚙")
        sub.setFont(QFont("Segoe UI", 8))
        sub.setStyleSheet("color: rgba(255,255,255,100); background: transparent; letter-spacing: 2px;")
        tv.addWidget(name)
        tv.addWidget(sub)

        ll.addWidget(robot)
        ll.addWidget(txt_w)
        root.addWidget(logo_w)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: rgba(255,255,255,30);")
        root.addWidget(sep)

        nav_items = [
            ("🏠", "Dashboard",         0),
            ("📦", "Lagerbestand",      1),
            ("🛒", "Bestellungen",       2),
            ("🏷", "Artikelverwaltung",  3),
            ("✅", "Bestätigung",         4),
            ("📋", "Artikelliste",        5),
            ("🏭", "Lieferanten",        6),
            ("📊", "Berichte",            7),
            ("⚙",  "Einstellungen",      8),
        ]

        for icon, text, idx in nav_items:
            b = NavButton(icon, text, active=(idx == 0))
            b.clicked.connect(lambda checked, i=idx, nm=text: self._nav_click(i, nm))
            self.nav_buttons.append(b)
            root.addWidget(b)

        root.addStretch()

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: rgba(255,255,255,30);")
        root.addWidget(sep2)

        user_w = QWidget()
        user_w.setStyleSheet("background: transparent;")
        ulay = QVBoxLayout(user_w)
        ulay.setContentsMargins(16, 12, 16, 12)
        ulay.setAlignment(Qt.AlignCenter)

        avatar = QLabel("👤")
        avatar.setFont(QFont("Segoe UI", 28))
        avatar.setStyleSheet("background: transparent;")
        avatar.setAlignment(Qt.AlignCenter)

        uname = QLabel("Max Mustermann")
        uname.setFont(QFont("Segoe UI", 12, QFont.Bold))
        uname.setStyleSheet("color: white; background: transparent;")
        uname.setAlignment(Qt.AlignCenter)

        urole = QLabel("Admin")
        urole.setFont(QFont("Segoe UI", 10))
        urole.setStyleSheet("color: rgba(255,255,255,120); background: transparent;")
        urole.setAlignment(Qt.AlignCenter)

        logout_btn = btn("⬛ LOGOUT", bg=C_ORANGE)
        logout_btn.clicked.connect(self._logout)
        logout_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        ulay.addWidget(avatar)
        ulay.addWidget(uname)
        ulay.addWidget(urole)
        ulay.addSpacing(6)
        ulay.addWidget(logout_btn)
        root.addWidget(user_w)

    def _nav_click(self, idx, name):
        for i, b in enumerate(self.nav_buttons):
            b.active = (i == idx)
            b._apply_style()
        self.on_nav(idx, name)

    def _logout(self):
        reply = QMessageBox.question(self, "Abmelden",
            "Möchten Sie sich wirklich abmelden?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()


# ──────────────────────────────────────────────
# TOPBAR
# ──────────────────────────────────────────────
class Topbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QFrame { background: white; border-bottom: 1px solid #d8e3f0; }
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(12)

        search = QLineEdit()
        search.setPlaceholderText("🔍  Suchen...")
        search.setFont(QFont("Segoe UI", 12))
        search.setFixedHeight(36)
        search.setMaximumWidth(380)
        search.setStyleSheet("""
            QLineEdit { background: #eef2f9; border: 1px solid #d8e3f0; border-radius: 10px; padding: 0 14px; color: #1a2a4a; }
            QLineEdit:focus { border: 1.5px solid #1a6bff; }
        """)
        lay.addWidget(search)
        lay.addStretch()

        for icon, tip in [("🔔", "Benachrichtigungen"), ("✉", "Nachrichten")]:
            b = QPushButton(icon)
            b.setToolTip(tip)
            b.setFont(QFont("Segoe UI", 14))
            b.setFixedSize(38, 38)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton { background: #eef2f9; border: 1px solid #d8e3f0; border-radius: 10px; }
                QPushButton:hover { background: #dce6f5; }
            """)
            lay.addWidget(b)

        user_chip = QPushButton("👤  Max Mustermann  (Admin)")
        user_chip.setFont(QFont("Segoe UI", 11))
        user_chip.setFixedHeight(38)
        user_chip.setCursor(Qt.PointingHandCursor)
        user_chip.setStyleSheet("""
            QPushButton { background: #eef2f9; border: 1px solid #d8e3f0; border-radius: 10px; padding: 0 14px; color: #1a2a4a; }
            QPushButton:hover { background: #dce6f5; }
        """)
        user_chip.clicked.connect(lambda: QMessageBox.information(None, "Profil", "Profil von Max Mustermann (Admin)"))
        lay.addWidget(user_chip)


# ──────────────────────────────────────────────
# BERICHTE PAGE (mit CSV Export)
# ──────────────────────────────────────────────
class BerichtePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C_PAGE};")

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet(f"background: {C_PAGE};")
        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(20)

        root.addWidget(label("📊 Berichte & Exports", 22, bold=True))

        # Export cards
        exports = [
            ("📦 Lagerbestand exportieren", "Alle Artikel mit Bestand, MHD und Preisen", C_BLUE,
             lambda: export_csv(APP_DATA["artikel"], ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"], "Lagerbestand", self)),
            ("🛒 Bestellungen exportieren", "Alle Bestellungen mit Status und Beträgen", C_GREEN,
             lambda: export_csv(APP_DATA["bestellungen"], ["id","datum","lieferant","artikel","menge","status","gesamt"], "Bestellungen", self)),
            ("🏭 Lieferanten exportieren", "Alle Lieferanten mit Kontaktdaten", C_ORANGE,
             lambda: export_csv(APP_DATA["lieferanten"], ["name","kontakt","telefon","lieferungen"], "Lieferanten", self)),
            ("⚠ Kritische Artikel exportieren", "Artikel unter Mindestbestand", C_RED,
             lambda: export_csv(
                [a for a in APP_DATA["artikel"] if a["bestand"] < a["min_bestand"]],
                ["id","name","bestand","min_bestand","lieferant"], "Kritische_Artikel", self)),
        ]

        for exp_title, exp_desc, exp_color, exp_fn in exports:
            c = card()
            cl = QHBoxLayout(c)
            cl.setContentsMargins(20, 16, 20, 16)

            info = QVBoxLayout()
            info.addWidget(label(exp_title, 14, bold=True))
            info.addWidget(label(exp_desc, 11, color=C_MUTED))

            b = btn("📊 CSV herunterladen", bg=exp_color)
            b.setFixedWidth(200)
            b.clicked.connect(exp_fn)

            cl.addLayout(info)
            cl.addStretch()
            cl.addWidget(b)
            root.addWidget(c)

        # Stats
        stat_c = card()
        stat_l = QVBoxLayout(stat_c)
        stat_l.setContentsMargins(20, 18, 20, 18)
        stat_l.addWidget(label("📈 Statistiken", 14, bold=True))
        stat_l.addSpacing(10)

        total_bestand = sum(a["bestand"] for a in APP_DATA["artikel"])
        krit = sum(1 for a in APP_DATA["artikel"] if a["bestand"] < a["min_bestand"])
        total_best = len(APP_DATA["bestellungen"])
        gesamt_wert = sum(b.get("gesamt",0) for b in APP_DATA["bestellungen"])

        stats = [
            ("Gesamtartikel", str(len(APP_DATA["artikel"])), C_BLUE),
            ("Gesamtbestand", str(total_bestand), C_GREEN),
            ("Kritische Artikel", str(krit), C_RED),
            ("Bestellungen gesamt", str(total_best), C_ORANGE),
            ("Bestellwert gesamt", f"€ {gesamt_wert:.2f}", C_BLUE),
        ]

        stat_row = QHBoxLayout()
        for stat_name, stat_val, stat_col in stats:
            stat_card = card()
            shadow(stat_card, blur=8)
            scl = QVBoxLayout(stat_card)
            scl.setContentsMargins(16, 12, 16, 12)
            v = label(stat_val, 22, bold=True, color=stat_col)
            n = label(stat_name, 10, color=C_MUTED)
            scl.addWidget(v)
            scl.addWidget(n)
            stat_row.addWidget(stat_card)

        stat_l.addLayout(stat_row)
        root.addWidget(stat_c)
        root.addStretch()

        scroll.setWidget(inner)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)


# ──────────────────────────────────────────────
# PLACEHOLDER PAGE
# ──────────────────────────────────────────────
class PlaceholderPage(QWidget):
    def __init__(self, title, icon="📄", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C_PAGE};")
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        ico = QLabel(icon)
        ico.setFont(QFont("Segoe UI", 64))
        ico.setAlignment(Qt.AlignCenter)
        ico.setStyleSheet("background: transparent;")
        t = label(title, 24, bold=True)
        t.setAlignment(Qt.AlignCenter)
        s = label("Diese Seite ist im Aufbau.", 14, color=C_MUTED)
        s.setAlignment(Qt.AlignCenter)
        lay.addWidget(ico)
        lay.addWidget(t)
        lay.addWidget(s)


# ──────────────────────────────────────────────
# MAIN WINDOW
# ──────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LagerPro Software")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        self.stack = QStackedWidget()

        # Create real pages for main sections
        self.dashboard_page = DashboardPage()
        self.lager_page = LagerbestandPage()
        self.bestellungen_page = BestellungenPage()
        self.berichte_page = BerichtePage()

        page_configs = [
            ("Dashboard",        "🏠", self.dashboard_page),
            ("Lagerbestand",     "📦", self.lager_page),
            ("Bestellungen",     "🛒", self.bestellungen_page),
            ("Artikelverwaltung","🏷", None),
            ("Bestätigung",       "✅", None),
            ("Artikelliste",      "📋", None),
            ("Lieferanten",      "🏭", None),
            ("Berichte",          "📊", self.berichte_page),
            ("Einstellungen",    "⚙", None),
        ]

        for title, icon, page in page_configs:
            if page is not None:
                self.stack.addWidget(page)
            else:
                self.stack.addWidget(PlaceholderPage(title, icon))

        sidebar = Sidebar(self._navigate)
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)
        right_lay.addWidget(Topbar())
        right_lay.addWidget(self.stack)

        main_lay.addWidget(sidebar)
        main_lay.addWidget(right)

    def _navigate(self, idx, name):
        self.stack.setCurrentIndex(idx)


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    f = QFont("Segoe UI", 12)
    app.setFont(f)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())