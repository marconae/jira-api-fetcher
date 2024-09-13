import unittest
import json

from jira_api_fetcher import JiraConnection, JiraApiFetcher

@unittest.skip("Skipping Playground")
class PlaygroundTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection, self.project = PlaygroundTest._get_environment()

    # Playground: fetch issues
    def test_fetch_issues(self):
        fetcher = JiraApiFetcher(self.connection)

        endpoint = 'rest/api/2/search'
        jql = f'project = "{self.project}" AND created >= -5d ORDER BY created DESC'
        fields = 'resolution,resolutiondate,updated,parent'

        data = fetcher.fetch_issues(endpoint=endpoint, fields_str=fields, jql=jql, fetch_size=10)

        print(data)

    # Playground: fetch resolution states
    def test_fetch_resolution_status(self):
        fetcher = JiraApiFetcher(self.connection)

        data = fetcher.fetch_array('rest/api/3/resolution')

        print(data)

    def test_fetch_issue_status(self):
        fetcher = JiraApiFetcher(self.connection)

        data = fetcher.fetch_paginated('rest/api/3/statuses/search')

        print(data)

    @staticmethod
    def _get_environment():
        with open('../http-requests/http-client.private.env.json') as env_data_file:
            env_data = json.load(env_data_file)["dev"]

        connection = JiraConnection(env_data["jiraServer"],
                                    env_data["user"],
                                    env_data["token"])
        return connection, env_data["jiraProject"]

