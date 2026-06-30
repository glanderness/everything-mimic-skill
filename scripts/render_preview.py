#!/usr/bin/env python3
"""Wrap a WeChat body HTML file in a simple preview shell."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("body_html", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="WeChat Layout Preview")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    body = args.body_html.read_text(encoding="utf-8")
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{args.title}</title>
  <style>
    body {{
      margin: 0;
      background: #f4f4f4;
      color: #222;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
    }}
    .preview-shell {{
      max-width: 680px;
      margin: 0 auto;
      min-height: 100vh;
      background: #fff;
      box-sizing: border-box;
    }}
    img {{
      max-width: 100%;
    }}
  </style>
</head>
<body>
  <main class="preview-shell">
{body}
  </main>
</body>
</html>
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

