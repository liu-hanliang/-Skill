# Bank Statement Scan Statistics Skill

面向律师、法务、会计和调查人员的银行流水扫描件整理 Skill：把扫描版银行流水 PDF/图片转换成可追溯的关键词匹配明细、总计和按月统计 XLSX。

仓库地址：<https://github.com/liu-hanliang/-Skill>

## 为什么需要这个 Skill

单次任务中，AI 也许能“想办法”完成 OCR；但银行流水任务容易反复遇到相同问题：页码范围不清、扫描件没有文字层、中文 OCR 把金额识别错、不同银行版式变化、统计总额无法追溯、低置信度记录被忽略。

这个 Skill 将经验固化成可复用的执行约束：本地优先、先识别再统计、明细驱动合计、保留页码和原始 OCR 行、异常记录进入人工复核，而不是静默丢弃。这样后续同类任务通常能用更少的上下文、更短的路径和更稳定的输出完成。

## 给 AI 直接发 GitHub 链接

当你使用 Codex、Work Buddy/CodeBuddy 或其他支持 Agent Skills 的 AI 工具时，可以直接把本仓库链接发给 AI，并说明：

> 请读取并安装这个 Skill，然后用它统计我上传的银行流水 PDF。目标关键词是“应付商户延迟清算款”，按月统计并生成 XLSX。

如果工具不能自动从链接安装，可以让 AI 将仓库中的 `skills/bank-statement-scan-statistics/` 复制到其 Skills 目录，再按 `SKILL.md` 执行。请以具体产品当前版本的安装说明为准。

## 直接运行脚本

需要 Python 3.9+、Tesseract 及 `chi_sim` 中文语言包。首次安装：

```bash
python -m pip install -e ".[pdf]"
```

运行：

```bash
python skills/bank-statement-scan-statistics/scripts/run_pipeline.py \
  --input "/path/to/statement.pdf" \
  --pages 1-48 \
  --keyword "应付商户延迟清算款" \
  --output "/path/to/output/银行流水统计.xlsx"
```

多关键词可重复使用 `--keyword`。输出工作簿包含：

- `汇总`：匹配笔数和总金额
- `按月统计`：按交易日期的笔数和金额
- `匹配明细`：页码、日期、流水号、金额、余额、原始 OCR 行和核验状态
- `核验说明`：处理范围、隐私提示和人工复核要求

## 隐私与准确性

默认使用本地 OCR。银行流水可能包含姓名、账号和交易对手信息；不要把真实资料上传到线上 OCR，也不要提交到公开 GitHub，除非已完成脱敏并获得必要授权。OCR 结果是证据整理初稿，不是银行出具的认证记录；重要金额必须回看原始 PDF。

## 当前范围

当前版本提供通用抽取器和可扩展的银行版式适配入口，重点覆盖“扫描 PDF → 关键词匹配 → 明细 → 总计/月度统计 → 复核说明”。银行版式差异较大时，应新增配置和合成测试样例，而不是在 Skill 中硬编码一次性修补。

## 开发

```bash
python -m unittest discover -s tests -v
```

测试只使用合成文本，不包含任何真实银行资料。
