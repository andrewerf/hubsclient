from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class CloudAPI:
    def __init__(self, host: str, api_key: str):
        """ Hubs Cloud API client.

        :param host: The host of the room, e.g. "hubs.mozilla.com"
        :param api_key: The API key (must be a user token)
        """
        self.host = host
        self.transport = RequestsHTTPTransport(
            url=f"https://{host}/graphql",
            use_json=True,
            headers={"Content-type": "application/json", "Authorization": "Bearer " + api_key},
            verify=True,
            retries=3,
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
