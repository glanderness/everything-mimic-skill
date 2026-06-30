#!/usr/bin/env python3
"""Create a WeChat Official Account draft from prepared article HTML.

Environment variables:
  WECHAT_APP_ID
  WECHAT_APP_SECRET

This creates a draft only. It does not publish.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image


TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
ADD_MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
DRAFT_ADD_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"


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


def post_json_url(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read().decode("utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        fail(f"Expected JSON response, got: {raw[:300]}")


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
        fail(f"Expected JSON from multipart upload, got: {raw[:300]}")


def prepare_thumb(src: Path, out: Path, max_bytes: int = 60 * 1024) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(src).convert("RGB")
    # Use a 2.35:1-ish crop that works for official account cover previews.
    target_ratio = 2.35
    ratio = image.width / image.height
    if ratio > target_ratio:
        new_width = int(image.height * target_ratio)
        left = (image.width - new_width) // 2
        image = image.crop((left, 0, left + new_width, image.height))
    elif ratio < target_ratio:
        new_height = int(image.width / target_ratio)
        top = max(0, (image.height - new_height) // 2)
        image = image.crop((0, top, image.width, top + new_height))

    widths = [900, 720, 600, 480, 360]
    qualities = [82, 74, 66, 58, 50, 42]
    for width in widths:
        work = image.copy()
        if work.width > width:
            height = round(work.height * width / work.width)
            work = work.resize((width, height), Image.Resampling.LANCZOS)
        for quality in qualities:
            work.save(out, format="JPEG", quality=quality, optimize=True)
            if out.stat().st_size <= max_bytes:
                return out
    fail(f"Could not prepare thumb under {max_bytes} bytes")


def upload_permanent_material(access_token: str, file_path: Path, media_type: str) -> dict[str, Any]:
    params = urllib.parse.urlencode({"access_token": access_token, "type": media_type})
    return multipart_upload(f"{ADD_MATERIAL_URL}?{params}", "media", file_path)


def create_draft(
    access_token: str,
    *,
    title: str,
    author: str,
    digest: str,
    content: str,
    thumb_media_id: str,
    content_source_url: str = "",
) -> dict[str, Any]:
    params = urllib.parse.urlencode({"access_token": access_token})
    payload = {
        "articles": [
            {
                "title": title,
                "author": author,
                "digest": digest,
                "content": content,
                "content_source_url": content_source_url,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }
        ]
    }
    return post_json_url(f"{DRAFT_ADD_URL}?{params}", payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="Article HTML whose img URLs are already WeChat-hosted")
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", default="")
    parser.add_argument("--digest", default="")
    parser.add_argument("--cover", type=Path, required=True, help="Local cover source image")
    parser.add_argument("--out-report", type=Path, required=True)
    parser.add_argument("--thumb-out", type=Path, default=None)
    args = parser.parse_args()

    app_id = os.environ.get("WECHAT_APP_ID")
    app_secret = os.environ.get("WECHAT_APP_SECRET")
    if not app_id or not app_secret:
        fail("Set WECHAT_APP_ID and WECHAT_APP_SECRET")

    html_path = args.html.resolve()
    cover_path = args.cover.resolve()
    if not html_path.exists():
        fail(f"HTML not found: {html_path}")
    if not cover_path.exists():
        fail(f"Cover not found: {cover_path}")

    content = html_path.read_text(encoding="utf-8")
    thumb_out = args.thumb_out or html_path.parent / "wechat-draft-thumb.jpg"
    thumb = prepare_thumb(cover_path, Path(thumb_out))

    access_token = get_access_token(app_id, app_secret)
    thumb_result = upload_permanent_material(access_token, thumb, "thumb")
    if "media_id" not in thumb_result:
        fail(f"Could not upload thumb material: {json.dumps(thumb_result, ensure_ascii=False)}")

    draft_result = create_draft(
        access_token,
        title=args.title,
        author=args.author,
        digest=args.digest,
        content=content,
        thumb_media_id=str(thumb_result["media_id"]),
    )
    if "media_id" not in draft_result:
        fail(f"Could not create draft: {json.dumps(draft_result, ensure_ascii=False)}")

    report = {
        "mode": "draft_created",
        "title": args.title,
        "html": str(html_path),
        "cover_source": str(cover_path),
        "thumb_file": str(thumb.resolve()),
        "thumb_bytes": thumb.stat().st_size,
        "thumb_media_id": thumb_result["media_id"],
        "draft_media_id": draft_result["media_id"],
        "raw_thumb_result": thumb_result,
        "raw_draft_result": draft_result,
    }
    args.out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.out_report.resolve())
    print(f"draft_media_id={draft_result['media_id']}")


if __name__ == "__main__":
    main()
