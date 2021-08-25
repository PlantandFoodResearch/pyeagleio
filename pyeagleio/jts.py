"""
Example Document
"docType": "jts",
    "version": "1.0",
    "header": {
        "startTime": "<startTime>",
        "endTime": "<endTime>",
        "recordCount": 0,
        "columns": {
            {
                "0": {
                    "id": "<id>",
                    "name": "<name>",
                    "dataType": "<dataType>",
                    "format": "<format>",
                    "aggregate": "<aggregate>",
                    "baseTime": "<baseTime>",
                    "interval": "<interval>"
                },
                "1": {},
                "2": {}
            }
        }
    },
    "data": [
        {
            "ts": "<ts>",
            "f": {
                "0": {"v": 10.4, "q": 100, "a": "site maintenance"},
                "1": {"v": 55},
                "2": {"a": "sensor recalibrated"}
            }
        },
        {
            "ts": "<ts>",
            "f": {"0": {"v": 12, "q": 100}, "1": {"v": 55, "q": 100}}
        }
    ]
}
"""
import datetime
from typing import List, Set, Dict


class TimeSeries(dict):
    """Add helpers to massage data into and out of Json Time Series (https://docs.eagle.io/en/latest/reference/historic\
    /jts.html?highlight=JTS)"""

    def __init__(self):
        # Setup base structure
        super(TimeSeries, self).__init__(
            {
                "docType": "jts",
                "version": "1.0",
                "header": {
                    # Leave these out by default
                    # "startTime": None,
                    # "endTime": None,
                    # "recordCount": 0,
                    "columns": {}
                },
                "data": [],
            }
        )
        self._jtscolumns: Set["Column"] = set()

    @property
    def columns(self) -> Dict:
        return self["header"]["columns"]

    @property
    def columns_jts(self):
        return self._jtscolumns

    def add_jtscolumn(self, column: "Column"):
        # index is == current length (starts at 0)
        index = len(self._jtscolumns)
        self._jtscolumns.add(column)
        # update dict
        self.columns.update({index: column.dict})
        column._jts = self
        column._index = index

    @property
    def data(self) -> List:
        return self["data"]

    def update_header(self):
        """Ensure start"""
        # Todo ensure self._jtscolumns matched columns
        pass


class Column:
    """Helper class to slot data into / out of a TimeSeries"""

    def __init__(
        self,
        id,
        name,
        data_type,
        units,
        format="0.##",
        aggregate=None,
        base_time=None,
        interval=None,
    ):
        self._dict = dict(
            {
                "id": id,
                "name": name,
                "dataType": data_type,
                "format": format,
                "units": units,
                "aggregate": aggregate or "NONE",
                # Not used for now
                # "baseTime": "<baseTime>",
                # "interval": "<interval>"
            }
        )
        self._jts: TimeSeries = None
        self._index = None

    @property
    def dict(self):
        return self._dict

    @property
    def jts(self):
        return self._jts

    @jts.setter
    def jts(self, jts: TimeSeries):
        raise NotImplementedError("Add column to TimeSeries instead.")

    @property
    def data(self):
        # Todo: fix this up, it is ugly. Is it even needed?
        raise NotImplementedError()
        if not self._jts:
            ValueError("Must first associate with a TimeSeries obj")
        return self._jts.data

    def add_data_point(self, dp: "DataPoint"):
        # Todo: this needs serious cleaning
        for idx, entry in enumerate(self._jts.data):
            if entry["ts"] == dp.time:
                # update this entry
                f: dict = entry["f"]
                f.update({str(self._index): {"v": dp.value}})
                self._jts.data[idx] = entry
                return
        entry = {"ts": dp.time, "f": {str(self._index): {"v": dp.value}}}
        self._jts.data.append(entry)


class DataPoint:
    def __init__(self, value, timestamp=None, quality=0, annotation=None):
        if not timestamp:
            timestamp = (
                datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
            )
        self.time = timestamp
        self.value = value
        self.quality = quality
        self.annotation = annotation
