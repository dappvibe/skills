#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Yandex Wordstat — popular queries containing a keyword (last 30 days).

Reads YC_API_KEY and YC_FOLDER_ID from the environment.
Outputs JSON to stdout.

Usage:
    python wordstat.py "keyword" [options]

Reference: skills/yandex-search-api/references/wordstat.gettop..md
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_URL = "https://searchapi.api.cloud.yandex.net/v2/wordstat/topRequests"


def main() -> None:
    p = argparse.ArgumentParser(
        description="Get popular search queries containing a keyword via Yandex Wordstat."
    )
    p.add_argument("phrase", help="Keyword to look up (max 400 chars)")
    p.add_argument(
        "--num-phrases",
        type=int,
        default=50,
        metavar="1-2000",
        help="Number of phrases to return (default: 50, max: 2000)",
    )
    p.add_argument(
        "--regions",
        nargs="*",
        default=[],
        metavar="ID",
        help="Region IDs to filter by, e.g. --regions 213 2 (max 100)",
    )
    p.add_argument(
        "--devices",
        nargs="*",
        choices=["DEVICE_ALL", "DEVICE_DESKTOP", "DEVICE_PHONE", "DEVICE_TABLET"],
        default=["DEVICE_ALL"],
        help="Device types to filter by (default: DEVICE_ALL)",
    )

    args = p.parse_args()

    api_key = os.environ.get("YC_API_KEY", "")
    folder_id = os.environ.get("YC_FOLDER_ID", "")

    if not api_key or not folder_id:
        missing = [v for v, k in [("YC_API_KEY", api_key), ("YC_FOLDER_ID", folder_id)] if not k]
        print(json.dumps({"error": f"Missing environment variables: {', '.join(missing)}"}))
        sys.exit(1)

    payload = {
        "phrase": args.phrase,
        "numPhrases": str(args.num_phrases),
        "folderId": folder_id,
        "devices": args.devices,
    }
    if args.regions:
        payload["regions"] = args.regions

    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(json.dumps({"error": f"HTTP {e.code}: {error_body}"}))
        sys.exit(1)

    output = {
        "phrase": args.phrase,
        "total_count": int(data.get("totalCount", 0)),
        "results": [
            {"phrase": r["phrase"], "count": int(r["count"])}
            for r in data.get("results", [])
        ],
        "associations": [
            {"phrase": r["phrase"], "count": int(r["count"])}
            for r in data.get("associations", [])
        ],
    }

    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
