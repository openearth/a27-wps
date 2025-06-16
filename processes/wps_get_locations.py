from pywps import Format
from pywps.app import Process
from pywps.inout.outputs import LiteralOutput
from pywps.app.Common import Metadata
from pywps.inout.outputs import ComplexOutput

class WpsGetLocations(Process):
    def __init__(self):
        inputs = []
        outputs = [
            ComplexOutput(identifier="locations", title="A27 locations", supported_formats=[Format('application/json')])
        ]

        super(WpsGetLocations, self).__init__(
            self._handler,
            identifier="wps_get_locations",
            version="1.0.0",
            title="Retrieve A27 locations",
            abstract="The process retrieves the A27 locations from the database",
            profile="",
            metadata=[
                Metadata("GetLocations"),
                Metadata("get_locations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False,
        )

    def _handler(self, request, response):
        response.outputs["locations"].data = "locations"
        return response
