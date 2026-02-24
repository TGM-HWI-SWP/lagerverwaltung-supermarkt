"""Report A (Rolle 2) - Lagerstandsreport / Inventory Report.

Der Report ist:
- eine eigene Komponente (kein UI/Controller-Print)
- deterministisch (gleiche Daten -> gleicher Output)
- testbar (Tests prüfen berechnete Werte, nicht Layout)
"""

from __future__ import annotations

from dataclasses import dataclass
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
    total_inventory_value: float


class InventoryReport:
    """Report A: Lagerstandsreport."""

    def __init__(self, repository: RepositoryPort):
        self._repository = repository

    @staticmethod
    def _status_for(product: Product) -> str:
        if product.quantity <= 0:
            return "OUT"
        if product.min_quantity > 0 and product.quantity < product.min_quantity:
            return "LOW"
        return "OK"

    def generate(self) -> InventoryReportResult:
        """Report A generieren."""
        products = self._repository.load_all_products()

        # deterministische Reihenfolge
        ordered = sorted(products.values(), key=lambda p: p.id)

        rows: List[InventoryReportRow] = []
        total_value = 0.0
        low_count = 0
        out_count = 0

        for p in ordered:
            status = self._status_for(p)
            if status == "LOW":
                low_count += 1
            elif status == "OUT":
                out_count += 1

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
            total_inventory_value=total_value,
        )