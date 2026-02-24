"""Unit Tests für Report A (InventoryReport)."""

from src.adapters.repository import InMemoryRepository
from src.reports import InventoryReport
from src.services import WarehouseService


class TestInventoryReport:
    """Tests für den Lagerstandsreport (Report A)."""

    def test_report_a_empty_repo(self):
        repo = InMemoryRepository()
        report = InventoryReport(repo)

        result = report.generate()
        assert result.product_count == 0
        assert result.total_inventory_value == 0
        assert result.low_stock_count == 0
        assert result.out_of_stock_count == 0
        assert result.rows == []

    def test_report_a_totals_and_status_counts(self):
        repo = InMemoryRepository()
        service = WarehouseService(repo)

        # OK
        service.create_product(
            "P001",
            "Milch",
            "1L",
            1.50,
            category="Molkerei",
            initial_quantity=10,
            min_quantity=5,
        )
        # LOW
        service.create_product(
            "P002",
            "Brot",
            "Vollkorn",
            2.00,
            category="Backwaren",
            initial_quantity=2,
            min_quantity=5,
        )
        # OUT
        service.create_product(
            "P003",
            "Eier",
            "10er",
            3.00,
            category="Frische",
            initial_quantity=0,
            min_quantity=4,
        )

        report = InventoryReport(repo)
        result = report.generate()

        assert result.product_count == 3
        assert result.low_stock_count == 1
        assert result.out_of_stock_count == 1
        assert result.total_inventory_value == (10 * 1.50) + (2 * 2.00) + (0 * 3.00)

        # deterministische Reihenfolge (nach product_id)
        assert [r.product_id for r in result.rows] == ["P001", "P002", "P003"]
        assert {r.product_id: r.status for r in result.rows} == {
            "P001": "OK",
            "P002": "LOW",
            "P003": "OUT",
        }