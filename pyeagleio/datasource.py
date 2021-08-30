from typing import Union, Optional, List
from pyeagleio.https import HTTPSClient
import logging

log = logging.getLogger(__name__)


class Parameter(object):
    DT_NUMBER = "VALUE"
    DT_TEXT = "TEXT"
    DT_TIME = "TIME"
    DT_COORDINATES = "COORDINATES"
    DT_UNKNOWN = None

    def __init__(self, node_id: str, name: str, fmt: str, dt: str):
        self.id = node_id
        self.name = name
        self.format = fmt
        if dt not in [
            Parameter.DT_NUMBER,
            Parameter.DT_TEXT,
            Parameter.DT_TIME,
            Parameter.DT_COORDINATES,
        ]:
            # See https://docs.eagle.io/en/latest/reference/historic/jts.html?highlight=dataType#json-time-series
            raise ValueError("invalid Eagle.IO dataType given")
        self.dt = dt
        self._cached_node: Optional[dict] = None

    @classmethod
    def from_node(cls, node_json: dict) -> "Parameter":
        """Init from a Node JSON object from the API"""
        node_id = node_json.get("_id", None)
        name = node_json.get("name", None)
        fmt = node_json.get("format", None)
        if "NumberPoint" in node_json.get("_class"):
            dt = Parameter.DT_NUMBER
        else:
            dt = Parameter.DT_UNKNOWN
        obj = cls(node_id, name, fmt, dt)
        obj._cached_node = node_json
        return obj


class DataSource:
    def __init__(self, node_id_or_name: str, client: Union[HTTPSClient]):
        """
        node_id_or_name: Either random node ID or custom name, including '@'.
        """
        if "/" in node_id_or_name or "\\" in node_id_or_name:
            raise ValueError("Invalid Node ID or Name")
        self.node = node_id_or_name
        self._client = client
        self._nodeid: Optional[str] = None
        self._check_node()
        self._parameters: List[Parameter] = []
        self._get_node_online()

    def _get_node_online(self):
        """Gets column information from the API and fills out class instance"""
        resp = self._client.get(
            path=f"api/v1/nodes",
            params={"filter": "parentId($eq:612c56d2818fe30f7b6533c9)"},
        )
        resp = resp.json()
        for child in resp:
            self._parameters.append(Parameter.from_node(child))

    def _check_node(self):
        """Raises if API enpoint seems non-functional"""
        resp = self._client.get(path=f"api/v1/nodes/{self.node}")
        if "source.data" not in resp.json()["_class"]:
            raise ValueError(f"Invalid node type: {resp.json()['_class']}")
        self._nodeid = resp.json().get("_id", None)

    def send(self, jts_content):
        """Send JSON Time Series content to data source.json

        It is often easier to use 'send_value' instead once the parameters have been defined
        """
        # Todo: add compression if large content
        _ = self._client.put(
            path=f"api/v1/nodes/{self.node}/historic",
            json=jts_content,
        )

    def send_value(self, value, name, quality=None, annotation=None, ts=None):
        """Send a value directly to a column of given name.

        If timestamp(ts) is None, then API will use request ts.
        """
        param = next((p for p in self.params if p.name == name), None)
        if not param:
            raise ValueError(
                "When sending single value, parameter name must match existing parameters"
            )
        _ = self._client.put(
            path=f"api/v1/nodes/{param.id}/historic/now",
            json={
                "value": value,
                "quality": quality,
                "annotation": annotation,
                "timestamp": ts,
            },
        )

    @property
    def params(self) -> List[Parameter]:
        return self._parameters
