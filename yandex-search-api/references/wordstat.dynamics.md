# Web Search API, REST: Wordstat.GetDynamics | Документация AI Studio

The method returns the frequency of queries over time for a given keyword.

## HTTP request

```
POST https://searchapi.api.cloud.yandex.net/v2/wordstat/dynamics
```

## Body parameters

```
{
  "phrase": "string",
  "period": "string",
  "fromDate": "string",
  "toDate": "string",
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

Required field. Keyword.

The maximum string length in characters is 400. |
| period | **enum** (Period)

Required field. The period of aggregation of the number of queries.

-   `PERIOD_MONTHLY`: Details by month.

-   `PERIOD_WEEKLY`: Details by week.
-   `PERIOD_DAILY`: Details by day. |
| fromDate | **string** (date-time)

Required field. The start of the period data is requested for.

String in [RFC3339](https://www.ietf.org/rfc/rfc3339.txt) text format. The range of possible values is from  
`0001-01-01T00:00:00Z` to `9999-12-31T23:59:59.999999999Z`, i.e. from 0 to 9 digits for fractions of a second.

To work with values in this field, use the APIs described in the  
[Protocol Buffers reference](https://developers.google.com/protocol-buffers/docs/reference/overview).  
In some languages, built-in datetime utilities do not support nanosecond precision (9 digits). |
| toDate | **string** (date-time)

The end of the period data is requested for.

String in [RFC3339](https://www.ietf.org/rfc/rfc3339.txt) text format. The range of possible values is from  
`0001-01-01T00:00:00Z` to `9999-12-31T23:59:59.999999999Z`, i.e. from 0 to 9 digits for fractions of a second.

To work with values in this field, use the APIs described in the  
[Protocol Buffers reference](https://developers.google.com/protocol-buffers/docs/reference/overview).  
In some languages, built-in datetime utilities do not support nanosecond precision (9 digits). |
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
  "results": [
    {
      "date": "string",
      "count": "string",
      "share": "string"
    }
  ]
}
```

## DynamicsInfo

| Field | Description |
| date | **string** (date-time)

The date

String in [RFC3339](https://www.ietf.org/rfc/rfc3339.txt) text format. The range of possible values is from  
`0001-01-01T00:00:00Z` to `9999-12-31T23:59:59.999999999Z`, i.e. from 0 to 9 digits for fractions of a second.

To work with values in this field, use the APIs described in the  
[Protocol Buffers reference](https://developers.google.com/protocol-buffers/docs/reference/overview).  
In some languages, built-in datetime utilities do not support nanosecond precision (9 digits). |
| count | **string** (int64)

Number of queries containing the given keyword |
| share | **string**

The share of the number of such queries from the total number of queries to Yandex. |

---
Source: [Web Search API, REST: Wordstat.GetDynamics](https://aistudio.yandex.ru/docs/ru/search-api/api-ref/Wordstat/getDynamics.html)