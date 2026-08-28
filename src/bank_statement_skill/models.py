from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class TransactionRecord:
    page: int
    date: Optional[date] = None
    txid: str = ""
    description: str = ""
    amount: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    raw_amount: str = ""
    raw_text: str = ""
    confidence: str = "low"
    review_status: str = "待人工核验"
    note: str = ""
