from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class CloudAPI:
    def __init__(self, host: str, app_token: str = None, user_token: str = None):
        """Hubs Cloud API client.

        :param host: The host of the room, e.g. "hubs.mozilla.com"
        :param app_token: The API key app token (from https://<host>/token)
        :param user_token: The API key user token (from https://<host>/token)
        """
        self.host = host
        self.gqlapp_transport = None
        self.gqlapp_client = None
        self.app_token = app_token
        if app_token is not None:
            self._gql_app_connect()
        self.gqluser_transport = None
        self.gqluser_client = None
        self.user_token = user_token
        if user_token is not None:
            self._gql_user_connect()

    def _gql_app_connect(self, app_token: str = None):
        self.app_token = app_token or self.app_token
        self.gqlapp_transport = RequestsHTTPTransport(
            url=f"https://{self.host}/api/v2_alpha/graphiql",
            use_json=True,
            headers={
                "Content-type": "application/json",
                "Authorization": "Bearer " + app_token,
            },
            verify=True,
            retries=3,
        )
        self.gqlapp_client = Client(
            transport=self.gqlapp_transport, fetch_schema_from_transport=True
        )

    def _gql_user_connect(self, user_token: str = None):
        self.user_token = user_token or self.user_token
        self.gqluser_transport = RequestsHTTPTransport(
            url=f"https://{self.host}/api/v2_alpha/graphiql",
            use_json=True,
            headers={
                "Content-type": "application/json",
                "Authorization": "Bearer " + user_token,
            },
            verify=True,
            retries=3,
        )
        self.gqluser_client = Client(
            transport=self.gqluser_transport, fetch_schema_from_transport=True
        )
