import unittest
from decimal import Decimal

from bank_statement_skill.extract import extract_matches


class ExtractTests(unittest.TestCase):
    def test_extract_matches_keeps_page_and_raw_text_and_uses_first_amount(self):
        pages = {3: ["20240522 0163223376 应付商户延迟清算款 706.60 6,078.98"]}
        rows = extract_matches(pages, ["应付商户延迟清算款"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].page, 3)
        self.assertEqual(rows[0].amount, Decimal("706.60"))
        self.assertEqual(rows[0].balance, Decimal("6078.98"))
        self.assertEqual(rows[0].raw_text, pages[3][0])

    def test_extract_matches_marks_missing_amount_for_review_instead_of_dropping_row(self):
        pages = {4: ["20240523 应付商户延迟清算款 金额无法识别"]}
        rows = extract_matches(pages, ["应付商户延迟清算款"])
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0].amount)
        self.assertEqual(rows[0].review_status, "待人工核验")
