---
name: bank-statement-scan-statistics
description: Use when a user needs to inspect a scanned bank-statement PDF or image, find transaction keywords, count or sum matching payments, or produce traceable monthly statistics in XLSX.
---

# Bank Statement Scan Statistics

## Purpose

Use this skill for evidence整理、流水筛选、涉案金额初步统计和月度汇总。它把 OCR 当作“可复核的初筛”，不是法律结论，也不承诺未知银行版式一次识别无误。

## Required workflow

1. Confirm the input file, page range, target keyword(s), amount field and desired output path. If the user did not specify a page range, inspect the PDF page count and state the assumed range.
2. Keep the original file read-only. Prefer 本地 OCR（local OCR） with `chi_sim+eng`; do not upload bank records to online OCR unless取得用户明确授权并先提示隐私风险。
3. Run the bundled pipeline:

   ```bash
   python skills/bank-statement-scan-statistics/scripts/run_pipeline.py \
     --input "/path/to/statement.pdf" \
     --pages 1-48 \
     --keyword "应付商户延迟清算款" \
     --output "/path/to/output/银行流水统计.xlsx"
   ```

4. Deliver an XLSX with `汇总`, `按月统计`, `匹配明细`, and `核验说明`. Every match must保留 PDF 页码、日期（如可识别）、流水号（如可识别）、原始 OCR 行、原始金额、规范化金额和核验状态。
5. Inspect the workbook after creation. Reconcile detail count/amount with monthly totals and total amount. Never silently discard a keyword hit whose date or amount is unclear; mark it `待人工核验` and include it in the人工复核清单。
6. In the final response, state the source pages, keyword, match count, total amount, output path and any uncertain rows. Remind the user to compare important rows with the original PDF before litigation, arbitration or audit.

## Bank profiles

Treat bank names as hints, not proof of layout. Use the generic parser first; add a bank profile only for stable, documented column differences. Do not create one Skill per bank. Unknown layouts and multi-line rows must be surfaced for review.

## Privacy and safety

- Never commit or publish real bank PDFs, images, OCR text, names, account numbers, transaction IDs or unredacted XLSX files.
- 不覆盖源 PDF（do not overwrite the source PDF）。
- Do not claim that OCR output is a certified bank record or legal conclusion.
- If a stamp, blur, clipped row, ambiguous decimal point or missing amount affects a match, preserve the row and mark it for human review.
