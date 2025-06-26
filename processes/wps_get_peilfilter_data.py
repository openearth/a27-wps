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
# http://localhost:5000/wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_peilfilter_data&datainputs=peilfilterinfo={"peilfilterid":436, "start_date":"2013-06-01 00:00:00","end_date":"2013-12-31 23:59:59"}
# https://a27.openearth.nl/wps?service=wps&request=Execute&version=2.0.0&Identifier=wps_get_peilfilter_data&datainputs=peilfilterinfo={"peilfilterid":436, "start_date":"2013-06-01 00:00:00","end_date":"2013-12-31 23:59:59"}

import json
from pywps import Format
from pywps.app import Process
from pywps.inout.outputs import LiteralOutput
from pywps.app.Common import Metadata
from pywps.inout.inputs import ComplexInput
from pywps.inout.outputs import ComplexOutput
from .utils import get_data
import logging
logger = logging.getLogger("PYWPS")


class WpsGetPeilfilterData(Process):
    def __init__(self):
        inputs = [ComplexInput('peilfilterinfo', 'Peilfilterinfo as peilfilterId, StartDate and EndDate',
                         supported_formats=[Format('application/json')])
        ]
        outputs = [
            ComplexOutput(identifier="peilfilter_data", title="Peilfilter data", supported_formats=[Format('application/json')])
        ]

        super(WpsGetPeilfilterData, self).__init__(
            self._handler,
            identifier="wps_get_peilfilter_data",
            version="1.0.0",
            title="Retrieve timeseries data for selected peilfilter wihtin specifiek period",
            abstract="Retrieve timeseries data for selected peilfilter wihtin specifiek period.",
            profile="",
            metadata=[
                Metadata("WpsGetPeilfilterData"),
                Metadata("Wps_get_peilfilter_data"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False,
        )

    def _handler(self, request, response):
        
        try:
            peilfilterinfo = request.inputs['peilfilterinfo'][0].data
            peilfilterinfo_json = json.loads(peilfilterinfo)

            # peilfilterid
            peilfilterid= peilfilterinfo_json['peilfilterid']
            start_date  = peilfilterinfo_json['start_date']
            end_date    = peilfilterinfo_json['end_date']
            logger.info('provided input', peilfilterid,start_date,end_date)

            #response.outputs["peilfilter_data"].data = "42"
            response.outputs["peilfilter_data"].data = get_data(peilfilterid,start_date,end_date)
        except Exception as e:
            res = { 'errMsg' : 'ERROR: {}'.format(e)}
            logger.info(res)
            #response.outputs['jsonstimeseries'].data = json.dumps(res)	        
            response.outputs["peilfilter_data"].data = "Something went very wrong, please check logfile"
        return response
