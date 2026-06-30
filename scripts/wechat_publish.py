#!/usr/bin/env python3
"""Publish a WeChat Official Account draft, or check publish status.

Environment variables:
  WECHAT_APP_ID
  WECHAT_APP_SECRET

Safety:
  This script does not publish unless --execute is passed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
FREEPUBLISH_SUBMIT_URL = "https://api.weixin.qq.com/cgi-bin/freepublish/submit"
FREEPUBLISH_GET_URL = "https://api.weixin.qq.com/cgi-bin/freepublish/get"


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


def publish_draft(access_token: str, draft_media_id: str) -> dict[str, Any]:
    params = urllib.parse.urlencode({"access_token": access_token})
    return post_json_url(f"{FREEPUBLISH_SUBMIT_URL}?{params}", {"media_id": draft_media_id})


def get_publish_status(access_token: str, publish_id: str) -> dict[str, Any]:
    params = urllib.parse.urlencode({"access_token": access_token})
    return post_json_url(f"{FREEPUBLISH_GET_URL}?{params}", {"publish_id": publish_id})


def load_draft_media_id(value: str) -> str:
    path = Path(value)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if "draft_media_id" in data:
            return str(data["draft_media_id"])
        if "media_id" in data:
            return str(data["media_id"])
        fail(f"No draft_media_id or media_id found in {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft-media-id", help="Draft media_id, or path to draft report JSON")
    parser.add_argument("--publish-id", help="Publish task id for status check")
    parser.add_argument("--execute", action="store_true", help="Actually submit the draft for publishing")
    parser.add_argument("--status", action="store_true", help="Check publish status for --publish-id")
    parser.add_argument("--out-report", type=Path, default=None)
    args = parser.parse_args()

    app_id = os.environ.get("WECHAT_APP_ID")
    app_secret = os.environ.get("WECHAT_APP_SECRET")
    if not app_id or not app_secret:
        fail("Set WECHAT_APP_ID and WECHAT_APP_SECRET")

    if args.status:
        if not args.publish_id:
            fail("--status requires --publish-id")
        access_token = get_access_token(app_id, app_secret)
        result = get_publish_status(access_token, args.publish_id)
        report = {
            "mode": "status",
            "checked_at": datetime.now().isoformat(timespec="seconds"),
            "publish_id": args.publish_id,
            "result": result,
        }
    else:
        if not args.draft_media_id:
            fail("Publishing requires --draft-media-id")
        draft_media_id = load_draft_media_id(args.draft_media_id)
        if not args.execute:
            report = {
                "mode": "dry-run",
                "message": "No publish request was sent. Re-run with --execute to submit.",
                "draft_media_id": draft_media_id,
            }
        else:
            access_token = get_access_token(app_id, app_secret)
            result = publish_draft(access_token, draft_media_id)
            report = {
                "mode": "published_request_sent",
                "submitted_at": datetime.now().isoformat(timespec="seconds"),
                "draft_media_id": draft_media_id,
                "result": result,
            }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out_report:
        args.out_report.parent.mkdir(parents=True, exist_ok=True)
        args.out_report.write_text(text, encoding="utf-8")
        print(args.out_report.resolve())
    print(text)


if __name__ == "__main__":
    main()
