# src/reports/report_b.py

class ReportB:
    """
    Verkaufsstatistik-Report
    Berechnet:
    - Gesamtverkäufe pro Produkt
    - Meistverkauftes Produkt
    """

    def __init__(self, repository):
        self.repository = repository

    def sales_per_product(self):
        """
        Erwartet vom Repository:
        get_all_movements() -> Liste von Dicts:
        {
            "product": "Milch",
            "quantity": 2,
            "type": "sale"
        }
        """

        movements = self.repository.get_all_movements()

        result = {}

        for movement in movements:
            if movement["type"] == "sale":
                product = movement["product"]
                quantity = movement["quantity"]

                if quantity < 0:
                    raise ValueError("Negative Verkaufsmenge nicht erlaubt")

                if product not in result:
                    result[product] = 0

                result[product] += quantity

        return result

    def best_selling_product(self):
        sales = self.sales_per_product()

        if not sales:
            return None

        return max(sales, key=sales.get)