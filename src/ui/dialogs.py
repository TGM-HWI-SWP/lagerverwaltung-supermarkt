"""
LagerPro – Dialoge
==================
ArtikelDetailDialog      : Details + Nachbestellung eines Artikels
NeueBestellungDialog     : Neue Bestellung erfassen
BestellungDetailDialog   : Details einer Bestellung
NeuerArtikelDialog       : Neuen Artikel anlegen
ArtikelBearbeitenDialog  : Artikel bearbeiten / löschen
LieferantDialog          : Lieferant anlegen / bearbeiten
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTextEdit, QMessageBox,
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont

from .colors import AppColors
from .data_store import DataStore
from .exporters import CsvExporter, PdfExporter
from .widget_factory import WidgetFactory


class ArtikelDetailDialog(QDialog):
    """Zeigt alle Details eines Artikels. Ermöglicht Nachbestellung und CSV-Export."""

    def __init__(self, artikel: dict, parent=None):
        super().__init__(parent)
        self._artikel = artikel
        self.setWindowTitle(f"Artikeldetail – {artikel['name']}")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"background: {AppColors.PAGE};")
        self._build_ui()

    def _build_ui(self):
        WF = WidgetFactory
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        lay.addWidget(WF.label(self._artikel["name"], 18, bold=True))

        c = WF.card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)
        for lbl_text, val in [
            ("Artikel-ID:",         self._artikel["id"]),
            ("Kategorie:",          self._artikel["kategorie"]),
            ("Aktueller Bestand:",  f"{self._artikel['bestand']} Stück"),
            ("Mindestbestand:",     f"{self._artikel['min_bestand']} Stück"),
            ("Preis:",              f"€ {self._artikel['preis']:.2f}"),
            ("Lieferant:",          self._artikel["lieferant"]),
            ("MHD:",                self._artikel["mhd"]),
        ]:
            fl.addRow(WF.label(lbl_text, 12, bold=True, color=AppColors.MUTED), WF.label(val, 12))
        lay.addWidget(c)

        ratio = self._artikel["bestand"] / max(self._artikel["min_bestand"], 1)
        if ratio < 0.5:   st_text, st_bg, st_fg = "⚠ Kritisch niedrig",       "#ffeaea", "#c0392b"
        elif ratio < 1.0: st_text, st_bg, st_fg = "⚠ Unter Mindestbestand",   "#fff4e0", "#b86200"
        else:             st_text, st_bg, st_fg = "✅ Bestand OK",              "#e8faf2", "#1a8a52"
        status_lbl = WF.badge(st_text, st_bg, st_fg)
        status_lbl.setFixedHeight(32)
        lay.addWidget(status_lbl)

        btn_row = QHBoxLayout()
        b_bestell = WF.button("📦 Nachbestellen", AppColors.BLUE)
        b_bestell.clicked.connect(self._nachbestellen)
        b_csv = WF.button("📊 CSV Export", AppColors.GREEN)
        b_csv.clicked.connect(lambda: CsvExporter.export(
            [self._artikel],
            ["id","name","kategorie","bestand","min_bestand","preis","lieferant","mhd"],
            f"Artikel_{self._artikel['id']}", self))
        b_close = WF.button("Schließen", bg="#e0e7f0", fg=AppColors.TEXT)
        b_close.clicked.connect(self.close)
        btn_row.addWidget(b_bestell)
        btn_row.addWidget(b_csv)
        btn_row.addStretch()
        btn_row.addWidget(b_close)
        lay.addLayout(btn_row)

    def _nachbestellen(self):
        NeueBestellungDialog(pre_artikel=self._artikel, parent=self).exec_()


class NeueBestellungDialog(QDialog):
    """Formular zum Erfassen einer neuen Bestellung."""

    def __init__(self, pre_artikel: dict = None, parent=None):
        super().__init__(parent)
        self._store = DataStore.instance()
        self.setWindowTitle("Neue Bestellung aufgeben")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background: {AppColors.PAGE};")
        self._build_ui(pre_artikel)

    def _build_ui(self, pre_artikel):
        WF = WidgetFactory
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        lay.addWidget(WF.label("📦 Neue Bestellung", 18, bold=True))

        c = WF.card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        lieferanten = self._store.lieferanten_namen()
        self._cb_lieferant = WF.combo_box(lieferanten)

        artikel_namen = self._store.artikel_namen()
        self._cb_artikel = WF.combo_box(artikel_namen)

        if pre_artikel:
            if pre_artikel["name"] in artikel_namen:
                self._cb_artikel.setCurrentIndex(artikel_namen.index(pre_artikel["name"]))
            if pre_artikel.get("lieferant") in lieferanten:
                self._cb_lieferant.setCurrentIndex(lieferanten.index(pre_artikel["lieferant"]))

        self._sp_menge  = WF.spin_box(1, 99999, 100)
        self._sp_preis  = WF.double_spin_box(
            0.01, 999999.99,
            pre_artikel.get("preis", 1.0) * 100 if pre_artikel else 100.0)
        self._de_datum  = WF.date_edit()
        self._cb_status = WF.combo_box(["Unterwegs","Ausstehend","Anrufen","Geliefert","Storniert"])

        self._te_notiz = QTextEdit()
        self._te_notiz.setPlaceholderText("Optionale Notizen zur Bestellung...")
        self._te_notiz.setFont(QFont("Segoe UI", 12))
        self._te_notiz.setFixedHeight(80)
        self._te_notiz.setStyleSheet(
            "QTextEdit { background:#f4f7fb; border:1.5px solid #d8e3f0; border-radius:8px; padding:8px; }")

        for row_label, widget in [
            ("Lieferant:",    self._cb_lieferant),
            ("Artikel:",      self._cb_artikel),
            ("Menge:",        self._sp_menge),
            ("Gesamtbetrag:", self._sp_preis),
            ("Datum:",        self._de_datum),
            ("Status:",       self._cb_status),
            ("Notizen:",      self._te_notiz),
        ]:
            fl.addRow(WF.label(row_label, 12, bold=True, color=AppColors.MUTED), widget)
        lay.addWidget(c)

        btn_row = QHBoxLayout()
        b_save   = WF.button("💾 Bestellung speichern", AppColors.GREEN)
        b_save.clicked.connect(self._save)
        b_pdf    = WF.button("🖨 Speichern & PDF", AppColors.BLUE)
        b_pdf.clicked.connect(lambda: self._save(print_pdf=True))
        b_cancel = WF.button("Abbrechen", bg="#e0e7f0", fg=AppColors.TEXT)
        b_cancel.clicked.connect(self.reject)
        btn_row.addWidget(b_save)
        btn_row.addWidget(b_pdf)
        btn_row.addStretch()
        btn_row.addWidget(b_cancel)
        lay.addLayout(btn_row)

    def _save(self, print_pdf: bool = False):
        bestellung = {
            "id":        self._store.next_bestellung_id(),
            "datum":     self._de_datum.date().toString("yyyy-MM-dd"),
            "lieferant": self._cb_lieferant.currentText(),
            "artikel":   self._cb_artikel.currentText(),
            "menge":     self._sp_menge.value(),
            "status":    self._cb_status.currentText(),
            "gesamt":    round(self._sp_preis.value(), 2),
            "notiz":     self._te_notiz.toPlainText(),
        }
        self._store.bestellungen.append(bestellung)
        self._store.save()
        if print_pdf:
            PdfExporter.export_bestellung(bestellung, self)
        else:
            QMessageBox.information(self, "Gespeichert",
                f"Bestellung {bestellung['id']} wurde erfolgreich gespeichert!")
        self.accept()


class BestellungDetailDialog(QDialog):
    """Zeigt alle Details einer Bestellung."""

    def __init__(self, bestellung: dict, parent=None):
        super().__init__(parent)
        self._bestellung = bestellung
        self.setWindowTitle(f"Bestelldetail – {bestellung['id']}")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background: {AppColors.PAGE};")
        self._build_ui()

    def _build_ui(self):
        WF = WidgetFactory
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        lay.addWidget(WF.label(f"Bestellung {self._bestellung['id']}", 18, bold=True))

        c = WF.card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)
        for lbl_text, val in [
            ("Bestell-ID:",   self._bestellung.get("id","–")),
            ("Datum:",        self._bestellung.get("datum","–")),
            ("Lieferant:",    self._bestellung.get("lieferant","–")),
            ("Artikel:",      self._bestellung.get("artikel","–")),
            ("Menge:",        str(self._bestellung.get("menge","–"))),
            ("Gesamtbetrag:", f"€ {self._bestellung.get('gesamt',0):.2f}"),
            ("Notizen:",      self._bestellung.get("notiz","–") or "–"),
        ]:
            fl.addRow(WF.label(lbl_text, 12, bold=True, color=AppColors.MUTED), WF.label(val, 12))

        status = self._bestellung.get("status","–")
        bg, fg = AppColors.STATUS_COLORS.get(status, ("#eee","#333"))
        status_badge = WF.badge(f"Status: {status}", bg, fg)
        status_badge.setFixedHeight(32)
        fl.addRow(WF.label("Status:", 12, bold=True, color=AppColors.MUTED), status_badge)
        lay.addWidget(c)

        btn_row = QHBoxLayout()
        b_pdf   = WF.button("🖨 Als PDF drucken", AppColors.BLUE)
        b_pdf.clicked.connect(lambda: PdfExporter.export_bestellung(self._bestellung, self))
        b_csv   = WF.button("📊 CSV Export", AppColors.GREEN)
        b_csv.clicked.connect(lambda: CsvExporter.export(
            [self._bestellung],
            ["id","datum","lieferant","artikel","menge","status","gesamt"],
            f"Bestellung_{self._bestellung['id'].replace('#','')}", self))
        b_close = WF.button("Schließen", bg="#e0e7f0", fg=AppColors.TEXT)
        b_close.clicked.connect(self.close)
        btn_row.addWidget(b_pdf)
        btn_row.addWidget(b_csv)
        btn_row.addStretch()
        btn_row.addWidget(b_close)
        lay.addLayout(btn_row)


class NeuerArtikelDialog(QDialog):
    """Formular zum Anlegen eines neuen Artikels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._store = DataStore.instance()
        self.setWindowTitle("Neuen Artikel anlegen")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"background: {AppColors.PAGE};")
        self._build_ui()

    def _build_ui(self):
        WF = WidgetFactory
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        lay.addWidget(WF.label("🏷 Neuer Artikel", 18, bold=True))

        c = WF.card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        self._f_name    = WF.text_input("Artikelname")
        self._f_id      = WF.text_input("Artikel-ID (z.B. ABC123)")
        self._f_kat     = WF.combo_box(AppColors.KATEGORIEN)
        self._f_bestand = WF.spin_box(0, 99999, 0)
        self._f_min     = WF.spin_box(0, 99999, 20)
        self._f_preis   = WF.double_spin_box(0.01, 99999.0, 1.0)
        self._f_lief    = WF.combo_box(self._store.lieferanten_namen())
        self._f_mhd     = WF.date_edit(QDate.currentDate().addDays(30))

        for lbl_text, widget in [
            ("Name:",          self._f_name),
            ("ID:",            self._f_id),
            ("Kategorie:",     self._f_kat),
            ("Bestand:",       self._f_bestand),
            ("Mindestbestand:",self._f_min),
            ("Preis:",         self._f_preis),
            ("Lieferant:",     self._f_lief),
            ("MHD:",           self._f_mhd),
        ]:
            fl.addRow(WF.label(lbl_text, 12, bold=True, color=AppColors.MUTED), widget)
        lay.addWidget(c)

        btn_row = QHBoxLayout()
        b_save   = WF.button("💾 Speichern", AppColors.GREEN)
        b_save.clicked.connect(self._save)
        b_cancel = WF.button("Abbrechen", bg="#e0e7f0", fg=AppColors.TEXT)
        b_cancel.clicked.connect(self.reject)
        btn_row.addWidget(b_save)
        btn_row.addStretch()
        btn_row.addWidget(b_cancel)
        lay.addLayout(btn_row)

    def _save(self):
        if not self._f_name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Artikelname eingeben!")
            return
        if not self._f_id.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Artikel-ID eingeben!")
            return
        new_art = {
            "id":          self._f_id.text().strip(),
            "name":        self._f_name.text().strip(),
            "kategorie":   self._f_kat.currentText(),
            "bestand":     self._f_bestand.value(),
            "min_bestand": self._f_min.value(),
            "preis":       self._f_preis.value(),
            "lieferant":   self._f_lief.currentText(),
            "mhd":         self._f_mhd.date().toString("yyyy-MM-dd"),
        }
        self._store.artikel.append(new_art)
        self._store.save()
        QMessageBox.information(self, "Gespeichert", f"Artikel '{new_art['name']}' wurde angelegt!")
        self.accept()


