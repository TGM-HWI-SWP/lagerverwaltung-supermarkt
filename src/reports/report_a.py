"""Report A (Rolle 2) - Lagerstandsreport / Inventory Report.

Der Report ist:
- eine eigene Komponente (kein UI/Controller-Print)
- deterministisch (gleiche Daten -> gleicher Output)
- testbar (Tests prüfen berechnete Werte, nicht Layout)
- hat eine eigene render()-Methode für Text-Ausgabe
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from ..domain.product import Product
from ..ports import RepositoryPort


@dataclass(frozen=True)
class InventoryReportRow:
    """Eine Zeile im Lagerstandsreport."""

    product_id: str
    name: str
    category: str
    quantity: int
    min_quantity: int
    price: float
    total_value: float
    status: str  # "OK" | "LOW" | "OUT"


@dataclass(frozen=True)
class InventoryReportResult:
    """Ergebnisobjekt für Report A."""

    rows: List[InventoryReportRow]
    product_count: int
    low_stock_count: int
    out_of_stock_count: int
    ok_count: int
    total_inventory_value: float
    generated_at: str  # Zeitstempel der Erzeugung


class InventoryReport:
    """Report A: Lagerstandsreport.

    Trennung von Logik (generate) und Darstellung (render):
    - generate() berechnet die Daten -> InventoryReportResult
    - render()   formatiert das Ergebnis als lesbaren Text
    """

    def __init__(self, repository: RepositoryPort):
        self._repository = repository

    @staticmethod
    def _status_for(product: Product) -> str:
        """Status eines Produkts bestimmen."""
        if product.quantity <= 0:
            return "OUT"
        if product.min_quantity > 0 and product.quantity < product.min_quantity:
            return "LOW"
        return "OK"

    def generate(self) -> InventoryReportResult:
        """Report-Daten berechnen und als strukturiertes Objekt zurückgeben.

        Returns:
            InventoryReportResult mit allen berechneten Kennzahlen.
        """
        products = self._repository.load_all_products()

        # Deterministische Reihenfolge: alphabetisch nach product_id
        ordered = sorted(products.values(), key=lambda p: p.id)

        rows: List[InventoryReportRow] = []
        total_value = 0.0
        low_count = 0
        out_count = 0
        ok_count = 0

        for p in ordered:
            status = self._status_for(p)
            if status == "LOW":
                low_count += 1
            elif status == "OUT":
                out_count += 1
            else:
                ok_count += 1

            row_total = p.get_total_value()
            total_value += row_total
            rows.append(
                InventoryReportRow(
                    product_id=p.id,
                    name=p.name,
                    category=p.category,
                    quantity=p.quantity,
                    min_quantity=p.min_quantity,
                    price=p.price,
                    total_value=row_total,
                    status=status,
                )
            )

        return InventoryReportResult(
            rows=rows,
            product_count=len(rows),
            low_stock_count=low_count,
            out_of_stock_count=out_count,
            ok_count=ok_count,
            total_inventory_value=total_value,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def render(self, result: InventoryReportResult) -> str:
        """Report-Ergebnis als formatierten Text ausgeben.

        Trennung von Logik (generate) und Darstellung (render) erlaubt
        verschiedene Ausgabeformate ohne die Berechnungslogik zu ändern.

        Args:
            result: Ergebnis von generate()

        Returns:
            Formatierter Report als String.
        """
        sep = "=" * 60
        thin = "-" * 60

        # Status-Symbol für bessere Lesbarkeit
        symbols = {"OK": "✓", "LOW": "!", "OUT": "✗"}

        lines = [
            sep,
            "  LAGERSTANDSREPORT",
            f"  Erstellt: {result.generated_at}",
            sep,
            "",
        ]

        if not result.rows:
            lines.append("  (Kein Produkt im Lager)")
        else:
            for row in result.rows:
                sym = symbols.get(row.status, "?")
                lines.append(f"  [{sym}] {row.product_id}  –  {row.name}")
                if row.category:
                    lines.append(f"       Kategorie: {row.category}")
                lines.append(f"       Bestand:   {row.quantity} Stk  "
                             f"(Mindest: {row.min_quantity} Stk)")
                lines.append(f"       Preis:     {row.price:.2f} €  "
                             f"| Gesamtwert: {row.total_value:.2f} €")
                lines.append(f"       Status:    {row.status}")
                lines.append("")

        lines += [
            thin,
            f"  Produkte gesamt:     {result.product_count}",
            f"  OK  (ausreichend):   {result.ok_count}",
            f"  LOW (Nachbestellen): {result.low_stock_count}",
            f"  OUT (Vergriffen):    {result.out_of_stock_count}",
            thin,
            f"  Gesamtlagerwert:     {result.total_inventory_value:.2f} €",
            sep,
        ]

        return "\n".join(lines)