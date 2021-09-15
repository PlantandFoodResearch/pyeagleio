import pytest

from datetime import datetime
from pyeagleio.datasource import DataSource
from pyeagleio.jts import TimeSeries, Column, DataPoint


def test_basic(httpsclient):
    _ = DataSource("@test-ci-source", client=httpsclient)


def test_upload(httpsclient, example_jts):
    param = DataSource("@test-ci-source", client=httpsclient)
    param.send(example_jts)


def test_upload_single_value(httpsclient, example_jts):
    ds = DataSource("@test-ci-source", client=httpsclient)
    ds.send_value(value=25.1, name="Temperature")
    assert len(ds.params) == 3
    for param in ds.params:
        if param.name == "Temperature":
            assert param.units == "°C"
    with pytest.raises(ValueError) as exc:
        ds.send_value(value=25.1, name="BadParam")


def test_upload_single_annotation(httpsclient, example_jts):
    ds = DataSource("@test-ci-source", client=httpsclient)
    ts = datetime.fromisoformat("2021-09-10T12:00:00").astimezone().replace(microsecond=0).isoformat()
    ds.send_value(value=None, name="Temperature", annotation="Testing", ts=ts)
    pass


def test_upload_JTS(httpsclient, example_jts):
    param = DataSource("@test-ci-source", client=httpsclient)
    jts = TimeSeries()
    column = Column(id="", name="Other Thingi", data_type="NUMBER", units="°C")
    jts.add_jtscolumn(column)
    dp = DataPoint(10.5)
    column.add_data_point(dp)
    param.send(jts)
