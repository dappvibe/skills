# Web Search API, REST: Wordstat.GetTop | AI Studio documentation

The method returns the last 30 days data about popular queries containing the specified keyword and queries that are similar to the specified one.

## HTTP request

```
POST https://searchapi.api.cloud.yandex.net/v2/wordstat/topRequests
```

## Body parameters

```
{
  "phrase": "string",
  "numPhrases": "string",
  "regions": [
    "string"
  ],
  "devices": [
    "string"
  ],
  "folderId": "string"
}
```

| Field | Description |
| phrase | **string**

Required field. Keyword

The maximum string length in characters is 400. |
| numPhrases | **string** (int64)

Number of the phrases in the response.

Acceptable values are 1 to 2000, inclusive. |
| regions\[\] | **string**

A list of IDs of the regions a query was made from.

The maximum number of elements is 100. |
| devices\[\] | **enum** (Device)

A list of device types a query was made from.

The maximum number of elements is 3.

-   `DEVICE_ALL`: All devices.

-   `DEVICE_DESKTOP`: Desktop computers.
-   `DEVICE_PHONE`: Phones.

-   `DEVICE_TABLET`: Tablets. |
| folderId | **string**

ID of the folder.

The maximum string length in characters is 50. |

## Response

**HTTP Code: 200 - OK**

```
{
  "totalCount": "string",
  "results": [
    {
      "phrase": "string",
      "count": "string"
    }
  ],
  "associations": [
    {
      "phrase": "string",
      "count": "string"
    }
  ]
}
```

| Field | Description |
| totalCount | **string** (int64)

Total number of the queries that contain all the keywords, regardless of their order. |
| results\[\] | **[PhraseInfo](https://aistudio.yandex.ru/docs/en/search-api/api-ref/Wordstat/getTop#yandex.cloud.searchapi.v2.GetTopResponse.PhraseInfo)**

Results. |
| associations\[\] | **[PhraseInfo](https://aistudio.yandex.ru/docs/en/search-api/api-ref/Wordstat/getTop#yandex.cloud.searchapi.v2.GetTopResponse.PhraseInfo)**

Queries that are similar to the specified one. |

## PhraseInfo

| Field | Description |
| phrase | **string**

Keyword. |
| count | **string** (int64)

Number of queries made. |

Previous

Next

---
Source: [Web Search API, REST: Wordstat.GetTop](https://aistudio.yandex.ru/docs/en/search-api/api-ref/Wordstat/getTop.html)