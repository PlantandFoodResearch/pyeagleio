from pyeagleio import DataSource
from pyeagleio.jts import TimeSeries, Column, DataPoint


def test_basic(httpsclient):
    _ = DataSource("@test_api", client=httpsclient)


def test_upload(httpsclient, example_jts):
    param = DataSource("@test_api", client=httpsclient)
    param.send(example_jts)


def test_upload_JTS(httpsclient, example_jts):
    param = DataSource("@test_api", client=httpsclient)
    jts = TimeSeries()
    column = Column(id="", name="Other Thingi", data_type="NUMBER", units="°C")
    jts.add_jtscolumn(column)
    dp = DataPoint(10.5)
    column.add_data_point(dp)
    param.send(jts)
