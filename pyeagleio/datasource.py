import time
import typing
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

    def __init__(self, node_id: str, name: str, fmt: str, dt: str, units: str):
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
        self.units = units
        self._cached_node: Optional[dict] = None

    @classmethod
    def from_node(cls, node_json: dict) -> "Parameter":
        """Init from a Node JSON object from the API"""
        node_id = node_json.get("_id", None)
        name = node_json.get("name", None)
        fmt = node_json.get("format", None)
        units = node_json.get("units", "")
        if "NumberPoint" in node_json.get("_class"):
            dt = Parameter.DT_NUMBER
        else:
            dt = Parameter.DT_UNKNOWN
        obj = cls(node_id, name, fmt, dt, units)
        obj._cached_node = node_json
        return obj

    def __str__(self):
        return f"{self.name}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, str):
            return self.__str__() == other
        return False


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
            params={"filter": f"parentId($eq:{self._nodeid})"},
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

    def create_new_param(
        self, name, units="", dataType=Parameter.DT_NUMBER, format=None
    ):
        """Creates a new parameter for this data source"""
        resp = self._client.post(
            path=f"api/v1/nodes/{self.node}/historic",
            json={
                "docType": "jts",
                "version": "1.0",
                "header": {
                    "columns": {
                        "0": {
                            "name": name,
                            "dataType": dataType,
                            "units": units,
                            "format": format,
                        }
                    }
                },
                "data": [],
            },
        )
        # We need to wait for Eagle to update the node...
        time.sleep(0.5)
        self._parameters: List[Parameter] = []
        self._get_node_online()
        if name not in self.params:
            raise ValueError("Failed to create parameter")

    def send_value(
        self,
        value: typing.Optional[typing.Union[str, float]],
        name,
        quality=None,
        annotation=None,
        ts=None,
    ):
        """Send a value directly to a column of given name.

        If timestamp(ts) is None, then API will use request ts.
        """
        try:
            param = next(p for p in self.params if p.name == name)
        except StopIteration as _:
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
