"""
LagerPro – Exporters
====================
CSV- und PDF-Export-Logik, vollständig von der UI getrennt.
"""

import csv
import datetime

from PyQt5.QtWidgets import QFileDialog, QMessageBox


class CsvExporter:
    """Exportiert beliebige Datensätze als CSV-Datei."""

    @staticmethod
    def export(data: list, headers: list, title: str = "Export", parent=None):
        path, _ = QFileDialog.getSaveFileName(
            parent, f"CSV exportieren – {title}", f"{title}.csv", "CSV Dateien (*.csv)"
        )
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


class PdfExporter:
    """Erstellt PDF-Bestellscheine mit reportlab."""

    @staticmethod
    def export_bestellung(bestellung: dict, parent=None):
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

        path, _ = QFileDialog.getSaveFileName(
            parent, "Bestellung als PDF speichern",
            f"Bestellung_{bestellung['id'].replace('#','')}.pdf", "PDF Dateien (*.pdf)"
        )
        if not path:
            return

        try:
            doc = SimpleDocTemplate(path, pagesize=A4,
                leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            styles = getSampleStyleSheet()
            story = []

            title_style = ParagraphStyle("title", parent=styles["Title"],
                fontSize=22, textColor=colors.HexColor("#0c2145"), spaceAfter=6)
            story.append(Paragraph("🤖 LAGERPRO – Bestellschein", title_style))

            sub_style = ParagraphStyle("sub", parent=styles["Normal"],
                fontSize=10, textColor=colors.HexColor("#7b8ea9"), spaceAfter=20)
            story.append(Paragraph(
                f"Erstellt am: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr", sub_style))
            story.append(Spacer(1, 0.3*cm))

            info_data = [
                ["Bestell-ID:",   bestellung.get("id", "–")],
                ["Datum:",        bestellung.get("datum", "–")],
                ["Lieferant:",    bestellung.get("lieferant", "–")],
                ["Artikel:",      bestellung.get("artikel", "–")],
                ["Menge:",        str(bestellung.get("menge", "–"))],
                ["Status:",       bestellung.get("status", "–")],
                ["Gesamtbetrag:", f"€ {bestellung.get('gesamt', 0):.2f}"],
            ]
            info_table = Table(info_data, colWidths=[5*cm, 12*cm])
            info_table.setStyle(TableStyle([
                ("FONTNAME",       (0,0), (-1,-1), "Helvetica"),
                ("FONTSIZE",       (0,0), (-1,-1), 11),
                ("FONTNAME",       (0,0), (0,-1),  "Helvetica-Bold"),
                ("TEXTCOLOR",      (0,0), (0,-1),  colors.HexColor("#0c2145")),
                ("TEXTCOLOR",      (1,0), (1,-1),  colors.HexColor("#1a2a4a")),
                ("ROWBACKGROUNDS", (0,0), (-1,-1),  [colors.HexColor("#f4f7fb"), colors.white]),
                ("GRID",           (0,0), (-1,-1), 0.5, colors.HexColor("#d8e3f0")),
                ("TOPPADDING",     (0,0), (-1,-1), 8),
                ("BOTTOMPADDING",  (0,0), (-1,-1), 8),
                ("LEFTPADDING",    (0,0), (-1,-1), 10),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 1*cm))

            footer_style = ParagraphStyle("footer", parent=styles["Normal"],
                fontSize=9, textColor=colors.HexColor("#7b8ea9"))
            story.append(Paragraph(
                "LagerPro Software – Automatisch generierter Bestellschein", footer_style))

            doc.build(story)
            QMessageBox.information(parent, "PDF erstellt", f"PDF gespeichert:\n{path}")

        except Exception as e:
            QMessageBox.critical(parent, "PDF Fehler", str(e))
