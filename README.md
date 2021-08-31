# pyeagleio

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
