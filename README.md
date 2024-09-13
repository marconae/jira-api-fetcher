# Jira API Fetcher

A Python module that provides the `JiraApiFetcher` class, which fetches data from the Jira API.

`JiraApiFetcher` is compatible with the following versions of the API:
* [Agile REST API](https://developer.atlassian.com/cloud/jira/software/rest/intro)
* [REST API v2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro/)
* [REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)

## Response handling

The responses of the Jira API can typically be handled by one of the three methods:

fetch_array
: Fetches data from a Jira API endpoint as an array and raises an exception if the response is not successful.

fetch_issues
: Fetches Jira issues, optionally with specified fields and JQL, and supports pagination.

fetch_paginated
: Handles pagination while fetching data, aggregates results, and allows for additional parameters via a JSON string.

See the provided docstring of the class for usage of the methods.

## Tested Endpoints

| Endpoint   | Method          |
|------------|-----------------|
| `rest/agile/1.0/board/21/issue` | `fetch_issues`  |
| `rest/agile/1.0/board/21/version` | `fetch_paginated` |
| `rest/agile/1.0/board/21/sprint` | `fetch_paginated` |
| `rest/api/2/search` | `fetch_issues`  |
| `rest/api/2/priority` | `fetch_array` |
| `rest/api/2/user/search/query` | `fetch_paginated` |
| `rest/api/3/issuetype` | `fetch_array` |
| `rest/api/3/statuses/search` | `fetch_paginated` |
| `rest/api/3/project` | `fetc_array` |
| `rest/api/3/resolution` | `fetc_array` |

## Examples

### Fetch Jira Issues based on a JQL

The following example shows how to fetch Issues based on a JQL.

1. Create a `JiraConnection` instance
2. Create an instancen of `JiraApiFetcher`
3. Use method `fetch_issues`

The used JQL fetches all issues in project `MY_PROJECT` that have been created within the last 5 days. The fetched fields are limited to `resolution` and `updated`.

```python
connection = JiraConnection('https://foo.atlassian.net',
                            'bart.simpson',
                            '****')

fetcher = JiraApiFetcher(connection)

endpoint = 'rest/api/2/search'
jql = f'project = "MY_PROJECT" AND created >= -5d ORDER BY created DESC'
fields = 'resolution,updated'

data = fetcher.fetch_issues(endpoint=endpoint, fields_str=fields, jql=jql, fetch_size=10)

print(data)
```

