import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional


def normalize_amount(raw: str) -> Optional[Decimal]:
    """Normalize one OCR amount token without guessing malformed digits."""
    if raw is None:
        return None
    value = str(raw).strip().translate(str.maketrans({"，": ",", "．": ".", "（": "(", "）": ")"}))
    value = value.replace("￥", "").replace("¥", "").replace(" ", "")
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1]
    value = value.replace(",", "")
    if not re.fullmatch(r"-?\d+(?:\.\d{1,2})?", value):
        return None
    try:
        amount = Decimal(value).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None
    return -abs(amount) if negative else amount


def normalize_date(raw: str) -> Optional[date]:
    """Parse common Chinese bank-statement date formats."""
    if raw is None:
        return None
    text = str(raw).strip()
    patterns = (
        (r"^(\d{4})(\d{2})(\d{2})$", "%Y%m%d"),
        (r"^(\d{4})[-/]([01]?\d)[-/]([0-3]?\d)$", None),
    )
    for pattern, fmt in patterns:
        match = re.fullmatch(pattern, text)
        if not match:
            continue
        try:
            if fmt:
                return date.fromisoformat(f"{text[:4]}-{text[4:6]}-{text[6:8]}")
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    match = re.fullmatch(r"(\d{4})年([01]?\d)月([0-3]?\d)日?", text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    return None
