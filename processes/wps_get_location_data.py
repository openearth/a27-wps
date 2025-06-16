#TODO to be modified to read location data given the location id.
from pywps.app import Process, Format
from pywps.inout.outputs import LiteralOutput
from pywps.app.Common import Metadata
from pywps.inout.outputs import ComplexOutput

class ReadLocations(Process):
    def __init__(self):
        inputs = []
        outputs = [
            ComplexOutput(identifier="locations", title="A27 locations", supported_formats=[Format('application/json')])
        ]

        super(ReadLocations, self).__init__(
            self._handler,
            identifier="read_locations",
            version="1.0.0",
            title="Retrieve A27 locations",
            abstract="The process retrieves the A27 locations from the database",
            profile="",
            metadata=[
                Metadata("ReadLocations"),
                Metadata("read_locations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=False,
            status_supported=False,
        )

    def _handler(self, request, response):
        response.outputs["answer"].data = "42"
        return response
