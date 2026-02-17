"""
LagerPro Software – PyQt5 Dashboard
====================================
Installation:
    pip install PyQt5

Ausführen:
    python lagerpro_app.py
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy, QStackedWidget,
    QLineEdit, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect
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
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {bg}, stop:1 #0d4fcf);
            opacity: 0.9;
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


# ──────────────────────────────────────────────
# GRADIENT WIDGET  (for KPI cards + sidebar)
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
        path.addRoundedRect(0, 0, self.width(), self.height(),
                            self.radius, self.radius)
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

        # grid
        p.setPen(QPen(QColor("#f0f4f8"), 1))
        for i in range(5):
            yy = pad_t + i * ch // 4
            p.drawLine(pad_l, yy, W - pad_r, yy)

        # y-axis labels
        y_labels = ["12k", "3k", "2k", "1k", "0"]
        p.setPen(QPen(QColor(C_MUTED)))
        p.setFont(QFont("Segoe UI", 8))
        for i, yl in enumerate(y_labels):
            yy = pad_t + i * ch // 4
            p.drawText(0, yy + 4, 30, 14, Qt.AlignRight, yl)

        # fill areas
        def draw_area(series, color):
            pts = [to_px(i, v) for i, v in enumerate(series)]
            path = QPainterPath()
            path.moveTo(pts[0][0], pts[0][1])
            for x, y in pts[1:]:
                path.lineTo(x, y)
            path.lineTo(pts[-1][0], H - pad_b)
            path.lineTo(pts[0][0],  H - pad_b)
            path.closeSubpath()
            c = QColor(color)
            c.setAlpha(40)
            p.fillPath(path, QBrush(c))

        draw_area(self.series1, C_BLUE)
        draw_area(self.series2, C_GREEN)

        # lines + dots
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

        # x-axis labels
        p.setPen(QPen(QColor(C_MUTED)))
        p.setFont(QFont("Segoe UI", 8))
        for i, xl in enumerate(self.labels):
            x = pad_l + i * cw // (len(self.labels) - 1) - 10
            p.drawText(x, H - pad_b + 6, 24, 16, Qt.AlignCenter, xl)


# ──────────────────────────────────────────────
# KPI CARD
# ──────────────────────────────────────────────
class KpiCard(GradientWidget):
    def __init__(self, title, value, icon_char, c1, c2, parent=None):
        super().__init__(c1, c2, parent=parent)
        self.setFixedHeight(100)
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
        QMessageBox.information(self, "KPI Details", "Detailansicht wird geöffnet...")


# ──────────────────────────────────────────────
# SIDEBAR NAV BUTTON
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
                    background: #1e4080;
                    color: white;
                    border: none;
                    border-left: 3px solid #1a6bff;
                    text-align: left;
                    padding-left: 14px;
                    border-radius: 0px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: rgba(255,255,255,160);
                    border: none;
                    border-left: 3px solid transparent;
                    text-align: left;
                    padding-left: 14px;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background: #122a52;
                    color: white;
                }
                QPushButton:pressed {
                    background: #1e4080;
                }
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

        # Logo area
        logo_w = QWidget()
        logo_w.setFixedHeight(80)
        logo_w.setStyleSheet("background: transparent;")
        ll = QHBoxLayout(logo_w)
        ll.setContentsMargins(12, 10, 12, 10)

        # Robot icon (simple unicode fallback)
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

        # Navigation items
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

        # User area
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
            QFrame {
                background: white;
                border-bottom: 1px solid #d8e3f0;
            }
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(12)

        # Search
        search = QLineEdit()
        search.setPlaceholderText("🔍  Suchen...")
        search.setFont(QFont("Segoe UI", 12))
        search.setFixedHeight(36)
        search.setMaximumWidth(380)
        search.setStyleSheet("""
            QLineEdit {
                background: #eef2f9;
                border: 1px solid #d8e3f0;
                border-radius: 10px;
                padding: 0 14px;
                color: #1a2a4a;
            }
            QLineEdit:focus {
                border: 1.5px solid #1a6bff;
            }
        """)
        lay.addWidget(search)
        lay.addStretch()

        # Icon buttons
        for icon, tip in [("🔔", "Benachrichtigungen"), ("✉", "Nachrichten")]:
            b = QPushButton(icon)
            b.setToolTip(tip)
            b.setFont(QFont("Segoe UI", 14))
            b.setFixedSize(38, 38)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton {
                    background: #eef2f9;
                    border: 1px solid #d8e3f0;
                    border-radius: 10px;
                }
                QPushButton:hover { background: #dce6f5; }
            """)
            b.clicked.connect(lambda _, t=tip: QMessageBox.information(None, t, f"{t} werden angezeigt."))
            lay.addWidget(b)

        # User chip
        user_chip = QPushButton("👤  Max Mustermann  (Admin)")
        user_chip.setFont(QFont("Segoe UI", 11))
        user_chip.setFixedHeight(38)
        user_chip.setCursor(Qt.PointingHandCursor)
        user_chip.setStyleSheet("""
            QPushButton {
                background: #eef2f9;
                border: 1px solid #d8e3f0;
                border-radius: 10px;
                padding: 0 14px;
                color: #1a2a4a;
            }
            QPushButton:hover { background: #dce6f5; }
        """)
        user_chip.clicked.connect(lambda: QMessageBox.information(None, "Profil", "Profil von Max Mustermann (Admin)"))
        lay.addWidget(user_chip)


