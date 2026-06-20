#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Yandex Wordstat Dynamics — query frequency over time for a keyword.

Reads YC_API_KEY and YC_FOLDER_ID from the environment.
Outputs JSON to stdout.

Usage:
    python3 wordstat_dynamics.py "keyword" --from-date 2025-01-01 [options]

Reference: skills/yandex-search-api/references/wordstat.dynamics.md
"""

import argparse
import calendar
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

API_URL = "https://searchapi.api.cloud.yandex.net/v2/wordstat/dynamics"


def to_rfc3339(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def snap_to_period_end(date_str: str, period: str) -> str:
    """Snap date to the last day of its period as required by the API."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if period == "PERIOD_MONTHLY":
        last_day = calendar.monthrange(dt.year, dt.month)[1]
        dt = dt.replace(day=last_day)
    elif period == "PERIOD_WEEKLY":
        # snap to Sunday (weekday 6)
        dt = dt + timedelta(days=(6 - dt.weekday()))
    return dt.strftime("%Y-%m-%d")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Get search query frequency over time for a keyword via Yandex Wordstat."
    )
    p.add_argument("phrase", help="Keyword to look up (max 400 chars)")
    p.add_argument(
        "--period",
        choices=["PERIOD_MONTHLY", "PERIOD_WEEKLY", "PERIOD_DAILY"],
        default="PERIOD_MONTHLY",
        help="Aggregation period (default: PERIOD_MONTHLY)",
    )
    p.add_argument(
        "--from-date",
        required=True,
        metavar="YYYY-MM-DD",
        help="Start of the date range (required)",
    )
    p.add_argument(
        "--to-date",
        metavar="YYYY-MM-DD",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        help="End of the date range (default: today)",
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

    to_date = snap_to_period_end(args.to_date, args.period)

    payload = {
        "phrase": args.phrase,
        "period": args.period,
        "fromDate": to_rfc3339(args.from_date),
        "toDate": to_rfc3339(to_date),
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
        "period": args.period,
        "from_date": args.from_date,
        "to_date": to_date,
        "results": [
            {
                "date": r["date"][:10],
                "count": int(r["count"]),
                "share": r.get("share", ""),
            }
            for r in data.get("results", [])
        ],
    }

    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
