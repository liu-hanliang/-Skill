import unittest
from pathlib import Path


SKILL = Path(__file__).parents[1] / "skills" / "bank-statement-scan-statistics" / "SKILL.md"


class SkillContractTests(unittest.TestCase):
    def test_skill_contract_is_local_first_and_traceable(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: bank-statement-scan-statistics\n"))
        self.assertIn("Use when", text.split("---", 2)[1])
        self.assertIn("本地 OCR", text)
        self.assertIn("明确授权", text)
        self.assertIn("页码", text)
        self.assertIn("人工复核", text)
        self.assertIn("不覆盖", text)
