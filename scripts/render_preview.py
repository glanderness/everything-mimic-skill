#!/usr/bin/env python3
"""Wrap WeChat article body HTML in the base preview template."""

from __future__ import annotations

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("body_html", type=Path)
    parser.add_argument("--template", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=Path("preview.html"))
    parser.add_argument("--title", default="WeChat Article Preview")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    template_path = args.template or skill_dir / "assets" / "templates" / "base-preview.html"

    body = args.body_html.read_text(encoding="utf-8")
    template = template_path.read_text(encoding="utf-8")
    html = template.replace("{{TITLE}}", args.title).replace("{{BODY}}", body)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(args.out.resolve())


if __name__ == "__main__":
    main()

