import unittest
import json
from unittest.mock import patch, Mock
from jira_api_fetcher import JiraConnection, JiraApiFetcher, JiraApiError

ENDPOINT = "/some/endpoint"
BASE_URL = "https://your-jira-instance.com"
EXPECTED_URL = BASE_URL + ENDPOINT
CONNECTION = JiraConnection(BASE_URL, "your-username", "your-token")
DEFAULT_HEADER = {"Content-Type": "application/json"}


class TestJiraApiFetcher(unittest.TestCase):

    # Fetch Issues

    @patch('requests.get')
    def test_fetch_issues_success(self, mock_get):
        # Arrange
        response_data = [{"total": 2, "issues": [{"id": 1}]}, {"total": 2, "issues": [{"id": 2}]}]
        expected_response = [{"id": 1}, {"id": 2}]
        fields_str = 'a,b'
        jql = 'project="Foo" and created >= -5d'

        self._test_fetch_issues(mock_get, expected_response, fields_str, jql, response_data)

    @patch('requests.get')
    def test_fetch_issues_success_no_jql(self, mock_get):
        # Arrange
        response_data = [{"total": 1, "issues": [{"id": 1}]}]
        expected_response = [{"id": 1}]
        fields_str = 'a,b'

        self._test_fetch_issues(mock_get, expected_response, fields_str, None, response_data)

    @patch('requests.get')
    def test_fetch_issues_success_no_fields(self, mock_get):
        # Arrange
        response_data = [{"total": 0, "issues": []}]
        expected_response = []
        jql = 'project="Foo" and created >= -5d'

        self._test_fetch_issues(mock_get, expected_response, None, jql, response_data)

    def _test_fetch_issues(self, mock_get, expected_response, fields_str, jql, response_data):
        # Under Test
        under_test = JiraApiFetcher(CONNECTION)

        # Mocking the response for a successful request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = response_data
        mock_get.return_value = mock_response

        # Act
        result = under_test.fetch_issues(endpoint=ENDPOINT, jql=jql, fields_str=fields_str, fetch_size=1)

        # Assert
        self.assertEqual(result, expected_response)

        # Method should be called at least once
        call_count = max(1, len(expected_response))

        self.assertEqual(mock_get.call_count, call_count)

    @patch('requests.get')
    def test_fetch_issues_error(self, mock_get):
        # Under Test
        under_test = JiraApiFetcher(CONNECTION)

        # Mocking the response for a successful request
        mock_response = Mock()
        mock_response.status_code = 500

        # Act
        with self.assertRaises(JiraApiError):
            under_test.fetch_issues(ENDPOINT)

        self.assertEqual(mock_get.call_count, 1)

    def test_fetch_issues_value_error_no_endpoint_str(self):
        under_test = JiraApiFetcher(CONNECTION)

        with self.assertRaises(ValueError):
            under_test.fetch_issues("")

    def test_fetch_issues_value_error_invalid_fetch_size(self):
        under_test = JiraApiFetcher(CONNECTION)

        with self.assertRaises(ValueError):
            under_test.fetch_issues(ENDPOINT, fetch_size=-1)

    # Fetch Array

    @patch('requests.get')
    def test_fetch_array_success(self, mock_get):
        # Arrange
        expected_response = [{"id": 1, "name": "Test"}]

        # Under Test
        under_test = JiraApiFetcher(CONNECTION)

        # Mocking the response for a successful request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        # Act
        result = under_test.fetch_array(ENDPOINT)

        # Assert
        self.assertEqual(result, expected_response)

        self.assert_response_get_called(EXPECTED_URL, mock_get)

    @patch('requests.get')
    def test_fetch_array_throws_error(self, mock_get):
        # Under Test
        under_test = JiraApiFetcher(CONNECTION)

        # Mocking the response for an erroneous request
        mock_response = Mock()
        status_code = 500
        mock_response.status_code = status_code
        mock_response.text = 'error message'
        mock_get.return_value = mock_response

        # Act
        with self.assertRaises(JiraApiError) as context:
            under_test.fetch_array(ENDPOINT)

        expected_msg = f"Failed to fetch data as array: {mock_response.text} (Status Code: {status_code})"
        self.assertEqual(str(context.exception), expected_msg)

        self.assert_response_get_called(EXPECTED_URL, mock_get)

    def assert_response_get_called(self, expected_url, mock_get):
        mock_get.assert_called_once_with(
            expected_url,
            headers=DEFAULT_HEADER,
            auth=(CONNECTION.username, CONNECTION.token),
            params={}
        )

    @patch('requests.get')
    def test_fetch_paginated(self, mock_get):
        # Arrange
        response_1 = {"startAt": 0, "total": 2, "isLast": False, "maxResults": 1, "values": [{"id": 1}]}
        response_2 = {"startAt": 0, "total": 2, "isLast": True, "maxResults": 1, "values": [{"id": 2}]}
        responses = [response_1, response_2]
        expected_result = [{"id": 1}, {"id": 2}]

        # Under Test
        under_test = JiraApiFetcher(CONNECTION)

        # Mocking the response for a successful request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = responses
        mock_get.return_value = mock_response

        # Act
        result = under_test.fetch_paginated(endpoint=ENDPOINT, fetch_size=1, params_json='{"foo": 2}')

        # Assert
        self.assertEqual(result, expected_result)

        # Method should be called at least once
        call_count = max(1, len(expected_result))

        self.assertEqual(mock_get.call_count, call_count)

    @patch('requests.get')
    def test_fetch_paginated_error(self, mock_get):
        # Under Test
        under_test = JiraApiFetcher(CONNECTION)

        # Mocking the response for a successful request
        mock_response = Mock()
        mock_response.status_code = 500

        # Act
        with self.assertRaises(JiraApiError):
            under_test.fetch_paginated(ENDPOINT)

        self.assertEqual(mock_get.call_count, 1)

    def test_fetch_paginated_value_error_invalid_fetch_size(self):
        under_test = JiraApiFetcher(CONNECTION)

        with self.assertRaises(ValueError):
            under_test.fetch_paginated(ENDPOINT, fetch_size=-1)

    def test_fetch_paginated_value_error_invalid_params(self):
        under_test = JiraApiFetcher(CONNECTION)

        with self.assertRaises(json.JSONDecodeError):
            under_test.fetch_paginated(ENDPOINT, params_json='{')

    def test_fetch_paginated_value_error_no_endpoint_str(self):
        under_test = JiraApiFetcher(CONNECTION)

        with self.assertRaises(ValueError):
            under_test.fetch_paginated("")
