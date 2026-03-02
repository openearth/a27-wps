# A27 Web Processing Service

A PyWPS implementation of the Web Processing Service for the A27 project.

## Processes

The service exposes the following WPS 2.0 processes:

### `wps_get_locations`

**Retrieve A27 locations**

Returns all A27 locations from the database as GeoJSON.

- **Inputs:** none  
- **Output:** `locations` (application/json)  
- **Example:**  
  `GET .../wps?service=WPS&request=Execute&version=1.0.0&identifier=wps_get_locations`

---

### `wps_get_peilfilter_data`

**Retrieve peilfilter timeseries data**

Returns timeseries data for a selected peilfilter. Date range is optional; use empty strings for `start_date` and/or `end_date` to request all available data or only bound one side.

- **Inputs:**  
  - `peilfilterinfo` (application/json):  
    `{"peilfilterid": <int>, "start_date": "<datetime or \"\">", "end_date": "<datetime or \"\">"}`  
- **Output:** `peilfilter_data` (application/json)  
- **Example:**  
  `GET .../wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_peilfilter_data&datainputs=peilfilterinfo={"peilfilterid":436, "start_date":"2013-06-01 00:00:00","end_date":"2013-12-31 23:59:59"}`

---

### `wps_get_depth_info`

**Retrieve depth info for selected peilfilters**

Returns depth info (peilbuis top/bottom and filter top/bottom per peilfilter) for the given peilfilter IDs. Values are in m NAP (two decimal places).

- **Inputs:**  
  - `peilfilter_ids` (application/json):  
    `{"peilfilter_ids": [<int>, <int>, ...]}`  
- **Output:** `depth_info` (application/json), e.g. `{"peilbuis_top": <m>, "peilbuis_bottom": <m>, "filters": [{"peilfilter_id": <int>, "filter_top": <m>, "filter_bottom": <m>}, ...]}`  
- **Example:**  
  `GET .../wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_depth_info&datainputs=peilfilter_ids={"peilfilter_ids":[2000,2001]}`

---

### `wps_get_precipitation_data`

**Retrieve precipitation timeseries for a location**

Returns daily precipitation (mm/day) from the nearest KNMI station for the given coordinates. Coordinates are in **WGS84 (EPSG:4326)**; the service uses RD New (EPSG:28992) internally. Date range is optional; empty strings use defaults or unbounded range.

- **Inputs:**  
  - `locationinfo` (application/json):  
    `{"x": <lon>, "y": <lat>, "start_date": "<date or \"\">", "end_date": "<date or \"\">"}`  
- **Output:** `precipitation_data` (application/json), e.g. `{"timeseries": [{"datetime": "...", "value": ...}, ...]}`  
- **Example:**  
  `GET .../wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_precipitation_data&datainputs=locationinfo={"x":5.207047,"y":52.066449,"start_date":"","end_date":""}`

---

### `ultimate_question`

**Answer to the ultimate question**

Demo process that returns the answer to “What is the meaning of life?”.

- **Inputs:** none  
- **Output:** `answer` (literal string), value `"42"`  
- **Example:**  
  `GET .../wps?service=wps&request=Execute&version=2.0.0&Identifier=ultimate_question`

---

## Install command

conda create --name env_name -c conda-forge --file requirements.txt

## Run service commands

conda activate env_name

python pywpws.wsgi

## License of PyWPS

[MIT](https://en.wikipedia.org/wiki/MIT_License)