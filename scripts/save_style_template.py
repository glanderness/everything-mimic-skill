#!/usr/bin/env python3
"""Save an approved style run as a reusable WeChat style template."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REQUIRED = ["style-profile.json", "style-brief.md"]


def find_style_file(run_dir: Path, name: str) -> Path | None:
    candidates = [
        run_dir / name,
        run_dir / "style" / name,
        run_dir / "style" / f"source-{name}",
    ]
    return next((path for path in candidates if path.exists()), None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("template_dir", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    run_dir = args.run_dir.expanduser().resolve()
    template_dir = args.template_dir.expanduser().resolve()
    sources = {name: find_style_file(run_dir, name) for name in REQUIRED}
    missing = [name for name, source in sources.items() if source is None]
    if missing:
        raise SystemExit(f"Missing required template files in {run_dir}: {', '.join(missing)}")
    if template_dir.exists() and not args.overwrite:
        raise SystemExit(f"Template exists: {template_dir}. Use --overwrite to replace it.")
    if template_dir.exists():
        shutil.rmtree(template_dir)
    template_dir.mkdir(parents=True)

    for name, source in sources.items():
        shutil.copy2(source, template_dir / name)
    for optional in ["preview.html", "article.wechat.html", "layout-notes.md"]:
        source = run_dir / optional
        if not source.exists():
            source = run_dir / "outputs" / optional
        if not source.exists():
            source = run_dir / "style" / optional
        if source.exists():
            shutil.copy2(source, template_dir / optional)

    assets = run_dir / "assets"
    if not assets.exists():
        assets = run_dir / "outputs" / "assets"
    if assets.exists():
        shutil.copytree(assets, template_dir / "assets")

    print(template_dir)


if __name__ == "__main__":
    main()
