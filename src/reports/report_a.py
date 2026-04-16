"""
Report A – Lagerstandsreport (Rolle 2)
=======================================
Dieser Report ist eine eigene Komponente – kein Print im Controller.
Er ist deterministisch (gleiche Daten → gleicher Output) und testbar.

Ausgabeformate:
  - render_text()  → reiner Text (Konsole)
  - render_html()  → HTML-Datei (Browser / als PDF drucken)
  - save_html()    → speichert HTML direkt als Datei
"""

from __future__ import annotations  # erlaubt Typen als Strings (Kompatibilität ältere Python-Versionen)

from dataclasses import dataclass   # generiert __init__, __repr__, __eq__ automatisch
from datetime import datetime       # für den Zeitstempel im Report-Header
from typing import List             # für List[InventoryReportRow] als Typangabe

from ..domain.product import Product    # Domain-Modell: ein Produkt im Lager
from ..ports import RepositoryPort      # abstrakter Port – kein konkretes Repository!


# ---------------------------------------------------------------------------
# Datenklassen – repräsentieren das Report-Ergebnis
# frozen=True = unveränderlich nach Erstellung (immutable)
# Warum frozen? Report-Ergebnisse sollen nach der Berechnung fix sein.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InventoryReportRow:
    """Eine einzelne Zeile im Report – entspricht genau einem Produkt."""
    product_id: str     # eindeutige ID, z.B. "MILCH-01"
    name: str           # lesbarer Name, z.B. "Vollmilch"
    category: str       # Kategorie, z.B. "Molkerei"
    quantity: int       # aktueller Bestand in Stück
    min_quantity: int   # Mindestbestand – unter dem Wert → Status LOW
    price: float        # Preis pro Stück in €
    total_value: float  # Gesamtwert = price * quantity
    status: str         # "OK" | "LOW" | "OUT"


@dataclass(frozen=True)
class InventoryReportResult:
    """Das gesamte Ergebnis: alle Zeilen + aggregierte Kennzahlen."""
    rows: List[InventoryReportRow]  # alle Produkt-Zeilen, alphabetisch sortiert
    product_count: int              # Gesamtanzahl Produkte
    low_stock_count: int            # Anzahl Produkte mit Status LOW
    out_of_stock_count: int         # Anzahl Produkte mit Status OUT
    ok_count: int                   # Anzahl Produkte mit Status OK
    total_inventory_value: float    # Gesamtlagerwert = Summe aller total_value
    generated_at: str               # Zeitstempel, z.B. "2026-04-16 10:30:00"


# ---------------------------------------------------------------------------
# Hauptklasse
# ---------------------------------------------------------------------------

