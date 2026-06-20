#!/usr/bin/env python3
# /// script
# dependencies = ["yandex-ai-studio-sdk"]
# ///
"""Synchronous Yandex Web Search (Russian index) via AI Studio SDK.

Reads YC_API_KEY and YC_FOLDER_ID from the environment.
Outputs JSON to stdout.

Usage:
    uv run search.py "query text" [options]
"""

import argparse
import json
import sys

from yandex_ai_studio_sdk import AIStudio


def main() -> None:
    p = argparse.ArgumentParser(
        description="Synchronous Yandex web search. Always searches the Russian index."
    )
    p.add_argument("query", help="Search query text (max 400 chars)")
    p.add_argument(
        "--page",
        type=int,
        default=0,
        metavar="N",
        help="Page number, 0-based (default: 0)",
    )
    p.add_argument(
        "--family-mode",
        choices=["NONE", "MODERATE", "STRICT"],
        default="NONE",
        help=(
            "Content filter: "
            "NONE=no filtering (default), "
            "MODERATE=exclude adult unless query targets it, "
            "STRICT=exclude adult and profanity always"
        ),
    )
    p.add_argument(
        "--fix-typo-mode",
        choices=["ON", "OFF"],
        default="ON",
        help="Typo correction: ON=auto-correct (default), OFF=exact query",
    )
    p.add_argument(
        "--sort-mode",
        choices=["BY_RELEVANCE", "BY_TIME"],
        default="BY_RELEVANCE",
        help="Sort rule: BY_RELEVANCE (default) or BY_TIME",
    )
    p.add_argument(
        "--sort-order",
        choices=["DESC", "ASC"],
        default="DESC",
        help="Sort order: DESC=newest first (default), ASC=oldest first (only with BY_TIME)",
    )
    p.add_argument(
        "--group-mode",
        choices=["DEEP", "FLAT"],
        default="DEEP",
        help="Grouping: DEEP=one group per domain (default), FLAT=one doc per group",
    )
    p.add_argument(
        "--groups-on-page",
        type=int,
        default=10,
        metavar="1-100",
        help="Max result groups per page, 1-100 (default: 10)",
    )
    p.add_argument(
        "--docs-in-group",
        type=int,
        default=1,
        metavar="1-3",
        help="Max documents per group, 1-3 (default: 1)",
    )
    p.add_argument(
        "--max-passages",
        type=int,
        default=4,
        metavar="1-5",
        help="Max text snippets per document, 1-5 (default: 4)",
    )
    p.add_argument(
        "--region",
        default="",
        metavar="ID",
        help="Yandex region ID affecting ranking, e.g. 213=Moscow, 2=Saint Petersburg",
    )
    p.add_argument(
        "--localization",
        choices=["RU", "BE", "KK", "UK"],
        default="RU",
        help=(
            "Language for error messages and count annotations "
            "(Russian index only): RU (default), BE, KK, UK"
        ),
    )
    p.add_argument(
        "--user-agent",
        default="",
        metavar="STRING",
        help="User-Agent header to optimise results for a specific browser or device",
    )

    args = p.parse_args()

    sdk = AIStudio()
    search = sdk.search_api.web(
        search_type="RU",
        family_mode=args.family_mode,
        fix_typo_mode=args.fix_typo_mode,
        sort_mode=args.sort_mode,
        sort_order=args.sort_order,
        group_mode=args.group_mode,
        groups_on_page=args.groups_on_page,
        docs_in_group=args.docs_in_group,
        max_passages=args.max_passages,
        localization=args.localization,
        region=args.region or None,
        user_agent=args.user_agent or None,
    )

    result = search.run(args.query, page=args.page)

    output = {
        "query": args.query,
        "page": args.page,
        "documents": [
            {
                "url": doc.url,
                "domain": doc.domain,
                "title": doc.title,
                "modtime": doc.modtime.isoformat() if doc.modtime else None,
                "lang": doc.lang,
                "passages": list(doc.passages),
            }
            for doc in result.docs
        ],
    }

    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
