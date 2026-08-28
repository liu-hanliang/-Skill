import unittest
from datetime import date
from decimal import Decimal

from bank_statement_skill.normalize import normalize_amount, normalize_date


class NormalizeTests(unittest.TestCase):
    def test_normalize_amount_handles_commas_spaces_and_parentheses(self):
        self.assertEqual(normalize_amount(" 1,421.15 "), Decimal("1421.15"))
        self.assertEqual(normalize_amount("(706.60)"), Decimal("-706.60"))

    def test_normalize_date_handles_compact_and_delimited_forms(self):
        self.assertEqual(normalize_date("20240522"), date(2024, 5, 22))
        self.assertEqual(normalize_date("2024-05-22"), date(2024, 5, 22))
