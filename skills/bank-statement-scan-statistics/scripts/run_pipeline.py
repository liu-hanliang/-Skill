#!/usr/bin/env python3
import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from bank_statement_skill.extract import extract_matches
from bank_statement_skill.export_xlsx import build_workbook
from bank_statement_skill.pdf_pipeline import inspect_pdf, ocr_image, parse_page_range, render_pages


def parse_args():
    parser = argparse.ArgumentParser(description="Local-first bank statement OCR and XLSX statistics")
    parser.add_argument("--input", required=True, help="PDF or image path")
    parser.add_argument("--keyword", action="append", required=True, help="Keyword to match; repeat for multiple terms")
    parser.add_argument("--pages", default=None, help="Page range such as 1-48 or 1,3,5-7")
    parser.add_argument("--output", required=True, help="New XLSX path")
    parser.add_argument("--dpi", type=int, default=220)
    parser.add_argument("--language", default="chi_sim+eng")
    parser.add_argument("--psm", type=int, default=6)
    return parser.parse_args()


def main():
    args = parse_args()
    source = Path(args.input).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"找不到输入文件：{source}")
    output = Path(args.output).expanduser().resolve()
    with tempfile.TemporaryDirectory(prefix="bank-statement-") as temp_dir:
        temp_dir = Path(temp_dir)
        if source.suffix.lower() == ".pdf":
            info = inspect_pdf(source)
            pages = parse_page_range(args.pages, info.page_count)
            images = render_pages(source, pages, temp_dir / "pages", dpi=args.dpi)
            page_lines = {page: ocr_image(image, args.language, args.psm) for page, image in images.items()}
            page_range = args.pages or f"1-{info.page_count}"
        else:
            page_lines = {1: ocr_image(source, args.language, args.psm)}
            page_range = "1"
        records = extract_matches(page_lines, args.keyword)
        build_workbook(
            records,
            {
                "source_file": source.name,
                "page_range": page_range,
                "keywords": "、".join(args.keyword),
                "ocr_method": "本地 Tesseract OCR",
            },
            output,
        )
    print(f"已生成：{output}")
    print(f"匹配笔数（OCR 初筛）：{len(records)}")
    print("提示：请在 XLSX 的‘匹配明细’和‘核验说明’中复核低置信度记录。")


if __name__ == "__main__":
    main()
