# tests/unit/test_report_b.py

import pytest
from src.reports.report_b import ReportB


class DummyRepository:
    def __init__(self, movements):
        self._movements = movements

    def get_all_movements(self):
        return self._movements


# ----------------------------
# NORMALFALL TEST
# ----------------------------

def test_sales_per_product_normal():
    movements = [
        {"product": "Milch", "quantity": 2, "type": "sale"},
        {"product": "Milch", "quantity": 3, "type": "sale"},
        {"product": "Brot", "quantity": 1, "type": "sale"},
    ]

    repo = DummyRepository(movements)
    report = ReportB(repo)

    result = report.sales_per_product()

    assert result["Milch"] == 5
    assert result["Brot"] == 1

# ----------------------------
# LEERES REPOSITORY
# ----------------------------

def test_empty_repository():
    repo = DummyRepository([])
    report = ReportB(repo)

    assert report.sales_per_product() == {}
    assert report.best_selling_product() is None


# ----------------------------
# NEGATIVE MENGE (Fehlerfall)
# ----------------------------

def test_negative_quantity():
    movements = [
        {"product": "Milch", "quantity": -3, "type": "sale"},
    ]

    repo = DummyRepository(movements)
    report = ReportB(repo)

    with pytest.raises(ValueError):
        report.sales_per_product()