# -*- coding: utf-8 -*-
#  Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2025 Deltares for Project A27.
#   Main contributors:
#     Ioanna Micha (ioanna.micha@deltares.nl)
#     Gerrit Hendriksen (Gerrit Hendriksen@deltares.nl)
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#   --------------------------------------------------------------------
#
# This tool is part of <a href="http://www.OpenEarth.eu">OpenEarthTools</a>.
# OpenEarthTools is an online collaboration to share and manage data and
# programming tools in an open source, version controlled environment.

import json
import logging
from datetime import datetime

from pywps import Format
from pywps.app import Process
from pywps.app.Common import Metadata
from pywps.inout.inputs import ComplexInput
from pywps.inout.outputs import ComplexOutput

from .utils import get_data, get_precipitation_data

logger = logging.getLogger("PYWPS")


def _parse_gw_datetime(dt_str):
    """
    Parse groundwater datetimes returned by `gws.get_peilfilter_data_json`.
    Typically: "YYYY-MM-DD HH:MM:SS" but we also accept "YYYY-MM-DDTHH:MM:SS".
    """
    if not dt_str:
        return None
    # fromisoformat does not accept space instead of "T" reliably in all cases.
    return datetime.fromisoformat(str(dt_str).replace(" ", "T"))


class WpsGetTimeseriesData(Process):
    """
    Combined response:
      {
        "precipitation": {"timeseries": [{"datetime": "...", "value": ...}, ...]},
        "groundwater": {"timeseries": [{"datetime": "...", "value": ...}, ...]}
      }

    KNMI precipitation start/end are matched to groundwater min/max dates (daily).
    """

    def __init__(self):
        inputs = [
            ComplexInput(
                "pointinfo",
                "point info as JSON: {'id', 'x', 'y'}",
                supported_formats=[Format("application/json")],
            ),
        ]

        outputs = [
            ComplexOutput(
                identifier="timeseries_data",
                title="Precipitation + groundwater (matched start/end)",
                supported_formats=[Format("application/json")],
            )
        ]

        super(WpsGetTimeseriesData, self).__init__(
            self._handler,
            identifier="wps_get_timeseries_data",
            version="1.0.0",
            title="Retrieve precipitation and groundwater timeseries (matched start/end)",
            abstract="Calls peilfilter first to derive start/end dates; then calls KNMI for precipitation and returns a common combined JSON response.",
            profile="",
            metadata=[
                Metadata("WpsGetTimeseriesData"),
                Metadata("wps_get_timeseries_data"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False,
        )

    def _handler(self, request, response):
        #try:
        # Inputs
        point_info = request.inputs["point_info"][0].data
        point_info_json = json.loads(point_info)

       
        peilfilter_id = point_info_json["peilfilterid"]
       

        x = point_info_json["x"]
        y = point_info_json["y"]
        print("x", x)
        print("y", y)
        print("peilfilter_id", peilfilter_id)
        # 1) Groundwater first (so we can derive time bounds)
        gw_raw = get_data(peilfilter_id, start_date= '', end_date= '')
        print("gw_raw", gw_raw)
        gw_json = json.loads(gw_raw)
        print("gw_json", gw_json)
      

        # gw_ts = gw_json.get("timeseries", []) or []

        # gw_dt_list = []
        # for item in gw_ts:
        #     dt = _parse_gw_datetime(item.get("datetime"))
        #     if dt is not None:
        #         gw_dt_list.append(dt)

        # if not gw_dt_list:
        #     raise ValueError("No groundwater timeseries returned for the provided period.")

        # gw_start_dt = min(gw_dt_list)
        # gw_end_dt = max(gw_dt_list)
        # gw_start_date = gw_start_dt.date()
        # gw_end_date = gw_end_dt.date()

        # # 2) KNMI precipitation second (matched to groundwater dates)
        # knmi_start = gw_start_date.isoformat()  # YYYY-MM-DD
        # knmi_end = gw_end_date.isoformat()  # YYYY-MM-DD

        # prec_raw = get_precipitation_data(x, y, knmi_start, knmi_end)
        # prec_json = json.loads(prec_raw)
        # prec_ts = prec_json.get("timeseries", []) or []

        # # Clip both series to keep the "start/end match" behavior.
        # prec_ts_clipped = []
        # for item in prec_ts:
        #     dt = datetime.fromisoformat(item["datetime"])
        #     if gw_start_date <= dt.date() <= gw_end_date:
        #         prec_ts_clipped.append(
        #             {
        #                 "datetime": item["datetime"],
        #                 "value": item.get("value"),
        #             }
        #         )

        # gw_ts_clipped = []
        # for item in gw_ts:
        #     dt = _parse_gw_datetime(item.get("datetime"))
        #     if dt is not None and gw_start_dt <= dt <= gw_end_dt:
        #         gw_ts_clipped.append(
        #             {
        #                 "datetime": item["datetime"],
        #                 "value": item.get("head"),
        #             }
        #         )

        # result = {
        #     "precipitation": {"timeseries": prec_ts_clipped},
        #     "groundwater": {"timeseries": gw_ts_clipped},
        # }
        result = {"test": "test"}
        response.outputs["timeseries_data"].data = json.dumps(result)
        #except Exception as e:
        #    res = {"errMsg": "ERROR: {}".format(e)}
        #    logger.exception(res)
        #    response.outputs["precipitation_groundwater_data"].data = json.dumps(res)
        return response

