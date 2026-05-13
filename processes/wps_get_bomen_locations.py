# -*- coding: utf-8 -*-
#  Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2026 Deltares for Project A27.
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

# http://localhost:5000/wps?service=WPS&request=Execute&version=1.0.0&identifier=wps_get_bomen_locations
# https://a27.openearth.nl/wps?service=WPS&request=Execute&version=1.0.0&identifier=wps_get_bomen_locations

import json
import logging

from pywps import Format
from pywps.app import Process
from pywps.app.Common import Metadata
from pywps.inout.outputs import ComplexOutput

from .utils import get_bomen

logger = logging.getLogger("PYWPS")


class WpsGetBomenLocations(Process):
    """Returns all monitored trees as a GeoJSON FeatureCollection.
    Intended to be called once at FE startup to populate the map layer.
    """

    def __init__(self):
        inputs = []
        outputs = [
            ComplexOutput(
                identifier="bomen_locations",
                title="Tree locations GeoJSON",
                supported_formats=[Format("application/json")],
            )
        ]

        super(WpsGetBomenLocations, self).__init__(
            self._handler,
            identifier="wps_get_bomen_locations",
            version="1.0.0",
            title="Retrieve tree (boom) locations",
            abstract=(
                "Returns all monitored trees as a GeoJSON FeatureCollection. "
                "Each feature carries boom_id, boomcode, boomnaam and soort_group "
                "as properties. Call once at application startup."
            ),
            profile="",
            metadata=[
                Metadata("WpsGetBomenLocations"),
                Metadata("wps_get_bomen_locations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False,
        )

    def _handler(self, request, response):
        try:
            response.outputs["bomen_locations"].data = get_bomen()
        except Exception as e:
            res = {"errMsg": "ERROR: {}".format(e)}
            logger.exception(res)
            response.outputs["bomen_locations"].data = json.dumps(res)
        return response
