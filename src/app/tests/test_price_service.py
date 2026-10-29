import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.price_service import calculate_final_price, get_previous_month_range


class PriceServiceTest(unittest.TestCase):
    def test_previous_month_in_middle_of_year(self):
        self.assertEqual(get_previous_month_range(date(2026, 5, 15)), (date(2026, 4, 1), date(2026, 5, 1)))

    def test_previous_month_in_january(self):
        self.assertEqual(get_previous_month_range(date(2026, 1, 10)), (date(2025, 12, 1), date(2026, 1, 1)))

    def test_discount_when_no_orders(self):
        self.assertEqual(calculate_final_price(Decimal("2190"), False), Decimal("1642.50"))

    def test_no_discount_when_has_orders(self):
        self.assertEqual(calculate_final_price(Decimal("2190"), True), Decimal("2190"))


if __name__ == "__main__":
    unittest.main()