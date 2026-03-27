"""
LagerPro – Seiten (Pages)
=========================
BasePage              : Basisklasse mit Scroll-Layout und Hilfsmethoden
DashboardPage         : Übersicht mit KPIs, Lieferungen, Bestellungen, Chart
LagerbestandPage      : Tabellarische Bestandsübersicht
BestellungenPage      : Bestellungsverwaltung mit Filter
ArtikelverwaltungPage : Karten-Ansicht mit CRUD
BestaetigungPage      : Wareneingang bestätigen
ArtikellistePage      : Artikel nach Kategorie gruppiert
LieferantenPage       : Lieferantenverwaltung
BerichtePage          : CSV-Exporte und Statistiken
EinstellungenPage     : Musik, Datenverwaltung, App-Info
"""

import datetime

from PyQt5.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QLabel, QPushButton, QMessageBox, QFileDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from .colors import AppColors
from .data_store import DataStore
from .exporters import CsvExporter, PdfExporter
from .widget_factory import WidgetFactory
from .widgets import GradientWidget, LineChart, KpiCard
from .dialogs import (
    ArtikelDetailDialog, NeueBestellungDialog, BestellungDetailDialog,
    NeuerArtikelDialog, ArtikelBearbeitenDialog, LieferantDialog,
)
from .music import MusicPlayer, MUSIC_AVAILABLE


# ══════════════════════════════════════════════
#  BASIS-SEITE
# ══════════════════════════════════════════════

