from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BankProfile:
    name: str
    amount_rule: str = "first_numeric_after_description"
    balance_rule: str = "second_numeric_after_description"
    multiline_description: bool = True


DEFAULT_PROFILE = BankProfile("generic")
BANK_PROFILES = {
    "中国农业银行": BankProfile("中国农业银行"),
    "建设银行": BankProfile("建设银行"),
    "中国银行": BankProfile("中国银行"),
    "宁波银行": BankProfile("宁波银行"),
    "民生银行": BankProfile("民生银行"),
}


def get_profile(bank_name: Optional[str] = None) -> BankProfile:
    if not bank_name:
        return DEFAULT_PROFILE
    for name, profile in BANK_PROFILES.items():
        if name in bank_name or bank_name in name:
            return profile
    return DEFAULT_PROFILE
