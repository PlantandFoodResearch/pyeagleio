# pyeagleio

[![Continuous Integration](https://github.com/pfrnz/pyeagleio/actions/workflows/ci.yml/badge.svg)](https://github.com/pfrnz/pyeagleio/actions/workflows/ci.yml) [![Python 3.6.2](https://img.shields.io/badge/python-3.6.2-blue.svg)](https://www.python.org/downloads/release/python-362/) [![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

Python library to interact with https://eagle.io/


## Description

Basic client library for uploading data to the Eagle.io platform. Currently supports:
* HTTPS API

## Example

```python
apikey = os.environ.get("API_KEY")
if not apikey:
    raise ValueError("No API Key")
nodeid = os.environ.get("NODEID_EAGLE_SOURCE")
if not nodeid:
    raise ValueError("No NODEID_EAGLE_SOURCE")
api = HTTPSClient(apikey)
ds = DataSource(nodeid, client=api)

# Send some data
jts = TimeSeries()
column = Column(
    id="", name="Temp", data_type="NUMBER", units="K"
)
jts.add_jtscolumn(column)
dp = DataPoint(value="5.0")
column.add_data_point(dp)
ds.send(jts)
```

## Micropython Support
This library is somewhat compatible with Micropython **after** being converted.
Use [pytomicropy](https://github.com/pfrnz/pytomicropy) to perform the conversion. E.g.
```bash
python -m pip install https://github.com/pfrnz/pytomicropy/archive/main.zip
pytomicropy --help
pytomicropy --input pyeagleio --output /path/to/pycom/project/libs/pyeagleio
```

## Developers

```python
python -m venv .venv
.venv/Scripts/activate
pip install -e .[tests,dev]
```

## Note

This project has been set up using PyScaffold 4.0.2. For details and usage
information on PyScaffold see https://pyscaffold.org/.
