"""
LagerPro – Geteilte Widgets
============================
GradientWidget  : Widget mit Farbverlauf-Hintergrund
LineChart       : Mini-Liniendiagramm
KpiCard         : KPI-Karte mit Farbverlauf
NavButton       : Navigations-Schaltfläche
Sidebar         : Linke Navigationsleiste
Topbar          : Obere Leiste
"""

from PyQt5.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QSizePolicy, QApplication, QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QColor, QFont, QLinearGradient, QPainter, QBrush, QPen, QPainterPath,
)

from .colors import AppColors
from .widget_factory import WidgetFactory
from .music import MusicPlayer


# ══════════════════════════════════════════════
#  GRADIENT WIDGET
# ══════════════════════════════════════════════

class GradientWidget(QWidget):
    """Widget mit linearem Farbverlauf als Hintergrund."""

    def __init__(self, color1: str, color2: str, radius: int = 14, parent=None):
        super().__init__(parent)
        self._c1 = QColor(color1)
        self._c2 = QColor(color2)
        self._radius = radius

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, self._c1)
        grad.setColorAt(1, self._c2)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self._radius, self._radius)
        p.fillPath(path, QBrush(grad))


# ══════════════════════════════════════════════
#  LINE CHART
# ══════════════════════════════════════════════

