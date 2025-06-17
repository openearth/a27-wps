# -*- coding: utf-8 -*-
# Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2022 Deltares
#       Ioanna Micha
#       ioanna.micha@deltares.nl
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


from pywps.app import Process, Format
from pywps.inout.outputs import LiteralOutput
from pywps.app.Common import Metadata
from pywps.inout.outputs import ComplexOutput
#TODO: still to be implemented. 
class GetLocationData(Process):
    def __init__(self):
        inputs = []
        outputs = [
            ComplexOutput(identifier="location_data", title="Location data", supported_formats=[Format('application/json')])
        ]

        super(GetLocationData, self).__init__(
            self._handler,
            identifier="get_location_data",
            version="1.0.0",
            title="Retrieve location data",
            abstract="The process retrieves location data based on the location identifier.",
            profile="",
            metadata=[
                Metadata("GetLocationData"),
                Metadata("get_location_data"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False,
        )

    def _handler(self, request, response):
        response.outputs["answer"].data = "42"
        return response
