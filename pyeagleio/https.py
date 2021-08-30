import requests
import logging

log = logging.getLogger(__name__)


class HTTPSClient:
    _PORT = 443

    def __init__(
        self,
        api_key: str,
        host: str = "api.eagle.io",
    ):
        if not api_key:
            raise ValueError(
                """You must supply a valid Eagle API Key. Visit https://docs.eagle.io/en/latest/topics/\
            account_settings/security/index.html#management-security-apikeys for more information"""
            )
        self._api_key = api_key
        self._host = host
        self._session = requests.Session()
        self._session.headers.update({"X-Api-Key": self._api_key})
        self._base_url = f"https://{host}:{HTTPSClient._PORT}"
        self._check_connection()

    def _check_connection(self):
        resp = self.session.get(url=f"{self._base_url}/api/v1/owners/account")
        if resp.status_code != 200:
            raise ValueError(f"API Check failed ({resp.status_code}): {resp.content}")

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def url(self) -> str:
        return self._base_url