class ArtikelBearbeitenDialog(QDialog):
    """Formular zum Bearbeiten oder Löschen eines Artikels."""

    def __init__(self, artikel: dict, parent=None):
        super().__init__(parent)
        self._artikel  = artikel
        self._store    = DataStore.instance()
        self._art_idx  = self._store.find_artikel_index(artikel["id"])
        self.setWindowTitle(f"Artikel bearbeiten – {artikel['name']}")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"background: {AppColors.PAGE};")
        self._build_ui()

    def _build_ui(self):
        WF = WidgetFactory
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        lay.addWidget(WF.label(f"✏ {self._artikel['name']}", 18, bold=True))

        c = WF.card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        self._f_name = WF.text_input()
        self._f_name.setText(self._artikel["name"])
        self._f_kat = WF.combo_box(AppColors.KATEGORIEN)
        idx = self._f_kat.findText(self._artikel["kategorie"])
        if idx >= 0:
            self._f_kat.setCurrentIndex(idx)
        self._f_bestand = WF.spin_box(0, 99999, self._artikel["bestand"])
        self._f_min     = WF.spin_box(0, 99999, self._artikel["min_bestand"])
        self._f_preis   = WF.double_spin_box(0.01, 99999.0, self._artikel["preis"])
        self._f_lief    = WF.combo_box(self._store.lieferanten_namen())
        li = self._f_lief.findText(self._artikel["lieferant"])
        if li >= 0:
            self._f_lief.setCurrentIndex(li)
        try:
            mhd_date = __import__("PyQt5.QtCore", fromlist=["QDate"]).QDate.fromString(
                self._artikel["mhd"], "yyyy-MM-dd")
        except Exception:
            from PyQt5.QtCore import QDate
            mhd_date = QDate.currentDate()
        self._f_mhd = WF.date_edit(mhd_date)

        for lbl_text, widget in [
            ("Name:",          self._f_name),
            ("Kategorie:",     self._f_kat),
            ("Bestand:",       self._f_bestand),
            ("Mindestbestand:",self._f_min),
            ("Preis:",         self._f_preis),
            ("Lieferant:",     self._f_lief),
            ("MHD:",           self._f_mhd),
        ]:
            fl.addRow(WF.label(lbl_text, 12, bold=True, color=AppColors.MUTED), widget)
        lay.addWidget(c)

        btn_row = QHBoxLayout()
        b_save   = WF.button("💾 Speichern", AppColors.GREEN)
        b_save.clicked.connect(self._save)
        b_del    = WF.button("🗑 Löschen", AppColors.RED)
        b_del.clicked.connect(self._delete)
        b_cancel = WF.button("Abbrechen", bg="#e0e7f0", fg=AppColors.TEXT)
        b_cancel.clicked.connect(self.reject)
        btn_row.addWidget(b_save)
        btn_row.addWidget(b_del)
        btn_row.addStretch()
        btn_row.addWidget(b_cancel)
        lay.addLayout(btn_row)

    def _save(self):
        if self._art_idx is not None:
            self._store.artikel[self._art_idx].update({
                "name":        self._f_name.text().strip(),
                "kategorie":   self._f_kat.currentText(),
                "bestand":     self._f_bestand.value(),
                "min_bestand": self._f_min.value(),
                "preis":       self._f_preis.value(),
                "lieferant":   self._f_lief.currentText(),
                "mhd":         self._f_mhd.date().toString("yyyy-MM-dd"),
            })
            self._store.save()
            QMessageBox.information(self, "Gespeichert", "Artikel wurde aktualisiert!")
            self.accept()

    def _delete(self):
        reply = QMessageBox.question(self, "Löschen",
            f"Artikel '{self._artikel['name']}' wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes and self._art_idx is not None:
            self._store.artikel.pop(self._art_idx)
            self._store.save()
            self.accept()


class LieferantDialog(QDialog):
    """Formular zum Anlegen oder Bearbeiten eines Lieferanten."""

    def __init__(self, lieferant: dict = None, parent=None):
        super().__init__(parent)
        self._lieferant = lieferant
        self._store     = DataStore.instance()
        self._lief_idx  = self._store.find_lieferant_index(lieferant["name"]) if lieferant else None
        self.setWindowTitle("Lieferant bearbeiten" if lieferant else "Neuer Lieferant")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"background: {AppColors.PAGE};")
        self._build_ui()

    def _build_ui(self):
        WF = WidgetFactory
        title = "Lieferant bearbeiten" if self._lieferant else "Neuer Lieferant"
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        lay.addWidget(WF.label(f"🏭 {title}", 17, bold=True))

        c = WF.card()
        fl = QFormLayout(c)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        self._f_name    = WF.text_input("Firmenname")
        self._f_kontakt = WF.text_input("E-Mail Adresse")
        self._f_tel     = WF.text_input("Telefonnummer")
        self._f_lief    = WF.spin_box(0, 9999, 0)

        if self._lieferant:
            self._f_name.setText(self._lieferant.get("name",""))
            self._f_kontakt.setText(self._lieferant.get("kontakt",""))
            self._f_tel.setText(self._lieferant.get("telefon",""))
            self._f_lief.setValue(self._lieferant.get("lieferungen",0))

        for lbl_text, widget in [
            ("Firma:",       self._f_name),
            ("E-Mail:",      self._f_kontakt),
            ("Telefon:",     self._f_tel),
            ("Lieferungen:", self._f_lief),
        ]:
            fl.addRow(WF.label(lbl_text, 12, bold=True, color=AppColors.MUTED), widget)
        lay.addWidget(c)

        btn_row = QHBoxLayout()
        b_save = WF.button("💾 Speichern", AppColors.GREEN)
        b_save.clicked.connect(self._save)
        if self._lieferant:
            b_del = WF.button("🗑 Löschen", AppColors.RED)
            b_del.clicked.connect(self._delete)
            btn_row.addWidget(b_del)
        b_cancel = WF.button("Abbrechen", bg="#e0e7f0", fg=AppColors.TEXT)
        b_cancel.clicked.connect(self.reject)
        btn_row.addWidget(b_save)
        btn_row.addStretch()
        btn_row.addWidget(b_cancel)
        lay.addLayout(btn_row)

    def _save(self):
        if not self._f_name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Firmenname eingeben!")
            return
        data = {
            "name":        self._f_name.text().strip(),
            "kontakt":     self._f_kontakt.text().strip(),
            "telefon":     self._f_tel.text().strip(),
            "lieferungen": self._f_lief.value(),
        }
        if self._lief_idx is not None:
            self._store.lieferanten[self._lief_idx] = data
        else:
            self._store.lieferanten.append(data)
        self._store.save()
        self.accept()

    def _delete(self):
        reply = QMessageBox.question(self, "Löschen",
            f"Lieferant '{self._lieferant['name']}' löschen?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes and self._lief_idx is not None:
            self._store.lieferanten.pop(self._lief_idx)
            self._store.save()
            self.accept()
