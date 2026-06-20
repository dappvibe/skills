---
name: yandex-search-api
description: Use this skill whenever the user asks to search the web, look something up online, find information, research a topic, or analyse keyword/search demand for market research. Provides two scripts: web search (search.py) and Yandex Wordstat keyword stats (wordstat.py).
---

# Yandex Web Search

When the user asks to search the web, run `scripts/search.py` with the appropriate query and flags. Read the JSON output and summarise the findings for the user.

**Never fabricate results.** Only report what is present in the JSON output of the script. If the script fails, returns an empty `documents` array, or is not run for any reason — tell the user that the search did not return results. Do not guess, invent URLs, or fill in from memory.

## Before running the script

Install the SDK library once into the local user environment:

```bash
pip install yandex-ai-studio-sdk --user --break-system-packages
```

Then run the script:

```bash
uv run --script skills/yandex-search-api/scripts/search.py "query"
```

The script always searches the **Russian index** and returns **JSON** to stdout.

## All flags

| Flag | Default | Allowed values | Description |
|------|---------|---------------|-------------|
| `query` | *(required)* | string ≤ 400 chars | Search query text |
| `--page` | `0` | integer ≥ 0 | Page number, 0-based; use to fetch more results |
| `--family-mode` | `NONE` | `NONE` `MODERATE` `STRICT` | `NONE`=no filtering, `MODERATE`=hide adult content, `STRICT`=strictest filter |
| `--fix-typo-mode` | `ON` | `ON` `OFF` | `ON`=auto-correct typos, `OFF`=exact query |
| `--sort-mode` | `BY_RELEVANCE` | `BY_RELEVANCE` `BY_TIME` | Sort by relevance or recency |
| `--sort-order` | `DESC` | `DESC` `ASC` | Direction for time-based sort |
| `--group-mode` | `DEEP` | `DEEP` `FLAT` | `DEEP`=one group per domain, `FLAT`=one doc per group |
| `--groups-on-page` | `10` | 1–100 | Number of result groups returned |
| `--docs-in-group` | `1` | 1–3 | Documents per group |
| `--max-passages` | `4` | 1–5 | Text snippets per document |
| `--region` | *(none)* | Yandex region ID | Ranking region. Common: `213`=Moscow, `2`=Saint Petersburg |
| `--localization` | `RU` | `RU` `BE` `KK` `UK` | Language for system messages |
| `--user-agent` | *(none)* | UA string | Target a specific device (e.g. mobile) |

## Output format

```json
{
  "query": "запрос",
  "page": 0,
  "documents": [
    {
      "url": "https://example.com/page",
      "domain": "example.com",
      "title": "Page title",
      "modtime": "2025-03-01T12:00:00",
      "lang": "ru",
      "passages": ["...snippet matching the query..."]
    }
  ]
}
```

Read `title`, `url`, and `passages` to answer the user. Fetch more results with `--page 1`, `--page 2`, etc.

## Wordstat — keyword demand stats (market research)

Use `scripts/wordstat.py` when the user wants to research search demand, find popular query variations, or validate keyword ideas. Data covers the **last 30 days** across Yandex.

See full API reference: `skills/yandex-search-api/references/wordstat.gettop..md`

```bash
python3 skills/yandex-search-api/scripts/wordstat.py "keyword" [options]
```

No extra dependencies — uses only stdlib `urllib`.

### Flags

| Flag | Default | Allowed values | Description |
|------|---------|---------------|-------------|
| `phrase` | *(required)* | string ≤ 400 chars | Keyword to look up |
| `--num-phrases` | `50` | 1–2000 | How many phrases to return |
| `--regions` | *(all)* | Yandex region IDs | Filter by region, e.g. `--regions 213 2` |
| `--devices` | `DEVICE_ALL` | `DEVICE_ALL` `DEVICE_DESKTOP` `DEVICE_PHONE` `DEVICE_TABLET` | Filter by device type |

### Output format

```json
{
  "phrase": "keyword",
  "total_count": 182374,
  "results": [
    { "phrase": "keyword something", "count": 45210 },
    { "phrase": "buy keyword", "count": 31500 }
  ],
  "associations": [
    { "phrase": "related term", "count": 12000 }
  ]
}
```

- **`total_count`** — total queries containing all keywords regardless of order
- **`results`** — popular queries that include the phrase, sorted by volume
- **`associations`** — semantically similar queries users also searched for

**Never fabricate counts or phrases.** Only report what the script returns.

## If credentials are missing

Check whether the required env vars are set:

```bash
echo "YC_API_KEY=${YC_API_KEY:+set}" && echo "YC_FOLDER_ID=${YC_FOLDER_ID:+set}"
```

If either is missing, ask the user to provide them. Explain:

- **`YC_API_KEY`** — a Yandex Cloud service account API key with the `search.editor` role. The user can create one in the [Yandex Cloud console](https://console.yandex.cloud/) under **IAM → Service accounts → API keys**.
- **`YC_FOLDER_ID`** — the ID of the Yandex Cloud folder to bill for requests. Visible in the console URL or in folder settings.

Once the user has the values, ask them to export both and retry:

```bash
export YC_API_KEY=<key>
export YC_FOLDER_ID=<folder_id>
```

## Error codes

| Code | Cause |
|------|-------|
| `UNAUTHENTICATED` | `YC_API_KEY` missing or invalid |
| `PERMISSION_DENIED` | Service account lacks `search.editor` on the folder |
| `RESOURCE_EXHAUSTED` | Quota exceeded |