class InventoryReport:
    """
    Report A: Lagerstandsreport.

    Prinzip der Trennung von Logik und Darstellung:
      generate()     → berechnet Daten  →  InventoryReportResult (testbar!)
      render_text()  → formatiert als Text   (Konsole)
      render_html()  → formatiert als HTML   (Browser / PDF)
      save_html()    → speichert HTML als Datei
    """

    def __init__(self, repository: RepositoryPort):
        """
        Dependency Injection: Repository kommt von außen.
        InventoryReport kennt nur den Port, nicht den konkreten Adapter.
        Im Test: InMemoryRepository. In Produktion: JsonFileRepository.
        """
        self._repository = repository  # _ = privates Attribut (Konvention)

    @staticmethod  # kein self nötig – braucht nur das product-Objekt
    def _status_for(product: Product) -> str:
        """
        Status eines Produkts bestimmen. Reihenfolge ist wichtig!
        OUT hat Vorrang – leerer Bestand ist IMMER OUT.

        Randfälle:
          quantity=0, min_quantity=5  → OUT  (nicht LOW! OUT hat Vorrang)
          quantity=5, min_quantity=5  → OK   (genau gleich = noch ausreichend)
          quantity=3, min_quantity=0  → OK   (kein Mindestbestand → nie LOW)
        """
        if product.quantity <= 0:
            return "OUT"  # leer → immer OUT, egal ob min_quantity gesetzt

        if product.min_quantity > 0 and product.quantity < product.min_quantity:
            return "LOW"  # Mindestbestand gesetzt UND aktueller Bestand darunter

        return "OK"  # alles andere ist ausreichend

    def generate(self) -> InventoryReportResult:
        """
        Daten berechnen und als strukturiertes Objekt zurückgeben.

        Ablauf:
          1. Alle Produkte über den Port laden
          2. Alphabetisch nach ID sortieren (deterministisch!)
          3. Pro Produkt: Status + Wert berechnen, Zeile erstellen
          4. Gesamtkennzahlen aufaddieren
          5. Fertiges, unveränderliches Ergebnisobjekt zurückgeben
        """
        # 1. Alle Produkte laden – egal ob InMemory oder JSON dahinter
        products = self._repository.load_all_products()

        # 2. Alphabetisch sortieren → deterministisch (gleiche Daten = gleiche Reihenfolge)
        #    lambda p: p.id = anonyme Funktion: "nimm p.id als Sortierschlüssel"
        ordered = sorted(products.values(), key=lambda p: p.id)

        # Vorbereitung: leere Liste + Zähler
        rows: List[InventoryReportRow] = []
        total_value = 0.0
        low_count = 0
        out_count = 0
        ok_count = 0

        # 3. Jedes Produkt verarbeiten
        for p in ordered:
            status = self._status_for(p)  # "OK", "LOW" oder "OUT"

            # Zähler je nach Status erhöhen
            if status == "LOW":
                low_count += 1
            elif status == "OUT":
                out_count += 1
            else:
                ok_count += 1

            row_total = p.get_total_value()  # price * quantity
            total_value += row_total         # zum Gesamtwert addieren

            # Unveränderliche Report-Zeile erstellen und anhängen
            rows.append(InventoryReportRow(
                product_id=p.id,
                name=p.name,
                category=p.category,
                quantity=p.quantity,
                min_quantity=p.min_quantity,
                price=p.price,
                total_value=row_total,
                status=status,
            ))

        # 4. Fertiges Ergebnisobjekt zurückgeben (frozen = unveränderlich)
        return InventoryReportResult(
            rows=rows,
            product_count=len(rows),
            low_stock_count=low_count,
            out_of_stock_count=out_count,
            ok_count=ok_count,
            total_inventory_value=total_value,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def render_text(self, result: InventoryReportResult) -> str:
        """
        Report als formatierter Text (Konsole).
        generate() rechnet, render_text() druckt – Trennung von Logik und Darstellung.
        """
        sep = "=" * 60
        thin = "-" * 60
        symbols = {"OK": "v", "LOW": "!", "OUT": "x"}

        lines = [sep, "  LAGERSTANDSREPORT", f"  Erstellt: {result.generated_at}", sep, ""]

        if not result.rows:
            lines.append("  (Kein Produkt im Lager)")
        else:
            for row in result.rows:
                sym = symbols.get(row.status, "?")
                lines.append(f"  [{sym}] {row.product_id}  -  {row.name}")
                if row.category:
                    lines.append(f"       Kategorie: {row.category}")
                lines.append(f"       Bestand:   {row.quantity} Stk  (Mindest: {row.min_quantity} Stk)")
                lines.append(f"       Preis:     {row.price:.2f} EUR  | Gesamtwert: {row.total_value:.2f} EUR")
                lines.append(f"       Status:    {row.status}")
                lines.append("")

        lines += [
            thin,
            f"  Produkte gesamt:     {result.product_count}",
            f"  OK  (ausreichend):   {result.ok_count}",
            f"  LOW (Nachbestellen): {result.low_stock_count}",
            f"  OUT (Vergriffen):    {result.out_of_stock_count}",
            thin,
            f"  Gesamtlagerwert:     {result.total_inventory_value:.2f} EUR",
            sep,
        ]

        return "\n".join(lines)

    def render_html(self, result: InventoryReportResult) -> str:
        """
        Report als vollständiges HTML-Dokument.

        HTML-Ausgabe ermöglicht:
          - Darstellung im Browser
          - Speichern als .html-Datei (save_html)
          - PDF: Browser öffnen → Drucken → Als PDF speichern
        """
        # Hilfsfunktion: Farbe je nach Status (inline für HTML)
        def status_color(status: str) -> str:
            if status == "OUT":
                return "#e74c3c"   # Rot
            if status == "LOW":
                return "#f39c12"   # Orange
            return "#27ae60"       # Grün

        # HTML-Tabellenzeilen für alle Produkte aufbauen
        rows_html = ""
        for row in result.rows:
            color = status_color(row.status)
            rows_html += f"""
            <tr>
                <td>{row.product_id}</td>
                <td>{row.name}</td>
                <td>{row.category}</td>
                <td>{row.quantity}</td>
                <td>{row.min_quantity}</td>
                <td>{row.price:.2f} &euro;</td>
                <td>{row.total_value:.2f} &euro;</td>
                <td style="color:{color}; font-weight:bold;">{row.status}</td>
            </tr>"""

        # Vollständiges HTML-Dokument zusammenbauen
        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Lagerstandsreport</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 8px; }}
        .meta {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
        th {{ background: #2c3e50; color: white; padding: 10px 12px; text-align: left; }}
        td {{ padding: 9px 12px; border-bottom: 1px solid #ddd; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #f0f0f0; }}
        .summary {{ background: #ecf0f1; border-radius: 6px; padding: 16px 20px; display: inline-block; min-width: 300px; }}
        .summary h2 {{ margin: 0 0 10px; font-size: 16px; color: #2c3e50; }}
        .summary p {{ margin: 4px 0; font-size: 14px; }}
        .total {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 10px; }}
    </style>
</head>
<body>
    <h1>Lagerstandsreport</h1>
    <p class="meta">Erstellt: {result.generated_at}</p>

    <!-- Tabelle mit einem Produkt pro Zeile -->
    <table>
        <thead>
            <tr>
                <th>ID</th><th>Name</th><th>Kategorie</th>
                <th>Bestand</th><th>Mindest</th>
                <th>Preis</th><th>Gesamtwert</th><th>Status</th>
            </tr>
        </thead>
        <tbody>{rows_html}
        </tbody>
    </table>

    <!-- Zusammenfassung: alle Kennzahlen auf einen Blick -->
    <div class="summary">
        <h2>Zusammenfassung</h2>
        <p>Produkte gesamt: <b>{result.product_count}</b></p>
        <p style="color:#27ae60;">OK (ausreichend): <b>{result.ok_count}</b></p>
        <p style="color:#f39c12;">LOW (Nachbestellen): <b>{result.low_stock_count}</b></p>
        <p style="color:#e74c3c;">OUT (Vergriffen): <b>{result.out_of_stock_count}</b></p>
        <p class="total">Gesamtlagerwert: {result.total_inventory_value:.2f} &euro;</p>
    </div>
</body>
</html>"""
        return html

    def save_html(self, result: InventoryReportResult, filepath: str = "report.html") -> None:
        """
        HTML-Report als Datei speichern.

        Verwendung:
            report = InventoryReport(repo)
            result = report.generate()
            report.save_html(result, "report.html")
            # → report.html im Browser öffnen → Drucken → Als PDF speichern

        Args:
            result:   Ergebnis von generate()
            filepath: Zieldatei, Standard: "report.html"
        """
        html_content = self.render_html(result)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML-Report gespeichert: {filepath}")