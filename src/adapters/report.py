"""Report Adapter – Konsolenausgabe über InventoryReport.

ConsoleReportAdapter implementiert ReportPort und delegiert intern
an InventoryReport (Report A). So ist die Logik nur einmal geschrieben.
"""

from ..ports import ReportPort, RepositoryPort
from ..reports.report_a import InventoryReport


class ConsoleReportAdapter(ReportPort):
    """Report-Adapter für Konsolenausgabe.

    Implementiert ReportPort und nutzt intern InventoryReport,
    sodass die Berechnungslogik nicht dupliziert wird.
    """

    def __init__(self, repository: RepositoryPort):
        self._repository = repository
        self._inventory_report = InventoryReport(repository)

    def generate_inventory_report(self) -> str:
        """Lagerbestandsbericht via InventoryReport erzeugen."""
        result = self._inventory_report.generate()
        return self._inventory_report.render(result)

    def generate_movement_report(self) -> str:
        """Bewegungsprotokoll als Text erzeugen."""
        movements = self._repository.load_movements()

        if not movements:
            return "Keine Lagerbewegungen vorhanden.\n"

        sep = "=" * 70
        thin = "-" * 70
        lines = [sep, "  BEWEGUNGSPROTOKOLL", sep, ""]

        for m in sorted(movements, key=lambda x: x.timestamp):
            sign = "+" if m.quantity_change > 0 else ""
            lines.append(
                f"  [{m.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]  "
                f"{m.movement_type}"
            )
            lines.append(f"  Produkt:  {m.product_name} (ID: {m.product_id})")
            lines.append(f"  Menge:    {sign}{m.quantity_change}")
            if m.reason:
                lines.append(f"  Grund:    {m.reason}")
            lines.append(f"  Von:      {m.performed_by}")
            lines.append("")

        lines += [thin, f"  Bewegungen gesamt: {len(movements)}", sep]
        return "\n".join(lines)