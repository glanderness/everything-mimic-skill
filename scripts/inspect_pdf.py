#!/usr/bin/env python3
"""Render PDF pages and write a rough inspection report for style extraction."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def try_import_fitz():
    try:
        import fitz  # PyMuPDF
    except Exception:
        return None
    return fitz


def try_import_pdfplumber():
    try:
        import pdfplumber
    except Exception:
        return None
    return pdfplumber


def summarize_blocks(page):
    blocks = page.get_text("blocks")
    text_blocks = []
    heights = []
    widths = []
    for block in blocks:
        x0, y0, x1, y1, text, block_no, block_type = block[:7]
        if block_type != 0 or not text.strip():
            continue
        width = max(0, x1 - x0)
        height = max(0, y1 - y0)
        widths.append(width)
        heights.append(height)
        text_blocks.append(
            {
                "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                "chars": len(text.strip()),
                "sample": " ".join(text.strip().split())[:120],
            }
        )
    return {
        "text_block_count": len(text_blocks),
        "median_block_width": round(statistics.median(widths), 2) if widths else None,
        "median_block_height": round(statistics.median(heights), 2) if heights else None,
        "blocks": text_blocks[:80],
    }


def inspect_with_fitz(fitz, pdf_path, out_dir, pages_dir, dpi, max_pages):
    doc = fitz.open(pdf_path)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    page_reports = []

    for index, page in enumerate(doc):
        if index >= max_pages:
            break
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        png_path = pages_dir / f"page-{index + 1:03d}.png"
        pix.save(png_path)
        page_report = {
            "page": index + 1,
            "width_pt": round(page.rect.width, 2),
            "height_pt": round(page.rect.height, 2),
            "rendered_png": str(png_path),
        }
        page_report.update(summarize_blocks(page))
        page_reports.append(page_report)

    return {
        "pdf": str(pdf_path),
        "page_count": doc.page_count,
        "inspected_pages": len(page_reports),
        "dpi": dpi,
        "renderer": "pymupdf",
        "notes": [
            "Measurements are PDF estimates, not source CSS.",
            "Use rendered PNGs for visual style judgment.",
        ],
        "pages": page_reports,
    }


def inspect_with_poppler(pdfplumber, pdf_path, out_dir, pages_dir, dpi, max_pages):
    prefix = pages_dir / "page"
    subprocess.run(
        [
            "pdftoppm",
            "-png",
            "-r",
            str(dpi),
            "-f",
            "1",
            "-l",
            str(max_pages),
            str(pdf_path),
            str(prefix),
        ],
        check=True,
    )

    page_reports = []
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        for index, page in enumerate(pdf.pages[:max_pages]):
            words = page.extract_words() or []
            widths = []
            heights = []
            blocks = []
            for word in words[:120]:
                x0 = float(word.get("x0", 0))
                x1 = float(word.get("x1", 0))
                top = float(word.get("top", 0))
                bottom = float(word.get("bottom", 0))
                widths.append(max(0, x1 - x0))
                heights.append(max(0, bottom - top))
                blocks.append(
                    {
                        "bbox": [round(x0, 2), round(top, 2), round(x1, 2), round(bottom, 2)],
                        "chars": len(word.get("text", "")),
                        "sample": word.get("text", "")[:80],
                    }
                )
            page_reports.append(
                {
                    "page": index + 1,
                    "width_pt": round(page.width, 2),
                    "height_pt": round(page.height, 2),
                    "rendered_png": str(pages_dir / f"page-{index + 1:02d}.png"),
                    "text_block_count": len(words),
                    "median_word_width": round(statistics.median(widths), 2) if widths else None,
                    "median_word_height": round(statistics.median(heights), 2) if heights else None,
                    "blocks": blocks,
                }
            )

    return {
        "pdf": str(pdf_path),
        "page_count": page_count,
        "inspected_pages": len(page_reports),
        "dpi": dpi,
        "renderer": "poppler+pdfplumber",
        "notes": [
            "Measurements are PDF estimates, not source CSS.",
            "Poppler file names may be page-01.png style rather than page-001.png.",
            "Use rendered PNGs for visual style judgment.",
        ],
        "pages": page_reports,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--max-pages", type=int, default=12)
    args = parser.parse_args()

    fitz = try_import_fitz()
    pdfplumber = None if fitz else try_import_pdfplumber()
    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    out_dir = args.out or pdf_path.with_suffix("")
    out_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = out_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    if fitz:
        report = inspect_with_fitz(fitz, pdf_path, out_dir, pages_dir, args.dpi, args.max_pages)
    elif pdfplumber:
        report = inspect_with_poppler(pdfplumber, pdf_path, out_dir, pages_dir, args.dpi, args.max_pages)
    else:
        raise SystemExit(
            "Missing PDF inspection dependencies. Install PyMuPDF or pdfplumber with Poppler pdftoppm."
        )
    report_path = out_dir / "inspection.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report_path)


if __name__ == "__main__":
    main()
