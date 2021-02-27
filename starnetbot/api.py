from starnetbot.wrappers import request


class StarnetAPI:
    def __init__(self):
        self._refresh_token = None

    def user(self, username: str, password: str):
        response = self.post('/auth/jwt/create/', data={'username': username, 'password': password}).json()
        self._refresh_token = response['refresh']

    def get_access_token(self):
        if self._refresh_token:
            response = self.post('/auth/jwt/refresh/', data={'refresh': self._refresh_token}).json()
            return response['access']

        raise ValueError(
            "There are no refresh token cached. "
            "You need to call `.user()` before trying to authenticate with token."
        )

    def post(self, url: str, data: dict = None, auth: bool = False):
        url = 'http://localhost/api/v1/' + url.lstrip('/')
        headers = {'Authorization': f'JWT {self.get_access_token()}'} if auth else None
        return request('post', url, data=data, headers=headers)


starnet_api = StarnetAPI()