class BasePage(QWidget):
    """Gemeinsame Basisklasse für alle Seiten."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._store = DataStore.instance()
        self.setStyleSheet(f"background: {AppColors.PAGE};")

    def _wrap_in_scroll(self, inner: QWidget):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(inner)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)

    @staticmethod
    def _page_root() -> tuple:
        inner = QWidget()
        inner.setStyleSheet(f"background: {AppColors.PAGE};")
        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(20)
        return inner, root

    @staticmethod
    def _make_table(headers: list, rows: list, badge_cols: dict = None) -> QTableWidget:
        WF = WidgetFactory
        t = QTableWidget(len(rows), len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.setAlternatingRowColors(False)
        t.verticalHeader().setVisible(False)
        t.setShowGrid(False)
        t.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        t.setStyleSheet("""
            QTableWidget { background: transparent; border: none; outline: none; }
            QHeaderView::section {
                background: transparent; color: #7b8ea9; font-size: 11px; font-weight: bold;
                border: none; padding: 4px 8px 8px 8px; border-bottom: 1px solid #d8e3f0;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #f0f4f8; color: #1a2a4a; }
            QTableWidget::item:selected { background: #e8f0ff; color: #1a2a4a; }
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
                    hl.addWidget(WF.badge(val, bg, fg))
                    hl.addStretch()
                    t.setCellWidget(r, c, cell_w)
                else:
                    item = QTableWidgetItem(str(val))
                    item.setFont(QFont("Segoe UI", 12, QFont.Medium if c == 0 else QFont.Normal))
                    t.setItem(r, c, item)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        total = sum(t.rowHeight(r) for r in range(len(rows)))
        t.setFixedHeight(total + t.horizontalHeader().height() + 4)
        return t


# ══════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════

class DashboardPage(BasePage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        WF = WidgetFactory
        inner, root = self._page_root()
        root.addWidget(WF.label("Dashboard", 22, bold=True))

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_row.addWidget(KpiCard("Kritische MHDs",          "47", "⚠",  AppColors.BLUE,   "#0d4fcf",
            on_click=lambda: QMessageBox.information(self,"MHDs","47 Artikel mit kritischem MHD.")))
        kpi_row.addWidget(KpiCard("Fehlartikel (Regal leer)", "12", "🚚", AppColors.ORANGE, "#e06b00",
            on_click=lambda: QMessageBox.information(self,"Fehlartikel","12 Artikel sofort nachbestellen!")))
        kpi_row.addWidget(KpiCard("Wareneingang Heute",       "6",  "📦", AppColors.GREEN,  "#1a9e55",
            on_click=lambda: QMessageBox.information(self,"Wareneingang","6 Lieferungen heute eingegangen.")))
        root.addLayout(kpi_row)

        grid = QHBoxLayout()
        grid.setSpacing(20)
        grid.setAlignment(Qt.AlignTop)

        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        left_col.setAlignment(Qt.AlignTop)
        left_col.addWidget(self._build_lieferungen_card())
        left_col.addWidget(self._build_bestellungen_card())
        left_col.addWidget(self._build_lagerbestand_card())
        left_col.addStretch()

        right_col = QVBoxLayout()
        right_col.setSpacing(20)
        right_col.setAlignment(Qt.AlignTop)
        right_col.addWidget(self._build_chart_card())
        right_col.addWidget(self._build_supplier_card())
        right_col.addStretch()

        left_w = QWidget()
        left_w.setLayout(left_col)
        left_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        right_w = QWidget()
        right_w.setLayout(right_col)
        right_w.setFixedWidth(330)

        grid.addWidget(left_w)
        grid.addWidget(right_w)
        root.addLayout(grid)
        self._wrap_in_scroll(inner)

    def _build_lieferungen_card(self) -> QFrame:
        WF = WidgetFactory
        c = WF.card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        hdr = QHBoxLayout()
        hdr.addWidget(WF.label("Aktuelle Lieferungen", 14, bold=True))
        hdr.addStretch()
        a_btn = QPushButton("›")
        a_btn.setFlat(True)
        a_btn.setFont(QFont("Segoe UI", 16))
        a_btn.setStyleSheet(f"color: {AppColors.BLUE}; background: transparent; border: none;")
        a_btn.setCursor(Qt.PointingHandCursor)
        a_btn.clicked.connect(lambda: QMessageBox.information(self,"Lieferungen","Alle aktuellen Lieferungen."))
        hdr.addWidget(a_btn)
        cl.addLayout(hdr)

        def lief_badge(val):
            return {"Verziegt":("#e8faf2","#1a8a52"),"Berailget":("#fff4e0","#b86200"),"Anrufen":("#ffeaea","#c0392b")}.get(val,("#eee","#333"))

        t = self._make_table(
            ["Lieferant","Status","Versendet"],
            [["Zentrallager (Kette Nord-West)","","Verziegt"],
             ["Lokaler Bauer (Milch & Eier)",   "","Berailget"],
             ["Getränke GmbH",                  "","Anrufen"]],
            badge_cols={2: lief_badge}
        )
        cl.addWidget(t)
        return c

    def _build_bestellungen_card(self) -> QFrame:
        WF = WidgetFactory
        c = WF.card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        hdr = QHBoxLayout()
        hdr.addWidget(WF.label("Aktuelle Bestellungen", 14, bold=True))
        hdr.addStretch()
        new_btn = WF.button("+ Neue Bestellung", bg=AppColors.GREEN, size=11)
        new_btn.setFixedHeight(32)
        new_btn.clicked.connect(self._neue_bestellung)
        hdr.addWidget(new_btn)
        cl.addLayout(hdr)

        rows = [[b["id"],b["lieferant"],b["status"]] for b in self._store.bestellungen[:4]]
        t = self._make_table(["Order-ID","Lieferant","Status"], rows,
            badge_cols={2: lambda v: AppColors.STATUS_COLORS.get(v,("#eee","#333"))})
        t.cellDoubleClicked.connect(lambda r, _: self._open_bestellung_detail(r))
        cl.addWidget(t)
        cl.addWidget(WF.label("Doppelklick für Details", 10, color=AppColors.MUTED))
        b_all = WF.button("Alle Bestellungen anzeigen")
        b_all.clicked.connect(lambda: QMessageBox.information(self,"Bestellungen","Wechseln Sie zur Bestellungsseite."))
        cl.addSpacing(10)
        cl.addWidget(b_all)
        return c

    def _build_lagerbestand_card(self) -> QFrame:
        WF = WidgetFactory
        c = WF.card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        hdr = QHBoxLayout()
        hdr.addWidget(WF.label("Lagerbestand & MHD", 14, bold=True))
        hdr.addStretch()
        csv_btn = WF.button("📊 CSV", bg=AppColors.MUTED, size=11)
        csv_btn.setFixedHeight(30)
        csv_btn.clicked.connect(lambda: CsvExporter.export(
            self._store.artikel,
            ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"],
            "Lagerbestand", self))
        hdr.addWidget(csv_btn)
        cl.addLayout(hdr)
        for art in self._store.artikel[:3]:
            cl.addWidget(self._build_mhd_row(art))
        b_all = WF.button("Alle Artikel anzeigen")
        b_all.clicked.connect(lambda: QMessageBox.information(self,"Lagerbestand","Wechseln Sie zur Lagerbestandsseite."))
        cl.addSpacing(10)
        cl.addWidget(b_all)
        return c

    def _build_mhd_row(self, art: dict) -> QWidget:
        WF = WidgetFactory
        mhd_display = self._format_mhd(art["mhd"])
        row_w = QWidget()
        row_w.setStyleSheet("border-bottom: 1px solid #f0f4f8;")
        rl = QHBoxLayout(row_w)
        rl.setContentsMargins(0, 8, 0, 8)
        rl.addWidget(WF.label(art["name"], 12, bold=True))
        rl.addWidget(WF.label(art["id"], 11, color=AppColors.MUTED))
        rl.addStretch()
        bg, fg = self._mhd_badge_color(mhd_display)
        rl.addWidget(WF.badge(mhd_display, bg, fg))
        rl.addSpacing(10)
        eb = WF.button("Detail", bg=AppColors.BLUE, size=11)
        eb.setFixedHeight(28)
        eb.clicked.connect(lambda _, a=art: ArtikelDetailDialog(a, self).exec_())
        rl.addWidget(eb)
        return row_w

    @staticmethod
    def _format_mhd(mhd_str: str) -> str:
        try:
            diff = (datetime.datetime.strptime(mhd_str,"%Y-%m-%d").date() - datetime.date.today()).days
            if diff < 3:  return "⚡ REDUZIEREN"
            if diff < 14: return f"⚠ {diff} Tage"
            return f"✅ {diff} Tage"
        except Exception:
            return mhd_str

    @staticmethod
    def _mhd_badge_color(mhd_display: str) -> tuple:
        if "REDUZIEREN" in mhd_display: return "#fff8e1","#a07000"
        if "Tage" in mhd_display:
            for part in mhd_display.split():
                try:
                    num = int(part)
                    return ("#e8faf2","#1a8a52") if num >= 14 else ("#fff4e0","#b86200")
                except ValueError:
                    pass
        return "#ffeaea","#c0392b"

    def _build_chart_card(self) -> QFrame:
        WF = WidgetFactory
        cc = WF.card()
        cl = QVBoxLayout(cc)
        cl.setContentsMargins(20, 18, 20, 14)
        cl.addWidget(WF.label("Bestandsübersicht", 14, bold=True))
        cl.addWidget(LineChart())
        legend_row = QHBoxLayout()
        for col, name in [(AppColors.BLUE,"Lagerbestand"),(AppColors.ORANGE,"Bestellungen"),(AppColors.GREEN,"Einlagerungen")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{col}; background:transparent;")
            dot.setFont(QFont("Segoe UI", 14))
            legend_row.addWidget(dot)
            legend_row.addWidget(WF.label(name, 10, color=AppColors.MUTED))
            legend_row.addSpacing(8)
        legend_row.addStretch()
        cl.addLayout(legend_row)
        return cc

    def _build_supplier_card(self) -> QFrame:
        WF = WidgetFactory
        c = WF.card()
        lay = QVBoxLayout(c)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(0)
        hdr = QHBoxLayout()
        hdr.addWidget(WF.label("Top Lieferanten", 14, bold=True))
        hdr.addStretch()
        lay.addLayout(hdr)
        lay.addSpacing(10)
        for icon, name, sub, count in [
            ("🏭","Zentrallager","134 Lieferungen",128),
            ("📦","Pfandflaschen Paletten","",76),
        ]:
            row = QHBoxLayout()
            ico = QLabel(icon)
            ico.setFont(QFont("Segoe UI", 22))
            ico.setFixedSize(38, 38)
            ico.setAlignment(Qt.AlignCenter)
            ico.setStyleSheet("background: #f0f4ff; border-radius: 8px;")
            info = QVBoxLayout()
            info.setSpacing(1)
            info.addWidget(WF.label(name, 12, bold=True))
            if sub:
                info.addWidget(WF.label(sub, 10, color=AppColors.MUTED))
            cnt = WF.label(str(count), 16, bold=True)
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
        b = WF.button("Lieferanten verwalten", bg="transparent", fg=AppColors.BLUE, radius=9)
        b.setStyleSheet(b.styleSheet() + f"QPushButton {{ border: 2px solid {AppColors.BLUE}; }}")
        b.clicked.connect(lambda: QMessageBox.information(None,"Lieferanten","Lieferantenverwaltung wird geöffnet."))
        lay.addSpacing(10)
        lay.addWidget(b)
        return c

    def _neue_bestellung(self):
        NeueBestellungDialog(parent=self).exec_()

    def _open_bestellung_detail(self, row: int):
        if row < len(self._store.bestellungen):
            BestellungDetailDialog(self._store.bestellungen[row], self).exec_()


# ══════════════════════════════════════════════
#  LAGERBESTAND
# ══════════════════════════════════════════════

class LagerbestandPage(BasePage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        WF = WidgetFactory
        inner, root = self._page_root()

        hdr = QHBoxLayout()
        hdr.addWidget(WF.label("📦 Lagerbestand", 22, bold=True))
        hdr.addStretch()
        b_new = WF.button("+ Neuer Artikel", bg=AppColors.GREEN)
        b_new.clicked.connect(self._neuer_artikel)
        b_csv = WF.button("📊 CSV Export", bg=AppColors.MUTED)
        b_csv.clicked.connect(lambda: CsvExporter.export(
            self._store.artikel,
            ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"],
            "Lagerbestand", self))
        hdr.addWidget(b_new)
        hdr.addWidget(b_csv)
        root.addLayout(hdr)

        self._search_box = WF.text_input("🔍 Artikel suchen...")
        self._search_box.textChanged.connect(self._filter)
        root.addWidget(self._search_box)

        c = WF.card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        self._table = WF.table_widget(["ID","Name","Kategorie","Bestand","Mindest","Preis","Lieferant","Aktionen"])
        self._table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self._table.setColumnWidth(7, 200)
        cl.addWidget(self._table)
        root.addWidget(c)

        self._populate_table(self._store.artikel)
        self._wrap_in_scroll(inner)

    def _populate_table(self, artikel_list: list):
        WF = WidgetFactory
        self._table.setRowCount(len(artikel_list))
        for r, art in enumerate(artikel_list):
            self._table.setRowHeight(r, 46)
            self._table.setItem(r, 0, QTableWidgetItem(art["id"]))
            self._table.setItem(r, 1, QTableWidgetItem(art["name"]))
            self._table.setItem(r, 2, QTableWidgetItem(art["kategorie"]))
            bestand_item = QTableWidgetItem(str(art["bestand"]))
            if art["bestand"] < art["min_bestand"]:
                bestand_item.setForeground(QColor(AppColors.RED))
                bestand_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            else:
                bestand_item.setForeground(QColor(AppColors.GREEN))
            self._table.setItem(r, 3, bestand_item)
            self._table.setItem(r, 4, QTableWidgetItem(str(art["min_bestand"])))
            self._table.setItem(r, 5, QTableWidgetItem(f"€ {art['preis']:.2f}"))
            self._table.setItem(r, 6, QTableWidgetItem(art["lieferant"]))
            btn_w = QWidget()
            btn_lay = QHBoxLayout(btn_w)
            btn_lay.setContentsMargins(4, 2, 4, 2)
            btn_lay.setSpacing(4)
            b_detail = WF.button("Detail", bg=AppColors.BLUE, size=10)
            b_detail.setFixedHeight(28)
            b_detail.clicked.connect(lambda _, a=art: ArtikelDetailDialog(a, self).exec_())
            b_bestell = WF.button("Bestellen", bg=AppColors.GREEN, size=10)
            b_bestell.setFixedHeight(28)
            b_bestell.clicked.connect(lambda _, a=art: NeueBestellungDialog(pre_artikel=a, parent=self).exec_())
            btn_lay.addWidget(b_detail)
            btn_lay.addWidget(b_bestell)
            btn_lay.addStretch()
            self._table.setCellWidget(r, 7, btn_w)

    def _filter(self, text: str):
        filtered = [a for a in self._store.artikel
                    if text.lower() in a["name"].lower() or text.lower() in a["id"].lower()]
        self._populate_table(filtered)

    def _neuer_artikel(self):
        if NeuerArtikelDialog(self).exec_():
            self._populate_table(self._store.artikel)


# ══════════════════════════════════════════════
#  BESTELLUNGEN
# ══════════════════════════════════════════════

class BestellungenPage(BasePage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        WF = WidgetFactory
        inner, root = self._page_root()

        hdr = QHBoxLayout()
        hdr.addWidget(WF.label("🛒 Bestellungen", 22, bold=True))
        hdr.addStretch()
        b_new = WF.button("+ Neue Bestellung", bg=AppColors.GREEN)
        b_new.clicked.connect(self._neue_bestellung)
        b_csv = WF.button("📊 CSV Export", bg=AppColors.MUTED)
        b_csv.clicked.connect(lambda: CsvExporter.export(
            self._store.bestellungen,
            ["id","datum","lieferant","artikel","menge","status","gesamt"],
            "Bestellungen", self))
        hdr.addWidget(b_new)
        hdr.addWidget(b_csv)
        root.addLayout(hdr)

        filter_row = QHBoxLayout()
        self._search = WF.text_input("🔍 Bestell-ID oder Lieferant suchen...")
        self._search.textChanged.connect(self._filter)
        self._status_filter = WF.combo_box(["Alle Status","Unterwegs","Ausstehend","Geliefert","Anrufen","Storniert"])
        self._status_filter.currentTextChanged.connect(self._filter)
        filter_row.addWidget(self._search, 2)
        filter_row.addWidget(self._status_filter, 1)
        root.addLayout(filter_row)

        c = WF.card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 18, 20, 18)
        self._table = WF.table_widget(["ID","Datum","Lieferant","Artikel","Menge","Gesamt","Status","Aktionen"])
        self._table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self._table.setColumnWidth(7, 200)
        cl.addWidget(self._table)
        root.addWidget(c)

        self._populate_table(self._store.bestellungen)
        self._wrap_in_scroll(inner)

    def _populate_table(self, data: list):
        WF = WidgetFactory
        self._table.setRowCount(len(data))
        for r, b_data in enumerate(data):
            self._table.setRowHeight(r, 46)
            self._table.setItem(r, 0, QTableWidgetItem(b_data.get("id","–")))
            self._table.setItem(r, 1, QTableWidgetItem(b_data.get("datum","–")))
            self._table.setItem(r, 2, QTableWidgetItem(b_data.get("lieferant","–")))
            self._table.setItem(r, 3, QTableWidgetItem(b_data.get("artikel","–")))
            self._table.setItem(r, 4, QTableWidgetItem(str(b_data.get("menge","–"))))
            self._table.setItem(r, 5, QTableWidgetItem(f"€ {b_data.get('gesamt',0):.2f}"))
            status = b_data.get("status","–")
            bg, fg = AppColors.STATUS_COLORS.get(status, ("#eee","#333"))
            cell_w = QWidget()
            hl = QHBoxLayout(cell_w)
            hl.setContentsMargins(4, 4, 4, 4)
            hl.addWidget(WF.badge(status, bg, fg))
            hl.addStretch()
            self._table.setCellWidget(r, 6, cell_w)
            btn_w = QWidget()
            btn_lay = QHBoxLayout(btn_w)
            btn_lay.setContentsMargins(4, 2, 4, 2)
            btn_lay.setSpacing(4)
            b_detail = WF.button("Detail", bg=AppColors.BLUE, size=10)
            b_detail.setFixedHeight(28)
            b_detail.clicked.connect(lambda _, d=b_data: BestellungDetailDialog(d, self).exec_())
            b_pdf = WF.button("🖨 PDF", bg=AppColors.ORANGE, size=10)
            b_pdf.setFixedHeight(28)
            b_pdf.clicked.connect(lambda _, d=b_data: PdfExporter.export_bestellung(d, self))
            btn_lay.addWidget(b_detail)
            btn_lay.addWidget(b_pdf)
            btn_lay.addStretch()
            self._table.setCellWidget(r, 7, btn_w)

    def _filter(self):
        text     = self._search.text().lower()
        status_f = self._status_filter.currentText()
        filtered = [b for b in self._store.bestellungen
                    if (text in b.get("id","").lower() or
                        text in b.get("lieferant","").lower() or
                        text in b.get("artikel","").lower())
                    and (status_f == "Alle Status" or b.get("status","") == status_f)]
        self._populate_table(filtered)

    def _neue_bestellung(self):
        if NeueBestellungDialog(parent=self).exec_():
            self._populate_table(self._store.bestellungen)


# ══════════════════════════════════════════════
#  ARTIKELVERWALTUNG
# ══════════════════════════════════════════════

class ArtikelverwaltungPage(BasePage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        WF = WidgetFactory
        inner, root = self._page_root()

        hdr = QHBoxLayout()
        hdr.addWidget(WF.label("🏷 Artikelverwaltung", 22, bold=True))
        hdr.addStretch()
        b_new = WF.button("+ Neuer Artikel", bg=AppColors.GREEN)
        b_new.clicked.connect(self._neuer_artikel)
        b_csv = WF.button("📊 CSV Export", bg=AppColors.MUTED)
        b_csv.clicked.connect(lambda: CsvExporter.export(
            self._store.artikel,
            ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"],
            "Artikel", self))
        hdr.addWidget(b_new)
        hdr.addWidget(b_csv)
        root.addLayout(hdr)

        # Kategorie-Statistiken
        stats_row = QHBoxLayout()
        kategorien: dict = {}
        for a in self._store.artikel:
            kategorien[a["kategorie"]] = kategorien.get(a["kategorie"], 0) + 1
        for kat, cnt in list(kategorien.items())[:4]:
            sc = WF.card()
            WF.shadow(sc, blur=8)
            scl = QVBoxLayout(sc)
            scl.setContentsMargins(14, 10, 14, 10)
            scl.addWidget(WF.label(str(cnt), 24, bold=True, color=AppColors.BLUE))
            scl.addWidget(WF.label(kat, 10, color=AppColors.MUTED))
            stats_row.addWidget(sc)
        root.addLayout(stats_row)

        f_row = QHBoxLayout()
        self._search = WF.text_input("🔍 Artikel suchen...")
        self._search.textChanged.connect(self._filter)
        self._kat_filter = WF.combo_box(
            ["Alle Kategorien"] + list(set(a["kategorie"] for a in self._store.artikel)))
        self._kat_filter.currentTextChanged.connect(self._filter)
        f_row.addWidget(self._search, 2)
        f_row.addWidget(self._kat_filter, 1)
        root.addLayout(f_row)

        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet("background: transparent;")
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setSpacing(12)
        self._render_artikel_cards(self._store.artikel)
        root.addWidget(self._cards_widget)
        root.addStretch()
        self._wrap_in_scroll(inner)

    def _render_artikel_cards(self, artikel_list: list):
        WF = WidgetFactory
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        ROW_SIZE = 2
        for i in range(0, len(artikel_list), ROW_SIZE):
            row_w = QWidget()
            row_w.setStyleSheet("background: transparent;")
            row_lay = QHBoxLayout(row_w)
            row_lay.setSpacing(16)
            row_lay.setContentsMargins(0, 0, 0, 0)
            for art in artikel_list[i:i+ROW_SIZE]:
                row_lay.addWidget(self._build_artikel_card(art))
            if len(artikel_list[i:i+ROW_SIZE]) < ROW_SIZE:
                row_lay.addStretch()
            self._cards_layout.addWidget(row_w)

    def _build_artikel_card(self, art: dict) -> QFrame:
        WF = WidgetFactory
        c = WF.card()
        WF.shadow(c, blur=10)
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(8)

        top = QHBoxLayout()
        art_icon = AppColors.KATEGORIE_ICONS.get(art["kategorie"], AppColors.KATEGORIE_ICONS_DEFAULT)
        ico_lbl = QLabel(art_icon)
        ico_lbl.setFont(QFont("Segoe UI", 26))
        ico_lbl.setStyleSheet("background: #f0f4ff; border-radius:10px; padding:4px;")
        ico_lbl.setFixedSize(48, 48)
        ico_lbl.setAlignment(Qt.AlignCenter)

        name_col = QVBoxLayout()
        name_col.addWidget(WF.label(art["name"], 13, bold=True))
        name_col.addWidget(WF.label(f"{art['id']} · {art['kategorie']}", 10, color=AppColors.MUTED))

        ratio = art["bestand"] / max(art["min_bestand"], 1)
        if ratio < 0.5:   st_bg, st_fg, st_txt = "#ffeaea","#c0392b","⚠ Kritisch"
        elif ratio < 1.0: st_bg, st_fg, st_txt = "#fff4e0","#b86200","⚠ Niedrig"
        else:             st_bg, st_fg, st_txt = "#e8faf2","#1a8a52","✅ OK"

        top.addWidget(ico_lbl)
        top.addSpacing(10)
        top.addLayout(name_col)
        top.addStretch()
        top.addWidget(WF.badge(st_txt, st_bg, st_fg))
        cl.addLayout(top)

        det_row = QHBoxLayout()
        for det_label_txt, det_val in [
            ("Bestand", f"{art['bestand']} Stk."),
            ("Mindest", f"{art['min_bestand']} Stk."),
            ("Preis",   f"€ {art['preis']:.2f}"),
            ("MHD",     art["mhd"]),
        ]:
            det_col = QVBoxLayout()
            det_col.setSpacing(2)
            det_col.addWidget(WF.label(det_label_txt, 9, color=AppColors.MUTED))
            det_col.addWidget(WF.label(det_val, 12, bold=True))
            det_row.addLayout(det_col)
            det_row.addStretch()
        cl.addLayout(det_row)
        cl.addWidget(WF.label(f"🏭 {art['lieferant']}", 11, color=AppColors.MUTED))

        btn_row = QHBoxLayout()
        for label_txt, color, callback in [
            ("Detail",     AppColors.BLUE,   lambda _, a=art: ArtikelDetailDialog(a, self).exec_()),
            ("Bestellen",  AppColors.GREEN,  lambda _, a=art: NeueBestellungDialog(pre_artikel=a, parent=self).exec_()),
            ("Bearbeiten", AppColors.ORANGE, lambda _, a=art: self._edit_artikel(a)),
        ]:
            b = WF.button(label_txt, bg=color, size=11)
            b.setFixedHeight(30)
            b.clicked.connect(callback)
            btn_row.addWidget(b)
        btn_row.addStretch()
        cl.addLayout(btn_row)
        return c

    def _filter(self):
        txt = self._search.text().lower()
        kat = self._kat_filter.currentText()
        filtered = [a for a in self._store.artikel
                    if (txt in a["name"].lower() or txt in a["id"].lower())
                    and (kat == "Alle Kategorien" or a["kategorie"] == kat)]
        self._render_artikel_cards(filtered)

    def _neuer_artikel(self):
        if NeuerArtikelDialog(self).exec_():
            self._render_artikel_cards(self._store.artikel)

    def _edit_artikel(self, art: dict):
        if ArtikelBearbeitenDialog(art, self).exec_():
            self._render_artikel_cards(self._store.artikel)


# ══════════════════════════════════════════════
#  BESTÄTIGUNG
# ══════════════════════════════════════════════

class BestaetigungPage(BasePage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        WF = WidgetFactory
        inner, root = self._page_root()
        root.addWidget(WF.label("✅ Wareneingang bestätigen", 22, bold=True))
        root.addWidget(WF.label(
            "Hier können eingehende Lieferungen geprüft und bestätigt werden.", 13, color=AppColors.MUTED))

        pending = [b for b in self._store.bestellungen
                   if b.get("status") not in ("Geliefert","Storniert")]

        if not pending:
            c = WF.card()
            cl = QVBoxLayout(c)
            cl.setContentsMargins(30, 40, 30, 40)
            cl.setAlignment(Qt.AlignCenter)
            cl.addWidget(WF.label("✅", 48))
            lbl_ok = WF.label("Alle Bestellungen bestätigt!", 16, bold=True)
            lbl_ok.setAlignment(Qt.AlignCenter)
            cl.addWidget(lbl_ok)
            root.addWidget(c)
        else:
            for best in pending:
                root.addWidget(self._build_pending_card(best))

        root.addStretch()
        self._wrap_in_scroll(inner)

    def _build_pending_card(self, best: dict) -> QFrame:
        WF = WidgetFactory
        c = WF.card()
        cl = QHBoxLayout(c)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(16)

        info = QVBoxLayout()
        info.setSpacing(4)
        top_row = QHBoxLayout()
        top_row.addWidget(WF.label(best["id"], 14, bold=True))
        top_row.addSpacing(8)
        status = best.get("status","–")
        bg, fg = AppColors.STATUS_COLORS.get(status, ("#eee","#333"))
        top_row.addWidget(WF.badge(status, bg, fg))
        top_row.addStretch()
        info.addLayout(top_row)
        info.addWidget(WF.label(f"📦 {best['artikel']}  ·  Menge: {best['menge']}", 12))
        info.addWidget(WF.label(
            f"🏭 {best['lieferant']}  ·  Datum: {best['datum']}  ·  € {best.get('gesamt',0):.2f}",
            11, color=AppColors.MUTED))
        cl.addLayout(info)
        cl.addStretch()

        btn_col = QVBoxLayout()
        for label_txt, color, callback in [
            ("✅ Bestätigen", AppColors.GREEN, lambda _, b=best: self._confirm(b)),
            ("❌ Stornieren", AppColors.RED,   lambda _, b=best: self._stornieren(b)),
            ("Detail",        AppColors.MUTED, lambda _, b=best: BestellungDetailDialog(b, self).exec_()),
        ]:
            b = WF.button(label_txt, bg=color, size=11)
            b.setFixedWidth(140)
            b.clicked.connect(callback)
            btn_col.addWidget(b)
        cl.addLayout(btn_col)
        return c

    def _confirm(self, best: dict):
        idx = self._store.find_bestellung_index(best["id"])
        if idx is not None:
            self._store.bestellungen[idx]["status"] = "Geliefert"
            self._store.save()
            QMessageBox.information(self,"Bestätigt",f"Bestellung {best['id']} als geliefert markiert!")
            self._rebuild()

    def _stornieren(self, best: dict):
        reply = QMessageBox.question(self,"Stornieren",
            f"Bestellung {best['id']} wirklich stornieren?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            idx = self._store.find_bestellung_index(best["id"])
            if idx is not None:
                self._store.bestellungen[idx]["status"] = "Storniert"
                self._store.save()
                self._rebuild()

    def _rebuild(self):
        old = self.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old)
        self._build()


# ══════════════════════════════════════════════
#  ARTIKELLISTE
# ══════════════════════════════════════════════

class ArtikellistePage(BasePage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        WF = WidgetFactory
        inner, root = self._page_root()

        hdr = QHBoxLayout()
        hdr.addWidget(WF.label("📋 Artikelliste", 22, bold=True))
        hdr.addStretch()
        b_csv = WF.button("📊 CSV Export", bg=AppColors.MUTED)
        b_csv.clicked.connect(lambda: CsvExporter.export(
            self._store.artikel,
            ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"],
            "Artikelliste", self))
        hdr.addWidget(b_csv)
        root.addLayout(hdr)

        by_kat: dict = {}
        for a in self._store.artikel:
            by_kat.setdefault(a["kategorie"], []).append(a)

        for kat, artikel in by_kat.items():
            kat_icon = AppColors.KATEGORIE_ICONS.get(kat, AppColors.KATEGORIE_ICONS_DEFAULT)
            cat_header = QHBoxLayout()
            cat_header.addWidget(WF.label(f"{kat_icon} {kat}", 15, bold=True))
            cat_header.addWidget(WF.badge(f"{len(artikel)} Artikel", "#e8f0ff", "#1a5dcf"))
            cat_header.addStretch()
            root.addLayout(cat_header)
            root.addWidget(self._build_kategorie_table(artikel))

        root.addStretch()
        self._wrap_in_scroll(inner)

    def _build_kategorie_table(self, artikel: list) -> QFrame:
        WF = WidgetFactory
        c = WF.card()
        cl = QVBoxLayout(c)
        cl.setContentsMargins(20, 12, 20, 12)

        t = QTableWidget(len(artikel), 7)
        t.setHorizontalHeaderLabels(["ID","Name","Bestand","Mindest","Preis","Lieferant","MHD"])
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.verticalHeader().setVisible(False)
        t.setShowGrid(False)
        t.setAlternatingRowColors(True)
        t.setStyleSheet("""
            QTableWidget { background: transparent; border: none; }
            QHeaderView::section { background:transparent; color:#7b8ea9; font-weight:bold; border:none; padding:4px 8px; border-bottom:1px solid #d8e3f0; }
            QTableWidget::item { padding:7px; border-bottom:1px solid #f0f4f8; color:#1a2a4a; }
            QTableWidget::item:selected { background:#e8f0ff; }
            QTableWidget::item:alternate { background:#f8fafd; }
        """)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for r, art in enumerate(artikel):
            t.setRowHeight(r, 40)
            t.setItem(r, 0, QTableWidgetItem(art["id"]))
            name_item = QTableWidgetItem(art["name"])
            name_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            t.setItem(r, 1, name_item)
            bestand_item = QTableWidgetItem(str(art["bestand"]))
            if art["bestand"] < art["min_bestand"]:
                bestand_item.setForeground(QColor(AppColors.RED))
                bestand_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            else:
                bestand_item.setForeground(QColor(AppColors.GREEN))
            t.setItem(r, 2, bestand_item)
            t.setItem(r, 3, QTableWidgetItem(str(art["min_bestand"])))
            t.setItem(r, 4, QTableWidgetItem(f"€ {art['preis']:.2f}"))
            t.setItem(r, 5, QTableWidgetItem(art["lieferant"]))
            t.setItem(r, 6, QTableWidgetItem(art["mhd"]))

        total_h = sum(t.rowHeight(r) for r in range(len(artikel)))
        t.setFixedHeight(total_h + t.horizontalHeader().height() + 8)
        t.doubleClicked.connect(
            lambda idx, al=artikel: ArtikelDetailDialog(al[idx.row()], self).exec_())
        cl.addWidget(t)
        return c


# ══════════════════════════════════════════════
#  LIEFERANTEN
# ══════════════════════════════════════════════

class LieferantenPage(BasePage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards_area = None
        self._build()

    def _build(self):
        WF = WidgetFactory
        inner, root = self._page_root()

        hdr = QHBoxLayout()
        hdr.addWidget(WF.label("🏭 Lieferanten", 22, bold=True))
        hdr.addStretch()
        b_new = WF.button("+ Neuer Lieferant", bg=AppColors.GREEN)
        b_new.clicked.connect(self._neuer_lieferant)
        b_csv = WF.button("📊 CSV Export", bg=AppColors.MUTED)
        b_csv.clicked.connect(lambda: CsvExporter.export(
            self._store.lieferanten,
            ["name","kontakt","telefon","lieferungen"],
            "Lieferanten", self))
        hdr.addWidget(b_new)
        hdr.addWidget(b_csv)
        root.addLayout(hdr)

        stat_row = QHBoxLayout()
        total_lief = len(self._store.lieferanten)
        total_del  = sum(l.get("lieferungen",0) for l in self._store.lieferanten)
        for st_val, st_name, st_col in [
            (str(total_lief), "Lieferanten",       AppColors.BLUE),
            (str(total_del),  "Lieferungen gesamt", AppColors.GREEN),
        ]:
            sc = WF.card()
            scl = QVBoxLayout(sc)
            scl.setContentsMargins(20, 14, 20, 14)
            scl.addWidget(WF.label(st_val, 28, bold=True, color=st_col))
            scl.addWidget(WF.label(st_name, 11, color=AppColors.MUTED))
            stat_row.addWidget(sc)
        stat_row.addStretch()
        root.addLayout(stat_row)

        self._cards_area = QVBoxLayout()
        self._cards_area.setSpacing(14)
        self._render_cards()
        root.addLayout(self._cards_area)
        root.addStretch()
        self._wrap_in_scroll(inner)

    def _render_cards(self):
        WF = WidgetFactory
        while self._cards_area.count():
            item = self._cards_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for lief in self._store.lieferanten:
            c = WF.card()
            WF.shadow(c, blur=10)
            cl = QHBoxLayout(c)
            cl.setContentsMargins(20, 16, 20, 16)
            cl.setSpacing(16)

            ico = QLabel("🏭")
            ico.setFont(QFont("Segoe UI", 28))
            ico.setFixedSize(56, 56)
            ico.setAlignment(Qt.AlignCenter)
            ico.setStyleSheet("background: #f0f4ff; border-radius: 12px;")

            info = QVBoxLayout()
            info.setSpacing(4)
            info.addWidget(WF.label(lief["name"], 15, bold=True))
            info.addWidget(WF.label(f"✉ {lief['kontakt']}", 11, color=AppColors.MUTED))
            info.addWidget(WF.label(f"📞 {lief['telefon']}", 11, color=AppColors.MUTED))

            stat_col = QVBoxLayout()
            stat_col.setAlignment(Qt.AlignCenter)
            stat_col.addWidget(WF.label(str(lief.get("lieferungen",0)), 24, bold=True, color=AppColors.BLUE))
            stat_col.addWidget(WF.label("Lieferungen", 10, color=AppColors.MUTED))

            action_col = QVBoxLayout()
            action_col.setSpacing(6)
            b_best = WF.button("📦 Bestellen", bg=AppColors.GREEN, size=11)
            b_best.setFixedWidth(130)
            b_best.clicked.connect(lambda: NeueBestellungDialog(parent=self).exec_())
            b_edit = WF.button("✏ Bearbeiten", bg=AppColors.BLUE, size=11)
            b_edit.setFixedWidth(130)
            b_edit.clicked.connect(lambda _, l=lief: self._edit_lieferant(l))
            action_col.addWidget(b_best)
            action_col.addWidget(b_edit)

            cl.addWidget(ico)
            cl.addLayout(info)
            cl.addStretch()
            cl.addLayout(stat_col)
            cl.addSpacing(20)
            cl.addLayout(action_col)
            self._cards_area.addWidget(c)

    def _neuer_lieferant(self):
        if LieferantDialog(parent=self).exec_():
            self._render_cards()

    def _edit_lieferant(self, lief: dict):
        if LieferantDialog(lieferant=lief, parent=self).exec_():
            self._render_cards()


# ══════════════════════════════════════════════
#  BERICHTE
# ══════════════════════════════════════════════

class BerichtePage(BasePage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        WF = WidgetFactory
        inner, root = self._page_root()
        root.addWidget(WF.label("📊 Berichte & Exports", 22, bold=True))

        exports = [
            ("📦 Lagerbestand exportieren",   "Alle Artikel mit Bestand, MHD und Preisen", AppColors.BLUE,
             lambda: CsvExporter.export(self._store.artikel,
                ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"],"Lagerbestand",self)),
            ("🛒 Bestellungen exportieren",    "Alle Bestellungen mit Status und Beträgen", AppColors.GREEN,
             lambda: CsvExporter.export(self._store.bestellungen,
                ["id","datum","lieferant","artikel","menge","status","gesamt"],"Bestellungen",self)),
            ("🏭 Lieferanten exportieren",     "Alle Lieferanten mit Kontaktdaten",         AppColors.ORANGE,
             lambda: CsvExporter.export(self._store.lieferanten,
                ["name","kontakt","telefon","lieferungen"],"Lieferanten",self)),
            ("⚠ Kritische Artikel exportieren","Artikel unter Mindestbestand",             AppColors.RED,
             lambda: CsvExporter.export(
                [a for a in self._store.artikel if a["bestand"]<a["min_bestand"]],
                ["id","name","bestand","min_bestand","lieferant"],"Kritische_Artikel",self)),
        ]

        for exp_title, exp_desc, exp_color, exp_fn in exports:
            c = WF.card()
            cl = QHBoxLayout(c)
            cl.setContentsMargins(20, 16, 20, 16)
            info = QVBoxLayout()
            info.addWidget(WF.label(exp_title, 14, bold=True))
            info.addWidget(WF.label(exp_desc, 11, color=AppColors.MUTED))
            b = WF.button("📊 CSV herunterladen", bg=exp_color)
            b.setFixedWidth(200)
            b.clicked.connect(exp_fn)
            cl.addLayout(info)
            cl.addStretch()
            cl.addWidget(b)
            root.addWidget(c)

        stat_c = WF.card()
        stat_l = QVBoxLayout(stat_c)
        stat_l.setContentsMargins(20, 18, 20, 18)
        stat_l.addWidget(WF.label("📈 Statistiken", 14, bold=True))
        stat_l.addSpacing(10)

        total_bestand = sum(a["bestand"] for a in self._store.artikel)
        krit          = sum(1 for a in self._store.artikel if a["bestand"] < a["min_bestand"])
        total_best    = len(self._store.bestellungen)
        gesamt_wert   = sum(b.get("gesamt",0) for b in self._store.bestellungen)

        stat_row = QHBoxLayout()
        for st_name, st_val, st_col in [
            ("Gesamtartikel",      str(len(self._store.artikel)), AppColors.BLUE),
            ("Gesamtbestand",      str(total_bestand),            AppColors.GREEN),
            ("Kritische Artikel",  str(krit),                     AppColors.RED),
            ("Bestellungen gesamt",str(total_best),               AppColors.ORANGE),
            ("Bestellwert gesamt", f"€ {gesamt_wert:.2f}",        AppColors.BLUE),
        ]:
            sc = WF.card()
            WF.shadow(sc, blur=8)
            scl = QVBoxLayout(sc)
            scl.setContentsMargins(16, 12, 16, 12)
            scl.addWidget(WF.label(st_val, 22, bold=True, color=st_col))
            scl.addWidget(WF.label(st_name, 10, color=AppColors.MUTED))
            stat_row.addWidget(sc)

        stat_l.addLayout(stat_row)
        root.addWidget(stat_c)
        root.addStretch()
        self._wrap_in_scroll(inner)


# ══════════════════════════════════════════════
#  EINSTELLUNGEN
# ══════════════════════════════════════════════

class EinstellungenPage(BasePage):

    def __init__(self, music_player: MusicPlayer = None, parent=None):
        super().__init__(parent)
        self._music_ref = music_player
        self._build()

    def _build(self):
        WF = WidgetFactory
        inner, root = self._page_root()
        root.addWidget(WF.label("⚙ Einstellungen", 22, bold=True))
        root.addWidget(self._build_music_card())
        root.addWidget(self._build_data_card())
        root.addWidget(self._build_info_card())
        root.addStretch()
        self._wrap_in_scroll(inner)

    def _build_music_card(self) -> QFrame:
        WF = WidgetFactory
        mc = WF.card()
        ml = QVBoxLayout(mc)
        ml.setContentsMargins(24, 20, 24, 20)
        ml.setSpacing(12)
        ml.addWidget(WF.label("🎵 Hintergrundmusik", 15, bold=True))
        ml.addWidget(WF.label(
            "Lo-Fi Ambient Musik – wird automatisch generiert und loopend abgespielt.", 12, color=AppColors.MUTED))
        ctrl = QHBoxLayout()
        b_play = WF.button("▶ Musik starten", bg=AppColors.BLUE)
        b_play.clicked.connect(lambda: self._music_ref._play() if self._music_ref else None)
        b_stop = WF.button("⏹ Stoppen", bg=AppColors.RED)
        b_stop.clicked.connect(lambda: self._music_ref._stop() if self._music_ref else None)
        ctrl.addWidget(b_play)
        ctrl.addWidget(b_stop)
        ctrl.addStretch()
        ml.addLayout(ctrl)
        vol_row = QHBoxLayout()
        vol_row.addWidget(WF.label("Lautstärke:", 12, bold=True, color=AppColors.MUTED))
        for pct in [25, 50, 75, 100]:
            bv = WF.button(f"{pct}%", bg="#e0e7f0", fg=AppColors.TEXT, size=11)
            bv.setFixedWidth(60)
            bv.clicked.connect(lambda _, p=pct: self._music_ref._set_volume(p/100) if self._music_ref else None)
            vol_row.addWidget(bv)
        vol_row.addStretch()
        ml.addLayout(vol_row)
        if not MUSIC_AVAILABLE:
            ml.addWidget(WF.label("⚠ pygame nicht installiert. Bitte: pip install pygame", 11, color=AppColors.RED))
        return mc

    def _build_data_card(self) -> QFrame:
        WF = WidgetFactory
        dc = WF.card()
        dl = QVBoxLayout(dc)
        dl.setContentsMargins(24, 20, 24, 20)
        dl.setSpacing(12)
        dl.addWidget(WF.label("💾 Datenverwaltung", 15, bold=True))
        dl.addWidget(WF.label(f"Datendatei: {DataStore.DATA_FILE}", 11, color=AppColors.MUTED))
        dat_row = QHBoxLayout()
        b_backup = WF.button("📦 Backup erstellen", bg=AppColors.GREEN)
        b_backup.clicked.connect(self._backup)
        b_reset = WF.button("🔄 Daten zurücksetzen", bg=AppColors.RED)
        b_reset.clicked.connect(self._reset)
        dat_row.addWidget(b_backup)
        dat_row.addWidget(b_reset)
        dat_row.addStretch()
        dl.addLayout(dat_row)
        return dc

    def _build_info_card(self) -> QFrame:
        WF = WidgetFactory
        ic = WF.card()
        il = QVBoxLayout(ic)
        il.setContentsMargins(24, 20, 24, 20)
        il.setSpacing(8)
        il.addWidget(WF.label("ℹ LagerPro Software", 15, bold=True))
        for line in [
            "Version: 2.0 – Vollausbau",
            "Framework: PyQt5",
            "PDF-Export: reportlab",
            "Musik: pygame + generiertes Lo-Fi WAV",
            "Daten: lokal als JSON gespeichert",
        ]:
            il.addWidget(WF.label(f"· {line}", 12, color=AppColors.MUTED))
        return ic

    def _backup(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Backup speichern", "lagerpro_backup.json", "JSON (*.json)")
        if path:
            try:
                DataStore.instance().backup(path)
                QMessageBox.information(self, "Backup", f"Backup gespeichert:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def _reset(self):
        reply = QMessageBox.question(self, "Zurücksetzen",
            "Wirklich alle Daten auf Standard zurücksetzen?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            DataStore.instance().reset()
            QMessageBox.information(self, "Zurückgesetzt",
                "Daten wurden zurückgesetzt. Bitte App neu starten.")
