import logging
from pyeagleio import MICROPYTHON

if MICROPYTHON:
    import urequests as requests
else:
    import requests

log = logging.getLogger(__name__)


class HTTPSClientError(Exception):
    pass


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
        self._base_url = f"https://{host}:{HTTPSClient._PORT}"
        self._check_connection()

    def _check_connection(self):
        resp = self.get("api/v1/owners/account")
        if resp.status_code != 200:
            raise ValueError(f"API Check failed ({resp.status_code}): {resp.content}")

    @property
    def url(self) -> str:
        return self._base_url

    def _call_requests(self, method, path, **kwargs):
        """Compatability layer for CPython / Micropython to avoid using a Session"""
        headers = kwargs.get("headers", {})
        headers.update({"X-Api-Key": self._api_key})
        kwargs.update({"headers": headers})
        url = self.path_to_url(path)
        params = kwargs.get("params", None)
        if params:
            from urllib.parse import urlencode, quote

            url += "?" + urlencode(params)
            # Does not properly encode "(". Quote also seems to give the wrong result
            kwargs.pop("params")  # Remove from kwargs
        resp = requests.request(method, url, **kwargs)
        if resp.status_code >= 300:
            raise HTTPSClientError(
                f"API request error status: {resp.status_code}, msg: {resp.text}"
            )
        return resp

    def path_to_url(self, path) -> str:
        return f"{self._base_url}/{path.rstrip('/')}"

    def get(self, path, **kwargs):
        return self._call_requests("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._call_requests("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._call_requests("PUT", path, **kwargs)
