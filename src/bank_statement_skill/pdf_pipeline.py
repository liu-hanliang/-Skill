import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class PdfInspection:
    path: Path
    page_count: int
    has_text_layer: bool


def _fitz():
    try:
        import fitz  # type: ignore

        return fitz
    except ImportError:
        return None


def inspect_pdf(path: Path) -> PdfInspection:
    path = Path(path).expanduser().resolve()
    fitz = _fitz()
    if fitz:
        doc = fitz.open(path)
        try:
            sample = "".join(doc[i].get_text() for i in range(min(3, len(doc))))
            return PdfInspection(path, len(doc), bool(sample.strip()))
        finally:
            doc.close()
    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        raise RuntimeError("需要安装 PyMuPDF，或提供 pdfinfo 命令来检查 PDF。")
    result = subprocess.run([pdfinfo, str(path)], check=True, capture_output=True, text=True)
    page_count = 0
    for line in result.stdout.splitlines():
        if line.lower().startswith("pages:"):
            page_count = int(line.split(":", 1)[1].strip())
            break
    if not page_count:
        raise RuntimeError("无法读取 PDF 页数。")
    return PdfInspection(path, page_count, False)


def parse_page_range(value: Optional[str], page_count: int) -> List[int]:
    if not value:
        return list(range(1, page_count + 1))
    pages = set()
    for part in value.split(","):
        part = part.strip()
        if "-" in part:
            start, end = [int(x.strip()) for x in part.split("-", 1)]
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    invalid = sorted(p for p in pages if p < 1 or p > page_count)
    if invalid:
        raise ValueError(f"页码超出范围：{invalid}；PDF 共 {page_count} 页。")
    return sorted(pages)


def render_pages(path: Path, pages: Iterable[int], output_dir: Path, dpi: int = 220) -> Dict[int, Path]:
    path = Path(path).expanduser().resolve()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    page_list = list(pages)
    fitz = _fitz()
    rendered: Dict[int, Path] = {}
    if fitz:
        doc = fitz.open(path)
        try:
            for page_number in page_list:
                page = doc[page_number - 1]
                pix = page.get_pixmap(dpi=dpi, alpha=False)
                target = output_dir / f"page-{page_number:04d}.png"
                pix.save(str(target))
                rendered[page_number] = target
        finally:
            doc.close()
        return rendered
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise RuntimeError("需要安装 PyMuPDF，或提供 pdftoppm 命令来渲染扫描 PDF。")
    for page_number in page_list:
        prefix = output_dir / f"page-{page_number:04d}"
        subprocess.run(
            [pdftoppm, "-f", str(page_number), "-l", str(page_number), "-r", str(dpi), "-png", str(path), str(prefix)],
            check=True,
            capture_output=True,
            text=True,
        )
        target = output_dir / f"page-{page_number:04d}-1.png"
        if not target.exists():
            candidates = sorted(output_dir.glob(f"page-{page_number:04d}*.png"))
            if not candidates:
                raise RuntimeError(f"第 {page_number} 页渲染失败。")
            target = candidates[0]
        rendered[page_number] = target
    return rendered


def ocr_image(image_path: Path, language: str = "chi_sim+eng", psm: int = 6) -> List[str]:
    command = os.environ.get("TESSERACT_CMD") or shutil.which("tesseract")
    if not command:
        raise RuntimeError("未找到 Tesseract。请安装 Tesseract 和 chi_sim 中文语言包。")
    result = subprocess.run(
        [command, str(image_path), "stdout", "-l", language, "--psm", str(psm)],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
