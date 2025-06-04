class InvalidAPIKeyError(Exception):
    def __init__(self, url: str):
        self.url = url
        super().__init__(f'Invalid API key, the service rejected access to {self.url}')


class InvalidCookiesError(Exception):
    def __init__(self, url: str):
        self.url = url
        super().__init__(f'Invalid cookies, the service rejected access to {self.url}')
