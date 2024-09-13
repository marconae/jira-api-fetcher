class JiraConnection:
    def __init__(self, base_url, username, token):
        self.base_url = base_url
        self.username = username
        self.token = token

    def __repr__(self):
        return f"JiraConnection(base_url={self.base_url}, username={self.username})"

class JiraApiError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        return f"{self.args[0]} (Status Code: {self.status_code})"