class LineChart(QWidget):
    """Einfaches Liniendiagramm mit zwei Datenreihen."""

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
        n = len(self.series1)

        def to_px(idx, val):
            return int(pad_l + idx * cw / (n - 1)), int(pad_t + val * ch / 120)

        p.setPen(QPen(QColor("#f0f4f8"), 1))
        for i in range(5):
            yy = pad_t + i * ch // 4
            p.drawLine(pad_l, yy, W - pad_r, yy)

        p.setPen(QPen(QColor(AppColors.MUTED)))
        p.setFont(QFont("Segoe UI", 8))
        for i, yl in enumerate(["12k", "3k", "2k", "1k", "0"]):
            p.drawText(0, pad_t + i * ch // 4 + 4, 30, 14, Qt.AlignRight, yl)

        def draw_area(series, color):
            pts = [to_px(i, v) for i, v in enumerate(series)]
            path = QPainterPath()
            path.moveTo(*pts[0])
            for x, y in pts[1:]:
                path.lineTo(x, y)
            path.lineTo(pts[-1][0], H - pad_b)
            path.lineTo(pts[0][0],  H - pad_b)
            path.closeSubpath()
            c = QColor(color)
            c.setAlpha(40)
            p.fillPath(path, QBrush(c))

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

        draw_area(self.series1, AppColors.BLUE)
        draw_area(self.series2, AppColors.GREEN)
        draw_line(self.series1, AppColors.BLUE)
        draw_line(self.series2, AppColors.GREEN)

        p.setPen(QPen(QColor(AppColors.MUTED)))
        p.setFont(QFont("Segoe UI", 8))
        for i, xl in enumerate(self.labels):
            x = pad_l + i * cw // (len(self.labels) - 1) - 10
            p.drawText(x, H - pad_b + 6, 24, 16, Qt.AlignCenter, xl)


# ══════════════════════════════════════════════
#  KPI CARD
# ══════════════════════════════════════════════

class KpiCard(GradientWidget):
    """KPI-Karte mit Farbverlauf, Titel, Wert und optionalem Click-Handler."""

    def __init__(self, title: str, value: str, icon_char: str,
                 color1: str, color2: str, on_click=None, parent=None):
        super().__init__(color1, color2, parent=parent)
        self.setFixedHeight(100)
        self._on_click = on_click
        WidgetFactory.shadow(self)
        self.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 14, 22, 14)

        left = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 11))
        lbl_title.setStyleSheet("color: rgba(255,255,255,200); background: transparent;")
        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Segoe UI", 36, QFont.Black))
        lbl_value.setStyleSheet("color: white; background: transparent;")
        left.addWidget(lbl_title)
        left.addWidget(lbl_value)

        lbl_icon = QLabel(icon_char)
        lbl_icon.setFont(QFont("Segoe UI", 34))
        lbl_icon.setStyleSheet("color: rgba(255,255,255,80); background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)

        lay.addLayout(left)
        lay.addStretch()
        lay.addWidget(lbl_icon)

    def mousePressEvent(self, event):
        if self._on_click:
            self._on_click()


# ══════════════════════════════════════════════
#  NAV BUTTON
# ══════════════════════════════════════════════

class NavButton(QPushButton):
    """Navigations-Schaltfläche für die Sidebar mit Aktiv-Zustand."""

    _STYLE_ACTIVE = """
        QPushButton {
            background: #1e4080; color: white; border: none;
            border-left: 3px solid #1a6bff;
            text-align: left; padding-left: 14px; border-radius: 0px;
        }
    """
    _STYLE_INACTIVE = """
        QPushButton {
            background: transparent; color: rgba(255,255,255,160);
            border: none; border-left: 3px solid transparent;
            text-align: left; padding-left: 14px; border-radius: 0px;
        }
        QPushButton:hover { background: #122a52; color: white; }
        QPushButton:pressed { background: #1e4080; }
    """

    def __init__(self, icon_char: str, text: str, active: bool = False, parent=None):
        super().__init__(parent)
        self.active = active
        self.setText(f"  {icon_char}  {text}")
        self.setFont(QFont("Segoe UI", 13))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.refresh_style()

    def refresh_style(self):
        self.setStyleSheet(self._STYLE_ACTIVE if self.active else self._STYLE_INACTIVE)


# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════

class Sidebar(GradientWidget):
    """Linke Navigationsleiste mit Logo, Menüpunkten, Musik-Player und Benutzerinfo."""

    _NAV_ITEMS = [
        ("🏠", "Dashboard",         0),
        ("📦", "Lagerbestand",      1),
        ("🛒", "Bestellungen",      2),
        ("🏷", "Artikelverwaltung", 3),
        ("✅", "Bestätigung",       4),
        ("📋", "Artikelliste",      5),
        ("🏭", "Lieferanten",       6),
        ("📊", "Berichte",          7),
        ("⚙",  "Einstellungen",    8),
    ]

    def __init__(self, on_navigate, music_player: MusicPlayer = None, parent=None):
        super().__init__(AppColors.SIDEBAR, AppColors.SIDEBAR_DARK, radius=0, parent=parent)
        self.setFixedWidth(210)
        self._on_navigate = on_navigate
        self._nav_buttons: list[NavButton] = []
        self._music_player = music_player
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_logo())
        root.addWidget(self._separator())

        for icon, text, idx in self._NAV_ITEMS:
            b = NavButton(icon, text, active=(idx == 0))
            b.clicked.connect(lambda _, i=idx, nm=text: self._handle_nav(i, nm))
            self._nav_buttons.append(b)
            root.addWidget(b)

        root.addStretch()
        root.addWidget(self._separator())

        if self._music_player:
            root.addWidget(self._music_player)
            root.addWidget(self._separator())

        root.addWidget(self._build_user_section())

    def _build_logo(self) -> QWidget:
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
        return logo_w

    def _build_user_section(self) -> QWidget:
        user_w = QWidget()
        user_w.setStyleSheet("background: transparent;")
        ulay = QVBoxLayout(user_w)
        ulay.setContentsMargins(16, 12, 16, 12)
        ulay.setAlignment(Qt.AlignCenter)

        for text, size, bold, color in [
            ("👤",           28, False, ""),
            ("Max Mustermann", 12, True,  "white"),
            ("Admin",          10, False, "rgba(255,255,255,120)"),
        ]:
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", size, QFont.Bold if bold else QFont.Normal))
            lbl.setStyleSheet(f"color: {color}; background: transparent;" if color else "background: transparent;")
            lbl.setAlignment(Qt.AlignCenter)
            ulay.addWidget(lbl)

        ulay.addSpacing(6)
        logout_btn = WidgetFactory.button("⬛ LOGOUT", bg=AppColors.ORANGE)
        logout_btn.clicked.connect(self._logout)
        logout_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        ulay.addWidget(logout_btn)
        return user_w

    @staticmethod
    def _separator() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: rgba(255,255,255,30);")
        return sep

    def _handle_nav(self, idx: int, name: str):
        for i, b in enumerate(self._nav_buttons):
            b.active = (i == idx)
            b.refresh_style()
        self._on_navigate(idx, name)

    def _logout(self):
        reply = QMessageBox.question(self, "Abmelden",
            "Möchten Sie sich wirklich abmelden?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()


# ══════════════════════════════════════════════
#  TOPBAR
# ══════════════════════════════════════════════

class Topbar(QFrame):
    """Obere Leiste mit Suche, Benachrichtigungen und Benutzer-Chip."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setStyleSheet("QFrame { background: white; border-bottom: 1px solid #d8e3f0; }")
        self._build_ui()

    def _build_ui(self):
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

        icon_style = """
            QPushButton { background: #eef2f9; border: 1px solid #d8e3f0; border-radius: 10px; }
            QPushButton:hover { background: #dce6f5; }
        """
        for icon, tip in [("🔔", "Benachrichtigungen"), ("✉", "Nachrichten")]:
            b = QPushButton(icon)
            b.setToolTip(tip)
            b.setFont(QFont("Segoe UI", 14))
            b.setFixedSize(38, 38)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(icon_style)
            lay.addWidget(b)

        user_chip = QPushButton("👤  Max Mustermann  (Admin)")
        user_chip.setFont(QFont("Segoe UI", 11))
        user_chip.setFixedHeight(38)
        user_chip.setCursor(Qt.PointingHandCursor)
        user_chip.setStyleSheet("""
            QPushButton { background: #eef2f9; border: 1px solid #d8e3f0; border-radius: 10px; padding: 0 14px; color: #1a2a4a; }
            QPushButton:hover { background: #dce6f5; }
        """)
        user_chip.clicked.connect(
            lambda: QMessageBox.information(None, "Profil", "Profil von Max Mustermann (Admin)"))
        lay.addWidget(user_chip)
