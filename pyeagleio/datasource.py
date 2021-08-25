from typing import Union

import requests
from pyeagleio.https import HTTPSClient


class DataSource:
    def __init__(self, node_id_or_name: str, client: Union[HTTPSClient]):
        """
        node_id_or_name: Either random node ID or custom name, including '@'.
        """
        if "/" in node_id_or_name or "\\" in node_id_or_name:
            raise ValueError("Invalid Node ID or Name")
        self.node = node_id_or_name
        self._client = client
        self._session: requests.Session = self._client.session
        self._check_node()

    def _check_node(self):
        """Raises if API enpoint seems non-functional"""
        resp = self._session.get(url=f"{self._client.url}/api/v1/nodes/{self.node}")
        if resp.status_code != 200:
            raise ValueError(f"API Check failed ({resp.status_code}): {resp.content}")
        if "source.data" not in resp.json()["_class"]:
            raise ValueError(f"Invalid node type: {resp.json()['_class']}")

    def send(self, jts_content):
        """Send JSON Time Series content to data source"""
        # Todo: add compression if large content
        resp = self._session.put(
            url=f"{self._client.url}/api/v1/nodes/{self.node}/historic",
            json=jts_content,
        )
        if resp.status_code != 200 and resp.status_code != 202:
            raise ValueError(
                f"Get historic data failed ({resp.status_code}): {resp.content}"
            )
        _ = resp.json()
