import re
from typing import Dict, Iterable, List, Sequence

from .models import TransactionRecord
from .normalize import normalize_amount, normalize_date


DATE_RE = re.compile(r"(?<!\d)(?:\d{8}|\d{4}[-/]\d{1,2}[-/]\d{1,2})(?!\d)")
TXID_RE = re.compile(r"(?<!\d)\d{8,20}(?!\d)")
AMOUNT_RE = re.compile(
    r"(?<!\d)(?:[（(]\s*)?-?\d{1,3}(?:[,，]\d{3})+(?:\.\d{1,2})?(?:\s*[)）])?"
    r"|(?<!\d)-?\d+\.\d{1,2}(?!\d)"
)


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def _has_term(text: str, term: str) -> bool:
    return term in text or _compact(term) in _compact(text)


def _first_date(text: str):
    for match in DATE_RE.finditer(text):
        parsed = normalize_date(match.group(0))
        if parsed:
            return parsed
    return None


def _txid(text: str) -> str:
    date_text = {m.group(0) for m in DATE_RE.finditer(text)}
    for match in TXID_RE.finditer(text):
        if match.group(0) not in date_text:
            return match.group(0)
    return ""


def _amounts(text: str):
    found = []
    for match in AMOUNT_RE.finditer(text):
        token = match.group(0).strip()
        parsed = normalize_amount(token)
        if parsed is not None:
            found.append((token, parsed))
    return found


def extract_matches(pages: Dict[int, Sequence[str]], target_terms: Iterable[str]) -> List[TransactionRecord]:
    """Extract one record per OCR line containing a target term.

    This deliberately keeps ambiguous rows rather than silently discarding them.
    The first numeric amount is treated as transaction amount and the second as
    balance, matching the common bank-statement row layout. Bank profiles can
    replace this heuristic later.
    """
    terms = [term.strip() for term in target_terms if term and term.strip()]
    records: List[TransactionRecord] = []
    for page, lines in pages.items():
        for line in lines:
            raw_text = str(line).strip()
            matched = next((term for term in terms if _has_term(raw_text, term)), None)
            if not matched:
                continue
            parsed_date = _first_date(raw_text)
            txid = _txid(raw_text)
            amounts = _amounts(raw_text)
            amount = amounts[0][1] if amounts else None
            balance = amounts[1][1] if len(amounts) > 1 else None
            if parsed_date and amount is not None:
                confidence, status = "high", "已提取"
            elif amount is not None or parsed_date is not None:
                confidence, status = "medium", "待人工核验"
            else:
                confidence, status = "low", "待人工核验"
            note_parts = []
            if parsed_date is None:
                note_parts.append("日期未识别")
            if amount is None:
                note_parts.append("金额未识别")
            records.append(
                TransactionRecord(
                    page=page,
                    date=parsed_date,
                    txid=txid,
                    description=matched,
                    amount=amount,
                    balance=balance,
                    raw_amount=amounts[0][0] if amounts else "",
                    raw_text=raw_text,
                    confidence=confidence,
                    review_status=status,
                    note="；".join(note_parts),
                )
            )
    return records
