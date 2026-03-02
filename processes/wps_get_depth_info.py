# -*- coding: utf-8 -*-
#  Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2025 Deltares for Project A27.
#   Main contributors:
#   Ioanna Micha (ioanna.micha@deltares.nl)
#  
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
# Sign up to recieve regular updates of this function, and to contribute
# your own tools.

# test and production requests
# http://localhost:5000/wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_depth_info&datainputs=peilfilter_ids={"peilfilter_ids":[2000,2001]}
# https://a27.openearth.nl/wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_depth_info&datainputs=peilfilter_ids={"peilfilter_ids":[2000,2001]}

import json
import logging
from pywps import Format
from pywps.app import Process
from pywps.app.Common import Metadata
from pywps.inout.inputs import ComplexInput
from pywps.inout.outputs import ComplexOutput

from .utils import get_depth_info

logger = logging.getLogger("PYWPS")


class WpsGetDepthInfo(Process):
    def __init__(self):
        inputs = [
            ComplexInput(
                "peilfilter_ids",
                "Peilfilter IDs as array",
                supported_formats=[Format("application/json")],
            )
        ]
        outputs = [
            ComplexOutput(
                identifier="depth_info",
                title="Depth info",
                supported_formats=[Format("application/json")],
            )
        ]

        super(WpsGetDepthInfo, self).__init__(
            self._handler,
            identifier="wps_get_depth_info",
            version="1.0.0",
            title="Retrieve depth info for selected peilfilters",
            abstract="Retrieve depth info for the given peilfilter IDs.",
            profile="",
            metadata=[
                Metadata("WpsGetDepthInfo"),
                Metadata("wps_get_depth_info"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False,
        )

    def _handler(self, request, response):
        try:
            peilfilter_ids_data = request.inputs["peilfilter_ids"][0].data
            peilfilter_ids_json = json.loads(peilfilter_ids_data)
            peilfilter_ids = peilfilter_ids_json.get("peilfilter_ids")
            logger.info("provided input peilfilter_ids=%s", peilfilter_ids)

            response.outputs["depth_info"].data = get_depth_info(peilfilter_ids)
        except Exception as e:
            res = {"errMsg": "ERROR: {}".format(e)}
            logger.info(res)
            response.outputs["depth_info"].data = json.dumps(res)
        return response
