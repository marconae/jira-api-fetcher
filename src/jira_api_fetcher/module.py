import json
import urllib.parse
import requests
from .etc import JiraConnection, JiraApiError

DEFAULT_HEADERS = {
    "Content-Type": "application/json"
}


class JiraApiFetcher:
    def __init__(self, connection: JiraConnection):
        self.connection = connection

    def fetch_array(self, endpoint):
        """
        Fetches an array of data from the specified Jira API endpoint.

        This method sends a GET request to the provided endpoint and returns the JSON response as an array.
        If the response status code is not 200, it raises a JiraApiError with the response details.

        Args:
            endpoint (str): The API endpoint to fetch data from.

        Returns:
            list or dict: The JSON response from the API.

        Raises:
            JiraApiError: If the response status code is not 200.
        """
        url = self._get_url(endpoint)

        response = self._get_response(url)

        if response.status_code != 200:
            msg = f"Failed to fetch data as array: {response.text}"
            raise JiraApiError(msg, response.status_code)

        return response.json()

    def fetch_paginated(self, endpoint: str, fetch_size: int = 50, params_json: str = None):
        """
        Fetches paginated data from the specified Jira API endpoint.

        This method iteratively sends GET requests to the provided endpoint, handling pagination
        based on the `fetch_size`. It aggregates the results across all pages and returns the
        complete set of data.

        Args:
            endpoint (str): The API endpoint to fetch paginated data from.
            fetch_size (int, optional): The number of results to fetch per request/page (default is 50).
            params_json (str, optional): Additional parameters in JSON format to include in the request.

        Returns:
            list: The aggregated data from all pages.

        Raises:
            ValueError: If `fetch_size` is less than 1.
            json.JSONDecodeError: If `params_json` is provided but is not valid JSON.
            JiraApiError: If the response status code is not 200.
        """
        url = self._get_url(endpoint)

        if fetch_size < 1:
            raise ValueError('fetch_size must be >= 1')

        start_at = 0
        has_next = True

        data = []

        while has_next:

            params = {
                "startAt": start_at,
                "maxResults": fetch_size
            }

            if params_json is not None:
                try:
                    add_params = json.loads(params_json)
                    params = {**params, **add_params}
                except json.JSONDecodeError:
                    raise

            response = self._get_response(url, params)

            if response.status_code != 200:
                msg = f"Failed to fetch paginated values: {response.text}"
                raise JiraApiError(msg, response.status_code)

            page_data = response.json()
            has_next = not page_data["isLast"]
            page_data_values = page_data["values"]

            data.extend(page_data_values)

            start_at += len(page_data_values)

        return data

    def fetch_issues(self, endpoint: str, fetch_size: int = 50, fields_str: str = None, jql: str = None):
        """
        Fetches Jira issues from the specified API endpoint.

        This method sends GET requests to the provided endpoint and handles pagination,
        fetching issues in batches based on `fetch_size`. Additional filters such as `fields`
        and `JQL` can be provided to refine the query.

        Args:
            endpoint (str): The API endpoint to fetch Jira issues from.
            fetch_size (int, optional): The number of issues to fetch per request (default is 50).
            fields_str (str, optional): A comma-separated string of fields to include in the results.
            jql (str, optional): A JQL (Jira Query Language) string to filter the issues.

        Returns:
            list: A list of issues fetched from the Jira API.

        Raises:
            ValueError: If `fetch_size` is less than 1.
            JiraApiError: If the response status code is not 200.
        """
        url = self._get_url(endpoint)

        if fetch_size < 1:
            raise ValueError('fetch_size must be >= 1')

        if fields_str:
            fields = fields_str.split(",")
        else:
            fields = None

        start_at = 0
        total_items = fetch_size

        fetched_issues = []

        while start_at < total_items:
            params = self._get_params(fetch_size, fields, jql, start_at)
            response = self._get_response(url, params)

            if response.status_code != 200:
                msg = f"Failed to fetch issues: {response.text}"
                raise JiraApiError(msg, response.status_code)

            data = response.json()
            total_items = data["total"]
            fetched_issues.extend(data["issues"])

            start_at += len(data["issues"])

        return fetched_issues

    def _get_url(self, endpoint: str):
        if endpoint is None or bool(endpoint) is False:
            raise ValueError('endpoint must not be empty')

        return urllib.parse.urljoin(self.connection.base_url, endpoint)

    def _get_params(self, fetch_size: int, fields, jql: str, start_at: int):
        params = {
            "startAt": start_at,
            "maxResults": fetch_size
        }

        if jql is not None:
            params["jql"] = jql

        if fields is not None:
            params["fields"] = fields

        return params

    def _get_response(self, url: str, params=None):
        if params is None:
            params = {}

        return requests.get(url,
                            headers=DEFAULT_HEADERS,
                            auth=(self.connection.username, self.connection.token),
                            params=params)