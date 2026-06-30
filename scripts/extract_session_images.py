#!/usr/bin/env python3
"""Extract Codex Desktop built-in image generation results from a session JSONL."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Decode image_generation_call results from a Codex session JSONL."
    )
    parser.add_argument("session_jsonl", type=Path, help="Path to rollout-*.jsonl")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output assets directory")
    parser.add_argument("--last", type=int, default=1)
    parser.add_argument("--names", default="")
    parser.add_argument("--lines", default="")
    return parser.parse_args()


def image_payload(obj: dict[str, Any]) -> str | None:
    payload = obj.get("payload")
    if not isinstance(payload, dict):
        return None
    result = payload.get("result")
    if not isinstance(result, str) or not result:
        return None
    payload_type = payload.get("type")
    if payload_type and "image_generation" not in str(payload_type):
        return None
    return result


def load_records(path: Path) -> list[tuple[int, str]]:
    records: list[tuple[int, str]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line_no, line in enumerate(handle, 1):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            result = image_payload(obj)
            if result:
                records.append((line_no, result))
    return records


def decode_png(data: str) -> bytes:
    raw = base64.b64decode(data)
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Decoded image is not a PNG")
    return raw


def main() -> int:
    args = parse_args()
    records = load_records(args.session_jsonl)
    if not records:
        raise SystemExit(f"No image generation results found in {args.session_jsonl}")

    if args.lines:
        wanted = {int(item.strip()) for item in args.lines.split(",") if item.strip()}
        selected = [record for record in records if record[0] in wanted]
    else:
        selected = records[-args.last :]

    names = [name.strip() for name in args.names.split(",") if name.strip()]
    if names and len(names) != len(selected):
        raise SystemExit("--names count must match selected image count")
    if not names:
        names = [f"image-{idx:02d}.png" for idx in range(1, len(selected) + 1)]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for (line_no, data), name in zip(selected, names):
        output_path = args.out_dir / name
        output_path.write_bytes(decode_png(data))
        print(f"line {line_no}: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