# ──────────────────────────────────────────────
# TABLE HELPER
# ──────────────────────────────────────────────
def make_table(headers, rows, badge_cols=None):
    """Create a styled QTableWidget. badge_cols = {col_index: (bg, fg)} for badge styling."""
    t = QTableWidget(len(rows), len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QTableWidget.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectRows)
    t.setAlternatingRowColors(False)
    t.verticalHeader().setVisible(False)
    t.setFocusPolicy(Qt.NoFocus)
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
            text-transform: uppercase;
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

    # Auto height
    total = sum(t.rowHeight(r) for r in range(len(rows)))
    t.setFixedHeight(total + t.horizontalHeader().height() + 4)
    return t


# ──────────────────────────────────────────────
# SUPPLIER CARD
# ──────────────────────────────────────────────
def supplier_card(title, suppliers):
    """suppliers = [(emoji, name, sub, count), ...]"""
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
    b.setStyleSheet(b.styleSheet() + f"""
        QPushButton {{
            border: 2px solid {C_BLUE};
        }}
    """)
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

        # Title
        root.addWidget(label("Dashboard", 22, bold=True))

        # ── KPI ROW ──
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_row.addWidget(KpiCard("Kritische MHDs", "47", "⚠", "#1a6bff", "#0d4fcf"))
        kpi_row.addWidget(KpiCard("Fehlartikel (Regal leer)", "12", "🚚", "#ff8c00", "#e06b00"))
        kpi_row.addWidget(KpiCard("Wareneingang Heute", "6", "📦", "#28c76f", "#1a9e55"))
        root.addLayout(kpi_row)

        # ── MAIN GRID: left | right ──
        grid = QHBoxLayout()
        grid.setSpacing(20)
        grid.setAlignment(Qt.AlignTop)

        # LEFT column
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
            m = {"Verziegt": ("#e8faf2", "#1a8a52"), "Berailget": ("#fff4e0", "#b86200"), "Anrufen": ("#ffeaea", "#c0392b")}
            return m.get(val, ("#eee", "#333"))

        t1 = make_table(
            ["Lieferant", "Status", "Versendet"],
            [
                ["Zentrallager (Ketie Nord-Wet)", "", "Verziegt"],
                ["Lokaler Bauer (Milch & Eirr)", "", "Berailget"],
                ["Getränke GmbH", "", "Anrufen"],
            ],
            badge_cols={2: lief_badge}
        )
        c1l.addWidget(t1)
        left_col.addWidget(c1)

        # Card 2 – Bestellungen
        c2 = card()
        c2l = QVBoxLayout(c2)
        c2l.setContentsMargins(20, 18, 20, 18)
        c2l.addWidget(label("Artikelname / Bestellungen", 14, bold=True))

        def status_badge(val):
            m = {"Unterwegs": ("#fff4e0", "#b86200"), "Anrufen": ("#ffeaea", "#c0392b")}
            return m.get(val, ("#eee", "#333"))

        t2 = make_table(
            ["Order-ID", "Lieferant", "Status"],
            [
                ["#567213", "Lokaler Bauer", "Unterwegs"],
                ["#567132", "Obst & Gemüse", "Unterwegs"],
                ["#567099", "Pfandflaschen", "Anrufen"],
            ],
            badge_cols={2: status_badge}
        )
        c2l.addWidget(t2)
        b2 = btn("Alle Bestellungen anzeigen")
        b2.clicked.connect(lambda: QMessageBox.information(self, "Bestellungen", "Vollständige Bestellübersicht wird geladen."))
        c2l.addSpacing(10)
        c2l.addWidget(b2)
        left_col.addWidget(c2)

        # Card 3 – Lagerbestand & MHD (with action buttons)
        c3 = card()
        c3l = QVBoxLayout(c3)
        c3l.setContentsMargins(20, 18, 20, 18)
        c3l.addWidget(label("Lagerbestand & MHD", 14, bold=True))

        def mhd_badge(val):
            if "REDUZIEREN" in val:
                return ("#fff8e1", "#a07000")
            if "Tage" in val:
                # extract first numeric token, skip emojis/symbols
                for part in val.split():
                    try:
                        num = int(part)
                        return ("#e8faf2", "#1a8a52") if num >= 14 else ("#fff4e0", "#b86200")
                    except ValueError:
                        continue
                return ("#e8faf2", "#1a8a52")
            return ("#ffeaea", "#c0392b")

        mhd_data = [
            ("Bio Julh 1L",  "ABC123", "✅ 14 Tage"),
            ("H-Mil12",      "ASE476", "✅ 45 Tage"),
            ("H-Milll",      "NE1789", "⚡ REDUZIEREN"),
        ]

        for art, sku, mhd in mhd_data:
            row_w = QWidget()
            row_w.setStyleSheet("border-bottom: 1px solid #f0f4f8;")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 8, 0, 8)
            rl.addWidget(label(art, 12, bold=True))
            rl.addWidget(label(sku, 11, color=C_MUTED))
            rl.addStretch()
            bg, fg = mhd_badge(mhd)
            rl.addWidget(badge(mhd, bg, fg))
            rl.addSpacing(10)
            eb = btn("Bearbeiten", bg=C_BLUE, size=11)
            eb.setFixedHeight(28)
            eb.clicked.connect(lambda _, a=art: QMessageBox.information(self, "Bearbeiten", f"Artikel '{a}' wird bearbeitet."))
            rl.addWidget(eb)
            c3l.addWidget(row_w)

        b3 = btn("Alle Bestellungen anzeigen")
        b3.clicked.connect(lambda: QMessageBox.information(self, "Lagerbestand", "Vollständige Lagerbestandsübersicht."))
        c3l.addSpacing(10)
        c3l.addWidget(b3)
        left_col.addWidget(c3)

        # Card 4 – second inventory table
        c4 = card()
        c4l = QVBoxLayout(c4)
        c4l.setContentsMargins(20, 18, 20, 18)
        c4l.addWidget(label("Lagerbestand & MHD (Detail)", 14, bold=True))

        inv2 = [
            ("BICTVy1L",        "ABC133", "450 Tams",  "Bearbeiten", C_BLUE),
            ("TK Pizza Salami",  "DEF446", "120 Talns", "2 Tage",    C_GREEN),
            ("Tomaton",          "CH1799", "20 Tag",    "ENTSTEUERN", C_RED),
        ]
        for name_, sku, stock, action, color in inv2:
            row_w = QWidget()
            row_w.setStyleSheet("border-bottom: 1px solid #f0f4f8;")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 8, 0, 8)
            rl.addWidget(label(name_, 12, bold=True))
            rl.addWidget(label(sku, 11, color=C_MUTED))
            rl.addWidget(label(stock, 11, color=C_MUTED))
            rl.addStretch()
            eb = btn(action, bg=color, size=11)
            eb.setFixedHeight(28)
            eb.clicked.connect(lambda _, n=name_, a=action: QMessageBox.information(self, a, f"Aktion '{a}' für Artikel '{n}'."))
            rl.addWidget(eb)
            c4l.addWidget(row_w)

        b4 = btn("Alle Bestellungen anzeigen")
        b4.clicked.connect(lambda: QMessageBox.information(self, "Inventar", "Vollständige Inventarübersicht."))
        c4l.addSpacing(10)
        c4l.addWidget(b4)
        left_col.addWidget(c4)
        left_col.addStretch()

        # RIGHT column
        right_col = QVBoxLayout()
        right_col.setSpacing(20)
        right_col.setAlignment(Qt.AlignTop)

        # Chart card
        cc = card()
        cl = QVBoxLayout(cc)
        cl.setContentsMargins(20, 18, 20, 14)
        cl.addWidget(label("BestandsÜbersicht", 14, bold=True))
        chart = LineChart()
        cl.addWidget(chart)

        legend_row = QHBoxLayout()
        for col, name in [(C_BLUE, "Lagerbestand"), (C_ORANGE, "Bestellungen"), (C_GREEN, "Einlagerungen")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {col}; background: transparent;")
            dot.setFont(QFont("Segoe UI", 14))
            legend_row.addWidget(dot)
            legend_row.addWidget(label(name, 10, color=C_MUTED))
            legend_row.addSpacing(8)
        legend_row.addStretch()
        cl.addLayout(legend_row)
        right_col.addWidget(cc)

        # Supplier cards
        right_col.addWidget(supplier_card("Top Lieferanten", [
            ("🏭", "Zentrallager",         "134 Lieferungen", 128),
            ("📦", "Pfandflaschen Paletten","",                 76),
        ]))

        right_col.addWidget(supplier_card("Top Lieferanten", [
            ("🏭", "Zentrallager",   "135 Lieferungen", 128),
            ("🌱", "Lokale Erzeuger","121 Lieferungen", 915),
            ("🏪", "Gerlah GmbH",    "181 Lieferungen",  76),
        ]))

        right_col.addStretch()

        # Assemble grid
        left_widget = QWidget()
        left_widget.setLayout(left_col)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        right_widget = QWidget()
        right_widget.setLayout(right_col)
        right_widget.setFixedWidth(330)
        right_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        grid.addWidget(left_widget)
        grid.addWidget(right_widget)
        root.addLayout(grid)

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


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

        # Pages
        self.stack = QStackedWidget()
        page_configs = [
            ("Dashboard",        "🏠"),
            ("Lagerbestand",     "📦"),
            ("Bestellungen",     "🛒"),
            ("Artikelverwaltung","🏷"),
            ("Bestätigung",       "✅"),
            ("Artikelliste",      "📋"),
            ("Lieferanten",      "🏭"),
            ("Berichte",          "📊"),
            ("Einstellungen",    "⚙"),
        ]
        for i, (t, icon) in enumerate(page_configs):
            if i == 0:
                self.stack.addWidget(DashboardPage())
            else:
                self.stack.addWidget(PlaceholderPage(t, icon))

        # Sidebar
        sidebar = Sidebar(self._navigate)

        # Right area = topbar + stack
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

    # Global font
    f = QFont("Segoe UI", 12)
    app.setFont(f)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
