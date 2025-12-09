# -*- coding: utf-8 -*-
#  Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2025 Deltares for Project A27.
#   Main contributors: 
#   Ioanna Micha (ioanna.micha@deltares.nl)
#   Gerrit Hendriksen (Gerrit Hendriksen@deltares.nl)
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
#http://localhost:5000/wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_precipitation_data&datainputs=locationinfo={%22x%22:5.207047,%22y%22:52.066449,%20%22start_date%22:%22%22,%22end_date%22:%22%22}

import json
from pywps import Format
from pywps.app import Process
from pywps.inout.outputs import LiteralOutput
from pywps.app.Common import Metadata
from pywps.inout.inputs import ComplexInput
from pywps.inout.outputs import ComplexOutput
from .utils import get_precipitation_data
import logging
logger = logging.getLogger("PYWPS")

class WpsGetPrecipitationData(Process):
    def __init__(self):
        inputs = [ComplexInput('locationinfo', 'X, Y, StartDate and EndDate',
                         supported_formats=[Format('application/json')])
        ]
        outputs = [
            ComplexOutput(identifier="precipitation_data", title="Precipitation data", supported_formats=[Format('application/json')])
        ]

        super(WpsGetPrecipitationData, self).__init__(
            self._handler,
            identifier="wps_get_precipitation_data",
            version="1.0.0",
            title="Retrieve timeseries precipitation data for selected coordinates (RD New EPSG:28992) for any date range (start_date and/or end_date can be empty strings)",
            abstract="Retrieve timeseries precipitation data for selected coordinates (RD New EPSG:28992) for any date range (start_date and/or end_date can be empty strings). ",
            profile="",
            metadata=[
                Metadata("WpsGetPrecipitationData"),
                Metadata("Wps_get_precipitation_data"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False,
        )

    def _handler(self, request, response):
        
        try:
            locationinfo = request.inputs['locationinfo'][0].data
            locationinfo_json = json.loads(locationinfo)

            # x, y coordinates in RD New (EPSG:28992)
            x = locationinfo_json['x']
            y = locationinfo_json['y']
            start_date = locationinfo_json['start_date']
            end_date = locationinfo_json['end_date']
        

            response.outputs["precipitation_data"].data = get_precipitation_data(x, y, start_date, end_date)
        except Exception as e:
                res = { 'errMsg' : 'ERROR: {}'.format(e)}
                logger.info(res)     
                response.outputs["precipitation_data"].data = "Something went very wrong, please check logfile"
        return response
