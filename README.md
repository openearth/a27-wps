# A27 Web Processing Service

A [PyWPS](https://pywps.org/) (Flask) implementation of the Web Processing Service for the A27 project. The frontend ([openearth/a27](https://github.com/openearth/a27)) calls these processes to load locations, groundwater, precipitation and tree data from a PostGIS database.

## Run locally

### Prerequisites

- [Conda](https://docs.conda.io/) (Miniconda/Miniforge)
- Access to the A27 PostGIS database

### 1. Create the environment

`environment.yml` contains all runtime dependencies (`pywps`, `flask`, `sqlalchemy`, `psycopg2`, `pandas`, `hydropandas`, …):

```bash
conda env create -f environment.yml
conda activate a27-wps
```

### 2. Configure the database connection

Copy the example configuration and fill in the PostGIS connection details. `configuration.txt` is gitignored, so do not commit credentials.

```bash
cp configuration.txt.example configuration.txt
```

```ini
[PostGIS]
HOST=<host>
USER=<user>
PASSWORD=<password>
DATABASE=<database>
PORT=5432
```

### 3. Start the service

```bash
python pywps.wsgi
```

The service runs at `http://localhost:5000`:

| URL | Description |
|---|---|
| `http://localhost:5000/` | Landing page listing all processes |
| `http://localhost:5000/wps` | WPS endpoint (GET and POST) |
| `http://localhost:5000/wps?service=WPS&request=GetCapabilities` | List of available processes |
| `http://localhost:5000/wps?service=WPS&request=DescribeProcess&version=1.0.0&identifier=<process>` | Inputs/outputs of one process |

Use `python pywps.wsgi -a` to listen on all network interfaces (`0.0.0.0`) instead of `127.0.0.1`. Service settings (server URL, logging) are in `pywps.cfg`.

Production: `https://a27.openearth.nl/wps`.

## Calling the processes

All processes run through `Execute` on `/wps` with WPS **version 1.0.0**. JSON inputs are passed as `ComplexData` with mime type `application/json`.

Add `RawDataOutput=<output identifier>` to receive plain JSON. Without it, PyWPS wraps the result in an XML `ExecuteResponse` document.

On error, processes return HTTP 200 with a JSON body `{"errMsg": "ERROR: ..."}`, so always check for `errMsg`.

### GET (key-value pairs)

Useful for quick tests in a browser or Postman:

```
http://localhost:5000/wps?service=WPS&request=Execute&version=1.0.0
  &identifier=<process identifier>
  &datainputs=<input identifier>=<JSON>
  &RawDataOutput=<output identifier>
```

URL-encode the JSON in `datainputs` when using curl or scripts (Postman and browsers encode it for you). Example:

```bash
curl -G "http://localhost:5000/wps" \
  --data-urlencode "service=WPS" \
  --data-urlencode "request=Execute" \
  --data-urlencode "version=1.0.0" \
  --data-urlencode "identifier=wps_get_boom_data" \
  --data-urlencode 'datainputs=boominfo={"boomnaams":["AW2Qu"]}' \
  --data-urlencode "RawDataOutput=boom_data"
```

### POST (XML Execute request)

This is how the frontend calls the service (`src/lib/wps/` in openearth/a27). Send the XML below to `/wps` with header `Content-Type: application/xml`:

```xml
<wps:Execute xmlns:wps="http://www.opengis.net/wps/1.0.0"
             xmlns:ows="http://www.opengis.net/ows/1.1"
             service="WPS" version="1.0.0">
  <ows:Identifier>wps_get_timeseries_data</ows:Identifier>
  <wps:DataInputs>
    <wps:Input>
      <ows:Identifier>pointinfo</ows:Identifier>
      <wps:Data>
        <wps:ComplexData mimeType="application/json">{"id": "1907", "x": 5.152291, "y": 52.071835}</wps:ComplexData>
      </wps:Data>
    </wps:Input>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/json">
      <ows:Identifier>timeseries_data</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
```

For processes without inputs, omit the `<wps:DataInputs>` block.

### Postman

- **GET**: create a `GET` request to `http://localhost:5000/wps` and add the query parameters `service=WPS`, `request=Execute`, `version=1.0.0`, `identifier`, `datainputs` and `RawDataOutput` from the examples below.
- **POST**: create a `POST` request to `http://localhost:5000/wps`, set **Body → raw → XML** (`Content-Type: application/xml`) and paste an Execute request like the one above, replacing the identifiers and the JSON input.

## Processes

| Identifier | Input | Output | Purpose |
|---|---|---|---|
| `wps_get_locations` | – | `locations` | All measurement locations (GeoJSON) |
| `wps_get_peilfilter_data` | `peilfilterinfo` | `peilfilter_data` | Groundwater timeseries + properties of one peilfilter |
| `wps_get_depth_info` | `peilfilter_ids` | `depth_info` | Peilbuis and filter depths |
| `wps_get_precipitation_data` | `locationinfo` | `precipitation_data` | KNMI precipitation for a coordinate |
| `wps_get_timeseries_data` | `pointinfo` | `timeseries_data` | Groundwater + matching precipitation for one peilfilter |
| `wps_get_bomen_locations` | – | `bomen_locations` | All monitored trees (GeoJSON) |
| `wps_get_boom_data` | `boominfo` | `boom_data` | Tree health graph data |
| `ultimate_question` | – | `answer` | Demo process (returns `42`) |

The GET examples below use the shared prefix `http://localhost:5000/wps?service=WPS&request=Execute&version=1.0.0`.

---

### `wps_get_locations`

**Retrieve A27 locations**

Returns all A27 measurement locations from the database as a GeoJSON FeatureCollection (WGS84). Each feature has the properties `locatie_id`, `locatienaam_master`, `peilfilter_ids` and `peilfilternaams` (comma-separated strings), `bron_id`, `dataleverancier` and `focus`.

- **Inputs:** none
- **Output:** `locations` (application/json)
- **Example:**
  `...&identifier=wps_get_locations&RawDataOutput=locations`

---

### `wps_get_peilfilter_data`

**Retrieve peilfilter timeseries data**

Returns the location properties and groundwater timeseries for one peilfilter. The date range is optional: use empty strings for `start_date` and/or `end_date` to request all available data or to bound only one side.

- **Inputs:**
  - `peilfilterinfo` (application/json):
    `{"peilfilterid": <int>, "start_date": "<datetime or \"\">", "end_date": "<datetime or \"\">"}`
- **Output:** `peilfilter_data` (application/json), `{"locationproperties": {...}, "timeseries": [{"datetime": "...", "value": ...}, ...]}`
- **Example:**
  `...&identifier=wps_get_peilfilter_data&datainputs=peilfilterinfo={"peilfilterid":1907,"start_date":"","end_date":""}&RawDataOutput=peilfilter_data`

---

### `wps_get_depth_info`

**Retrieve depth info for selected peilfilters**

Returns depth info (peilbuis top/bottom and filter top/bottom per peilfilter) for the given peilfilter IDs. Values are in m NAP (two decimal places).

- **Inputs:**
  - `peilfilter_ids` (application/json): a plain JSON array, `[<int>, <int>, ...]`
- **Output:** `depth_info` (application/json), e.g. `{"peilbuis_top": <m>, "peilbuis_bottom": <m>, "filters": [{"peilfilter_id": <int>, "filter_top": <m>, "filter_bottom": <m>}, ...]}`
- **Example:**
  `...&identifier=wps_get_depth_info&datainputs=peilfilter_ids=[2000,2001]&RawDataOutput=depth_info`

---

### `wps_get_precipitation_data`

**Retrieve precipitation timeseries for a location**

Returns daily precipitation (mm/day) from the nearest KNMI station for the given coordinates. Coordinates are in **WGS84 (EPSG:4326)**; the service converts them to RD New (EPSG:28992) internally. The date range is optional; empty strings use defaults or an unbounded range.

- **Inputs:**
  - `locationinfo` (application/json):
    `{"x": <lon>, "y": <lat>, "start_date": "<date or \"\">", "end_date": "<date or \"\">"}`
- **Output:** `precipitation_data` (application/json), e.g. `{"timeseries": [{"datetime": "...", "value": ..., "show": true}, ...]}`
- **Example:**
  `...&identifier=wps_get_precipitation_data&datainputs=locationinfo={"x":5.152291,"y":52.071835,"start_date":"2024-01-01","end_date":"2024-01-31"}&RawDataOutput=precipitation_data`

---

### `wps_get_timeseries_data`

**Retrieve groundwater + precipitation timeseries (matched start/end)**

Used by the frontend chart. It first retrieves the full groundwater timeseries of the peilfilter (`id`), then retrieves daily KNMI precipitation for the coordinates over the same date range.

- **Inputs:**
  - `pointinfo` (application/json):
    `{"id": "<peilfilter id>", "x": <lon>, "y": <lat>}` (WGS84)
- **Output:** `timeseries_data` (application/json), e.g.
  `{"precipitation": {"timeseries": [{"datetime": "...", "value": ..., "show": true}, ...]}, "groundwater": {"timeseries": [{"datetime": "...", "value": ...}, ...]}}`
- **Example:**
  `...&identifier=wps_get_timeseries_data&datainputs=pointinfo={"id":"1907","x":5.152291,"y":52.071835}&RawDataOutput=timeseries_data`

---

### `wps_get_bomen_locations`

**Retrieve monitored tree locations**

Returns all monitored trees as a GeoJSON FeatureCollection. Intended to be called once at FE startup to populate the tree map layer.

- **Inputs:** none
- **Output:** `bomen_locations` (application/json): a GeoJSON FeatureCollection where each feature has the properties `boom_id`, `boomcode`, `boomnaam`, `soort_group` and `exclude_from_group_stats`
- **Example:**
  `...&identifier=wps_get_bomen_locations&RawDataOutput=bomen_locations`

---

### `wps_get_boom_data`

**Retrieve tree health graph data**

Returns graph data for one clicked tree (or multiple selected trees in the future). The database function shapes the response directly: selected tree, y-axis metadata, the relevant group average line(s), and the requested tree timeseries.

- **Inputs:**
  - `boominfo` (application/json):
    `{"boomnaams": ["<boomcode or boomnaam>", …]}`
- **Output:** `boom_data` (application/json), e.g.:
  ```json
  {
    "selected_tree": "1FS",
    "y_axis": {
      "min": 0,
      "max": 8,
      "labels": ["Dood", "Bijna dood", "Slecht", "Matig-slecht", "Matig",
                 "Voldoende-matig", "Voldoende", "Voldoende-goed", "Goed"]
    },
    "group_averages": [
      {
        "group": "Beuken",
        "visible_by_default": true,
        "timeseries": [
          { "date": "2018-06-01T00:00:00", "health_value": 6.8 }
        ]
      }
    ],
    "trees": [
      {
        "tree": "1FS",
        "tree_name": "1FS",
        "group_that_belongs": "Beuken",
        "visible_by_default": true,
        "timeseries": [
          { "date": "2018-06-01T00:00:00", "health_value": 7, "health_label": "Voldoende-goed" }
        ]
      }
    ]
  }
  ```
- **Examples:**
  `...&identifier=wps_get_boom_data&datainputs=boominfo={"boomnaams":["1FS"]}&RawDataOutput=boom_data`
  `...&identifier=wps_get_boom_data&datainputs=boominfo={"boomnaams":["1FS","9FS","3Qu"]}&RawDataOutput=boom_data`

---

### `ultimate_question`

**Answer to the ultimate question**

Demo process that returns the answer to “What is the meaning of life?”. Handy to check that the service is running without needing the database.

- **Inputs:** none
- **Output:** `answer` (literal string), value `"42"`
- **Example:**
  `...&identifier=ultimate_question&RawDataOutput=answer`

## License of PyWPS

[MIT](https://en.wikipedia.org/wiki/MIT_License)