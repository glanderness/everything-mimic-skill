#!/usr/bin/env python3
"""Upload article images with WeChat media/uploadimg and rewrite HTML.

Environment variables:
  WECHAT_APP_ID
  WECHAT_APP_SECRET

The script compresses local PNG/JPG images under the uploadimg size limit,
uploads them to WeChat's article-image endpoint, then rewrites img src values
in the provided HTML to the returned WeChat-hosted URLs.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image


TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
UPLOADIMG_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
DEFAULT_MAX_BYTES = 950 * 1024


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_json_url(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as response:
        body = response.read().decode("utf-8")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        fail(f"Expected JSON from {url}, got: {body[:300]}")


def get_access_token(app_id: str, app_secret: str) -> str:
    params = urllib.parse.urlencode(
        {
            "grant_type": "client_credential",
            "appid": app_id,
            "secret": app_secret,
        }
    )
    data = read_json_url(f"{TOKEN_URL}?{params}")
    if "access_token" not in data:
        fail(f"Could not obtain access_token: {json.dumps(data, ensure_ascii=False)}")
    return str(data["access_token"])


def compress_for_upload(src: Path, out_dir: Path, max_bytes: int) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    if src.stat().st_size <= max_bytes and src.suffix.lower() in {".jpg", ".jpeg", ".png"}:
        return src

    image = Image.open(src).convert("RGB")
    base = out_dir / f"{src.stem}.jpg"

    # First reduce dimensions if the source is large. WeChat editor displays at
    # mobile width, so huge 1600px+ diagrams rarely need original dimensions.
    max_widths = [1400, 1200, 1000, 900, 800, 700]
    qualities = [88, 82, 76, 70, 64, 58, 52, 46]

    for max_width in max_widths:
        work = image.copy()
        if work.width > max_width:
            new_height = round(work.height * max_width / work.width)
            work = work.resize((max_width, new_height), Image.Resampling.LANCZOS)
        for quality in qualities:
            work.save(base, format="JPEG", quality=quality, optimize=True, progressive=True)
            if base.stat().st_size <= max_bytes:
                return base

    fail(f"Could not compress {src} under {max_bytes} bytes")


def multipart_upload(url: str, field_name: str, file_path: Path) -> dict[str, Any]:
    boundary = f"----everything-mimic-{int(time.time() * 1000)}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()

    parts = [
        f"--{boundary}\r\n".encode(),
        (
            f'Content-Disposition: form-data; name="{field_name}"; '
            f'filename="{file_path.name}"\r\n'
        ).encode(),
        f"Content-Type: {content_type}\r\n\r\n".encode(),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    body = b"".join(parts)
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read().decode("utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        fail(f"Expected JSON from uploadimg, got: {raw[:300]}")


def upload_image(access_token: str, file_path: Path) -> str:
    params = urllib.parse.urlencode({"access_token": access_token})
    data = multipart_upload(f"{UPLOADIMG_URL}?{params}", "media", file_path)
    if "url" not in data:
        fail(f"uploadimg failed for {file_path}: {json.dumps(data, ensure_ascii=False)}")
    return str(data["url"])


def extract_img_sources(html: str) -> list[str]:
    return re.findall(r'<img[^>]+src="([^"]+)"', html)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="Input article HTML with local img src values")
    parser.add_argument("--project-dir", type=Path, default=None, help="Base dir for resolving local image paths")
    parser.add_argument("--out", type=Path, required=True, help="Output HTML with WeChat-hosted image URLs")
    parser.add_argument("--map", type=Path, default=None, help="Output JSON map")
    parser.add_argument("--prepared-dir", type=Path, default=None, help="Where compressed upload files are saved")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--dry-run", action="store_true", help="Only compress and report; do not call WeChat APIs")
    args = parser.parse_args()

    html_path = args.html.resolve()
    project_dir = args.project_dir.resolve() if args.project_dir else html_path.parent
    prepared_dir = args.prepared_dir or project_dir / "wechat-upload-prepared"
    map_path = args.map or project_dir / "wechat-upload-map.json"

    html = html_path.read_text(encoding="utf-8")
    sources = extract_img_sources(html)
    if not sources:
        fail("No <img src=\"...\"> values found")

    local_sources = [src for src in sources if not src.startswith(("http://", "https://", "data:"))]
    if not local_sources:
        fail("No local image sources found to upload")

    app_id = os.environ.get("WECHAT_APP_ID")
    app_secret = os.environ.get("WECHAT_APP_SECRET")
    if not args.dry_run and (not app_id or not app_secret):
        fail("Set WECHAT_APP_ID and WECHAT_APP_SECRET, or run with --dry-run")

    upload_plan: list[dict[str, Any]] = []
    for src in local_sources:
        local_path = (project_dir / src).resolve()
        if not local_path.exists():
            fail(f"Image not found: {src} -> {local_path}")
        prepared = compress_for_upload(local_path, prepared_dir, args.max_bytes)
        upload_plan.append(
            {
                "source": src,
                "local_path": str(local_path),
                "prepared_path": str(prepared.resolve()),
                "original_bytes": local_path.stat().st_size,
                "prepared_bytes": prepared.stat().st_size,
            }
        )

    if args.dry_run:
        result = {"mode": "dry-run", "images": upload_plan}
        map_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(map_path.resolve())
        return

    assert app_id and app_secret
    access_token = get_access_token(app_id, app_secret)

    rewritten = html
    for item in upload_plan:
        url = upload_image(access_token, Path(item["prepared_path"]))
        item["wechat_url"] = url
        rewritten = rewritten.replace(f'src="{item["source"]}"', f'src="{url}"')

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rewritten, encoding="utf-8")
    result = {"mode": "uploaded", "images": upload_plan, "output_html": str(args.out.resolve())}
    map_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.out.resolve())
    print(map_path.resolve())


if __name__ == "__main__":
    main()
