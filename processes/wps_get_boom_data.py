# -*- coding: utf-8 -*-
#  Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2025 Deltares for Project A27.
#   Main contributors:
#   Ioanna Micha (ioanna.micha@deltares.nl)
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

# Single clicked tree:
# http://localhost:5000/wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_boom_data&datainputs=boominfo={"boomnaams":["1FS"]}
#
# Multiple trees (future multi-select):
# http://localhost:5000/wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_boom_data&datainputs=boominfo={"boomnaams":["1FS","9FS","3Qu"]}
#
# Production:
# https://a27.openearth.nl/wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_boom_data&datainputs=boominfo={"boomnaams":["1FS"]}

import json
import logging

from pywps import Format
from pywps.app import Process
from pywps.app.Common import Metadata
from pywps.inout.inputs import ComplexInput
from pywps.inout.outputs import ComplexOutput

from .utils import get_boom_data

logger = logging.getLogger("PYWPS")


class WpsGetBoomData(Process):
    """
    Returns tree-health graph data for one or more trees.

    Input JSON:
        {
            "boomnaams": ["1FS"]  // list of boomcode or boomnaam strings
        }

    Output JSON shape:
        {
            "selected_tree": "1FS",
            "y_axis": { "min": 0, "max": 8, "labels": ["Dood", …, "Goed"] },
            "group_averages": [
                { "group": "Beuken", "visible_by_default": true, "timeseries": […] }
            ],
            "trees": [
                { "tree": "1FS", "tree_name": "1FS", "group_that_belongs": "Beuken",
                  "visible_by_default": true, "timeseries": […] }
            ]
        }

    Multi-tree selection is supported by passing more entries in "boomnaams".
    """

    def __init__(self):
        inputs = [
            ComplexInput(
                "boominfo",
                'Tree info as JSON: {"boomnaams": [...]}',
                supported_formats=[Format("application/json")],
            )
        ]
        outputs = [
            ComplexOutput(
                identifier="boom_data",
                title="Tree health timeseries",
                supported_formats=[Format("application/json")],
            )
        ]

        super(WpsGetBoomData, self).__init__(
            self._handler,
            identifier="wps_get_boom_data",
            version="1.0.0",
            title="Retrieve tree health timeseries for one or more trees",
            abstract=(
                "Returns tree-health graph data for the requested trees. "
                "The database response includes the selected tree, y-axis metadata, "
                "relevant group averages and requested tree timeseries."
            ),
            profile="",
            metadata=[
                Metadata("WpsGetBoomData"),
                Metadata("wps_get_boom_data"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False,
        )

    def _handler(self, request, response):
        try:
            boominfo = json.loads(request.inputs["boominfo"][0].data)
            boomnaams = boominfo["boomnaams"]

            response.outputs["boom_data"].data = get_boom_data(boomnaams)
        except Exception as e:
            res = {"errMsg": "ERROR: {}".format(e)}
            logger.exception(res)
            response.outputs["boom_data"].data = json.dumps(res)
        return response
