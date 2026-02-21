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
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, QPoint
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
        b2.clicked.connect(lambda: self.window().findChild(QStackedWidget).setCurrentIndex(2) if self.window().findChild(QStackedWidget) else None)
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
# ORDER DETAIL DIALOG (groß, klickbar)
# ──────────────────────────────────────────────
class OrderDetailDialog(QWidget):
    def __init__(self, row_data, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(parent.window().size() if parent else QSize(900, 650))
        self.move(0, 0)

        # Semi-transparent overlay
        overlay = QWidget(self)
        overlay.setStyleSheet("background: rgba(10,25,60,0.55);")
        overlay.resize(self.size())
        overlay.mousePressEvent = lambda e: self.close()

        # Card
        dialog = QFrame(self)
        dialog.setObjectName("dialog")
        dialog.setFixedSize(720, 520)
        dialog.move((self.width() - 720) // 2, (self.height() - 520) // 2)
        dialog.setStyleSheet("""
            QFrame#dialog {
                background: #ffffff;
                border-radius: 18px;
                border: 1px solid #d8e3f0;
            }
        """)
        shadow(dialog, blur=40, color="#00000040")

        lay = QVBoxLayout(dialog)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title_lbl = label("📋  Bestellübersicht – Details", 17, bold=True)
        hdr.addWidget(title_lbl)
        hdr.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        close_btn.setFixedSize(34, 34)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton { background:#f0f4ff; border-radius:8px; border:none; color:#1a2a4a; }
            QPushButton:hover { background:#e0e8ff; }
        """)
        close_btn.clicked.connect(self.close)
        hdr.addWidget(close_btn)
        lay.addLayout(hdr)

        # Order info row
        info_row = QHBoxLayout()
        for lbl_txt, val_txt in [
            ("Order-ID", row_data[0]),
            ("Lieferant", row_data[1]),
            ("Status", row_data[2]),
            ("Datum", row_data[3] if len(row_data) > 3 else "—"),
            ("Betrag", row_data[4] if len(row_data) > 4 else "—"),
        ]:
            box = QFrame()
            box.setStyleSheet("background:#f4f7fd; border-radius:10px; border:1px solid #dde6f5;")
            bl = QVBoxLayout(box)
            bl.setContentsMargins(14, 10, 14, 10)
            bl.setSpacing(2)
            bl.addWidget(label(lbl_txt, 9, color=C_MUTED))
            bl.addWidget(label(val_txt, 13, bold=True))
            info_row.addWidget(box)
        lay.addLayout(info_row)

        # Line items table
        lay.addWidget(label("Bestellpositionen", 13, bold=True))
        detail_headers = ["Artikel", "SKU", "Menge", "Einheit", "Preis/Stk", "Gesamt"]
        detail_rows = [
            ["Bio Vollmilch 3,5%", "ML-001", "48", "Liter", "1,29 €", "61,92 €"],
            ["Frische Eier Gr. M",  "EI-204", "120", "Stk",  "0,25 €", "30,00 €"],
            ["Butter 250g",         "BU-017", "24", "Pkg",   "2,49 €", "59,76 €"],
            ["Naturjoghurt 500g",   "JO-033", "36", "Becher","1,09 €", "39,24 €"],
            ["Sauerrahm 200g",      "SR-055", "18", "Pkg",   "0,89 €", "16,02 €"],
        ]
        tbl = make_table(detail_headers, detail_rows)
        lay.addWidget(tbl)

        # Total row
        total_row = QHBoxLayout()
        total_row.addStretch()
        total_frame = QFrame()
        total_frame.setStyleSheet("background:#1a6bff; border-radius:10px;")
        tfl = QHBoxLayout(total_frame)
        tfl.setContentsMargins(20, 10, 20, 10)
        tl = QLabel("Gesamtbetrag:  206,94 €")
        tl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        tl.setStyleSheet("color:white; background:transparent;")
        tfl.addWidget(tl)
        total_row.addWidget(total_frame)
        lay.addLayout(total_row)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        b_print = btn("🖨  Drucken", bg="#eef2f9", fg=C_TEXT, size=12)
        b_confirm = btn("✅  Bestätigen", bg=C_GREEN, size=12)
        b_cancel  = btn("❌  Stornieren", bg=C_RED, size=12)
        for b in [b_print, b_confirm, b_cancel]:
            b.clicked.connect(lambda _, bb=b: QMessageBox.information(self, "Aktion", f"'{bb.text().strip()}' ausgeführt."))
            btn_row.addWidget(b)
        lay.addLayout(btn_row)

    def show_centered(self, parent_window):
        self.resize(parent_window.size())
        self.move(parent_window.mapToGlobal(parent_window.rect().topLeft()))
        self.show()


# ──────────────────────────────────────────────
# LAGERBESTAND PAGE
# ──────────────────────────────────────────────
class LagerbestandPage(QWidget):
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
        root.addWidget(label("Lagerbestand", 22, bold=True))

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_row.addWidget(KpiCard("Artikel gesamt", "1.248", "📦", "#1a6bff", "#0d4fcf"))
        kpi_row.addWidget(KpiCard("Niedrig-Bestand", "34", "⚠", "#ff8c00", "#e06b00"))
        kpi_row.addWidget(KpiCard("Lagerplätze frei", "87", "🏠", "#28c76f", "#1a9e55"))
        root.addLayout(kpi_row)

        c = card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.addWidget(label("Alle Artikel", 14, bold=True))
        rows = [
            ["Bio Vollmilch 3,5% 1L", "ML-001", "Kühlregal A1", "248", "✅ OK"],
            ["H-Milch 1,5% 1L",       "ML-002", "Regal B3",     "512", "✅ OK"],
            ["Frische Eier Gr. M",     "EI-204", "Kühlregal A2",  "84", "⚠ Niedrig"],
            ["Butter 250g",            "BU-017", "Kühlregal A3", "120", "✅ OK"],
            ["TK Pizza Salami",        "PZ-101", "Tiefkühlung C1","37", "⚠ Niedrig"],
            ["Naturjoghurt 500g",      "JO-033", "Kühlregal A4", "195", "✅ OK"],
            ["Tomaten 500g",           "TO-009", "Regal D2",      "60", "✅ OK"],
            ["Orangensaft 1L",         "OJ-041", "Regal E1",     "310", "✅ OK"],
            ["Mineral Still 1,5L",     "WA-055", "Regal E2",     "430", "✅ OK"],
            ["Sauerrahm 200g",         "SR-055", "Kühlregal A5",  "22", "⚠ Niedrig"],
        ]
        def stock_badge(val):
            if "OK" in val: return ("#e8faf2", "#1a8a52")
            return ("#fff4e0", "#b86200")
        t = make_table(["Artikel", "SKU", "Lagerort", "Bestand", "Status"], rows, badge_cols={4: stock_badge})
        cl.addWidget(t)
        root.addWidget(c)
        root.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


# ──────────────────────────────────────────────
# BESTELLUNGEN PAGE
# ──────────────────────────────────────────────
class BestellungenPage(QWidget):
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
        root.addWidget(label("Bestellungen", 22, bold=True))

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_row.addWidget(KpiCard("Offene Bestellungen", "23", "🛒", "#1a6bff", "#0d4fcf"))
        kpi_row.addWidget(KpiCard("Unterwegs", "11", "🚚", "#ff8c00", "#e06b00"))
        kpi_row.addWidget(KpiCard("Heute erwartet", "4", "📬", "#28c76f", "#1a9e55"))
        root.addLayout(kpi_row)

        c = card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        hdr = QHBoxLayout()
        hdr.addWidget(label("Alle Bestellungen", 14, bold=True))
        hdr.addStretch()
        hdr.addWidget(label("Klicke auf eine Zeile für Details", 10, color=C_MUTED))
        cl.addLayout(hdr)

        self.order_rows = [
            ["#567213", "Lokaler Bauer",     "Unterwegs",  "20.02.2026", "206,94 €"],
            ["#567132", "Obst & Gemüse GmbH","Unterwegs",  "19.02.2026", "148,50 €"],
            ["#567099", "Pfandflaschen AG",  "Anrufen",    "18.02.2026",  "84,20 €"],
            ["#566988", "Zentrallager",      "Bestätigt",  "17.02.2026", "542,30 €"],
            ["#566800", "Bäckerei Müller",   "Geliefert",  "16.02.2026",  "73,10 €"],
            ["#566745", "Molkerei Sonntal",  "Bestätigt",  "15.02.2026", "310,00 €"],
            ["#566600", "Getränke Depot",    "Unterwegs",  "14.02.2026", "229,80 €"],
            ["#566512", "Bio Hof Grüntal",   "Geliefert",  "13.02.2026", "167,40 €"],
        ]

        def status_badge(val):
            m = {
                "Unterwegs": ("#fff4e0", "#b86200"),
                "Anrufen":   ("#ffeaea", "#c0392b"),
                "Bestätigt": ("#e8f0ff", "#1a5dcf"),
                "Geliefert": ("#e8faf2", "#1a8a52"),
            }
            return m.get(val, ("#eee", "#333"))

        self.table = make_table(
            ["Order-ID", "Lieferant", "Status", "Datum", "Betrag"],
            self.order_rows, badge_cols={2: status_badge}
        )
        self.table.setCursor(Qt.PointingHandCursor)
        self.table.cellClicked.connect(self._open_detail)
        cl.addWidget(self.table)
        root.addWidget(c)
        root.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _open_detail(self, row, col):
        dlg = OrderDetailDialog(self.order_rows[row], self)
        dlg.resize(self.window().size())
        dlg.move(self.mapToGlobal(QPoint(0, 0)) - self.window().mapToGlobal(QPoint(0, 0)))
        dlg.show()


# ──────────────────────────────────────────────
# ARTIKELVERWALTUNG PAGE
# ──────────────────────────────────────────────
class ArtikelverwaltungPage(QWidget):
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
        root.addWidget(label("Artikelverwaltung", 22, bold=True))

        bar = QHBoxLayout()
        search = QLineEdit()
        search.setPlaceholderText("🔍  Artikel suchen...")
        search.setFixedHeight(36)
        search.setMaximumWidth(340)
        search.setStyleSheet("background:#fff; border:1.5px solid #d8e3f0; border-radius:9px; padding:0 12px; font-size:13px;")
        bar.addWidget(search)
        bar.addStretch()
        b_new = btn("＋ Neuer Artikel", bg=C_BLUE)
        b_new.clicked.connect(lambda: QMessageBox.information(self, "Neu", "Artikel-Formular öffnen."))
        bar.addWidget(b_new)
        root.addLayout(bar)

        c = card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.addWidget(label("Artikelkatalog", 14, bold=True))
        rows = [
            ["Bio Vollmilch 3,5% 1L", "ML-001", "Molkereiprodukte", "1,29 €", "aktiv"],
            ["H-Milch 1,5% 1L",       "ML-002", "Molkereiprodukte", "0,99 €", "aktiv"],
            ["Frische Eier Gr. M 10er","EI-204", "Frischware",       "2,49 €", "aktiv"],
            ["Butter 250g",            "BU-017", "Molkereiprodukte", "2,49 €", "aktiv"],
            ["TK Pizza Salami 350g",   "PZ-101", "Tiefkühlkost",     "3,99 €", "aktiv"],
            ["Sauerrahm 200g",         "SR-055", "Molkereiprodukte", "0,89 €", "aktiv"],
            ["Altpapier 80g/m²",       "PA-009", "Bürobedarf",       "4,50 €", "inaktiv"],
            ["Orangensaft 1L",         "OJ-041", "Getränke",         "1,79 €", "aktiv"],
        ]
        def art_badge(val):
            return ("#e8faf2", "#1a8a52") if val == "aktiv" else ("#ffeaea", "#c0392b")
        t = make_table(["Artikel", "SKU", "Kategorie", "VK-Preis", "Status"], rows, badge_cols={4: art_badge})
        cl.addWidget(t)
        root.addWidget(c)
        root.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


# ──────────────────────────────────────────────
# BESTÄTIGUNG PAGE
# ──────────────────────────────────────────────
class BestaetigungPage(QWidget):
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
        root.addWidget(label("Bestätigung", 22, bold=True))

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_row.addWidget(KpiCard("Ausstehend", "8", "⏳", "#ff8c00", "#e06b00"))
        kpi_row.addWidget(KpiCard("Heute bestätigt", "15", "✅", "#28c76f", "#1a9e55"))
        kpi_row.addWidget(KpiCard("Abgelehnt", "2", "❌", "#ea5455", "#c0392b"))
        root.addLayout(kpi_row)

        c = card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.addWidget(label("Eingangsbestätigungen", 14, bold=True))
        rows = [
            ["#567213", "Lokaler Bauer",     "20.02.2026 08:15", "ausstehend"],
            ["#566988", "Zentrallager",       "19.02.2026 14:30", "bestätigt"],
            ["#566800", "Bäckerei Müller",    "19.02.2026 09:00", "bestätigt"],
            ["#566745", "Molkerei Sonntal",   "18.02.2026 11:45", "ausstehend"],
            ["#566512", "Bio Hof Grüntal",    "18.02.2026 07:30", "bestätigt"],
            ["#566400", "Getränke Depot",     "17.02.2026 15:00", "abgelehnt"],
        ]
        def best_badge(val):
            m = {
                "ausstehend": ("#fff4e0", "#b86200"),
                "bestätigt":  ("#e8faf2", "#1a8a52"),
                "abgelehnt":  ("#ffeaea", "#c0392b"),
            }
            return m.get(val, ("#eee", "#333"))
        t = make_table(["Order-ID", "Lieferant", "Zeitpunkt", "Status"], rows, badge_cols={3: best_badge})
        cl.addWidget(t)
        root.addWidget(c)
        root.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


# ──────────────────────────────────────────────
# ARTIKELLISTE PAGE
# ──────────────────────────────────────────────
class ArtikellistePage(QWidget):
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
        root.addWidget(label("Artikelliste", 22, bold=True))

        c = card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        hdr = QHBoxLayout()
        hdr.addWidget(label("Vollständige Artikelliste", 14, bold=True))
        hdr.addStretch()
        b_exp = btn("📤 Export", bg="#eef2f9", fg=C_TEXT, size=11)
        b_exp.clicked.connect(lambda: QMessageBox.information(self, "Export", "CSV-Export gestartet."))
        hdr.addWidget(b_exp)
        cl.addLayout(hdr)
        rows = [
            ["Bio Vollmilch 3,5% 1L", "ML-001", "Kühlregal A1",    "248", "1,29 €",  "14 Tage"],
            ["H-Milch 1,5% 1L",       "ML-002", "Regal B3",        "512", "0,99 €",  "45 Tage"],
            ["Frische Eier Gr. M",     "EI-204", "Kühlregal A2",     "84", "2,49 €",   "5 Tage"],
            ["Butter 250g",            "BU-017", "Kühlregal A3",    "120", "2,49 €",  "21 Tage"],
            ["TK Pizza Salami 350g",   "PZ-101", "Tiefkühlung C1",   "37", "3,99 €",  "90 Tage"],
            ["Naturjoghurt 500g",      "JO-033", "Kühlregal A4",    "195", "1,09 €",   "8 Tage"],
            ["Tomaten 500g",           "TO-009", "Regal D2",         "60", "1,49 €",   "3 Tage"],
            ["Orangensaft 1L",         "OJ-041", "Regal E1",        "310", "1,79 €",  "60 Tage"],
            ["Mineral Still 1,5L",     "WA-055", "Regal E2",        "430", "0,79 €", "180 Tage"],
            ["Sauerrahm 200g",         "SR-055", "Kühlregal A5",     "22", "0,89 €",  "12 Tage"],
        ]
        t = make_table(["Artikel", "SKU", "Lagerort", "Bestand", "Preis", "MHD"], rows)
        cl.addWidget(t)
        root.addWidget(c)
        root.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


# ──────────────────────────────────────────────
# LIEFERANTEN PAGE
# ──────────────────────────────────────────────
class LieferantenPage(QWidget):
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
        root.addWidget(label("Lieferanten", 22, bold=True))

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_row.addWidget(KpiCard("Aktive Lieferanten", "18", "🏭", "#1a6bff", "#0d4fcf"))
        kpi_row.addWidget(KpiCard("Lieferungen diesen Monat", "134", "📦", "#28c76f", "#1a9e55"))
        kpi_row.addWidget(KpiCard("Offene Rechnungen", "7", "💶", "#ff8c00", "#e06b00"))
        root.addLayout(kpi_row)

        c = card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.addWidget(label("Lieferantenübersicht", 14, bold=True))
        rows = [
            ["Zentrallager Nord-West",  "ZLN",  "Lebensmittel",    "134",  "aktiv"],
            ["Lokale Erzeuger GmbH",    "LEG",  "Frischware",      "121",  "aktiv"],
            ["Gerlah GmbH",             "GER",  "Getränke",         "81",  "aktiv"],
            ["Bäckerei Müller",         "BMÜ",  "Backwaren",        "45",  "aktiv"],
            ["Molkerei Sonntal",        "MST",  "Molkereiprodukte", "98",  "aktiv"],
            ["Bio Hof Grüntal",         "BHG",  "Bioprodukte",      "63",  "aktiv"],
            ["Pfandflaschen AG",        "PFA",  "Verpackung",       "29",  "aktiv"],
            ["Alten Lieferant KG",      "ALK",  "Sonstiges",         "4",  "inaktiv"],
        ]
        def lief_stat_badge(val):
            return ("#e8faf2", "#1a8a52") if val == "aktiv" else ("#ffeaea", "#c0392b")
        t = make_table(["Lieferant", "Kürzel", "Kategorie", "Lieferungen", "Status"], rows, badge_cols={4: lief_stat_badge})
        cl.addWidget(t)
        root.addWidget(c)
        root.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


# ──────────────────────────────────────────────
# BERICHTE PAGE
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
        root.addWidget(label("Berichte", 22, bold=True))

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_row.addWidget(KpiCard("Umsatz Februar", "12.480 €", "📈", "#1a6bff", "#0d4fcf"))
        kpi_row.addWidget(KpiCard("Schwund", "342 €", "📉", "#ea5455", "#c0392b"))
        kpi_row.addWidget(KpiCard("Retourenquote", "2,3%", "🔄", "#ff8c00", "#e06b00"))
        root.addLayout(kpi_row)

        # Chart card
        cc = card()
        cl = QVBoxLayout(cc)
        cl.setContentsMargins(20, 18, 20, 14)
        cl.addWidget(label("Bestandsentwicklung (Monat)", 14, bold=True))
        chart = LineChart()
        cl.addWidget(chart)
        root.addWidget(cc)

        c = card()
        cl2 = QVBoxLayout(c)
        cl2.setContentsMargins(20, 18, 20, 18)
        cl2.addWidget(label("Monatsübersicht", 14, bold=True))
        rows = [
            ["Januar 2026",  "10.240 €", "280 €", "1.8%", "1.124"],
            ["Dezember 2025","14.880 €", "410 €", "2.9%", "1.380"],
            ["November 2025","11.760 €", "300 €", "2.1%", "1.205"],
            ["Oktober 2025", "12.100 €", "270 €", "1.7%", "1.190"],
        ]
        t = make_table(["Monat", "Umsatz", "Schwund", "Retourenquote", "Artikel bewegt"], rows)
        cl2.addWidget(t)
        root.addWidget(c)
        root.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


# ──────────────────────────────────────────────
# EINSTELLUNGEN PAGE
# ──────────────────────────────────────────────
class EinstellungenPage(QWidget):
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
        root.addWidget(label("Einstellungen", 22, bold=True))

        for section, fields in [
            ("Benutzerprofil", [
                ("Name", "Max Mustermann"),
                ("E-Mail", "max.mustermann@lagerpro.de"),
                ("Rolle", "Administrator"),
            ]),
            ("System", [
                ("Sprache", "Deutsch"),
                ("Zeitzone", "Europe/Berlin"),
                ("Datenbank-Host", "localhost:5432"),
            ]),
        ]:
            c = card()
            cl = QVBoxLayout(c)
            cl.setContentsMargins(24, 18, 24, 18)
            cl.setSpacing(12)
            cl.addWidget(label(section, 14, bold=True))
            for field, value in fields:
                row = QHBoxLayout()
                row.addWidget(label(field, 12, color=C_MUTED))
                row.addStretch()
                inp = QLineEdit(value)
                inp.setFixedHeight(34)
                inp.setMaximumWidth(300)
                inp.setStyleSheet("background:#f4f7fd; border:1.5px solid #d8e3f0; border-radius:8px; padding:0 10px; font-size:12px;")
                row.addWidget(inp)
                cl.addLayout(row)
            b_save = btn("💾 Speichern", bg=C_GREEN, size=12)
            b_save.clicked.connect(lambda _, s=section: QMessageBox.information(self, "Gespeichert", f"'{s}' gespeichert."))
            cl.addWidget(b_save)
            root.addWidget(c)

        root.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


# ──────────────────────────────────────────────
# PLACEHOLDER PAGE (Fallback)
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
        page_classes = [
            DashboardPage,
            LagerbestandPage,
            BestellungenPage,
            ArtikelverwaltungPage,
            BestaetigungPage,
            ArtikellistePage,
            LieferantenPage,
            BerichtePage,
            EinstellungenPage,
        ]
        for i, (t, icon) in enumerate(page_configs):
            self.stack.addWidget(page_classes[i]())

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