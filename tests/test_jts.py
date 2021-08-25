from pyeagleio.jts import TimeSeries, Column, DataPoint


def test_basic():
    jts = TimeSeries()
    print(jts.columns)


def test_column():
    jts = TimeSeries()
    column = Column(
        id="60f8a0ef6dfce40ebe570a83",
        name="Temperature",
        data_type="NUMBER",
        units="°C",
    )
    jts.add_jtscolumn(column)
    print(jts)


def test_datapoint():
    jts = TimeSeries()
    column = Column(
        id="60f8a0ef6dfce40ebe570a83",
        name="Temperature",
        data_type="NUMBER",
        units="°C",
    )
    jts.add_jtscolumn(column)
    dp = DataPoint(10.5)
    column.add_data_point(dp)
    print(jts.data)
