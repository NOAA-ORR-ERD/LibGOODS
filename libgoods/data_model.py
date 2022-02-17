"""
Base classes for the core data models

Static Model metadata:

{'name': self.name,
 'bounding_box': self.bounding_box, # (lower_left, upper_right)
 'bounds': self.bounds, # thinned polygon ~ 100 points
 'info_text': self.info_text
 'forecast_available': True
 'hindcast_availalbe': False
 'environmental_parameters': ## eg: ['surface winds', 'sea surface temperature']
}

Environmental Parameters will be one of these:
    - This is to make sure we use the same vocabulary everywhere
    - Draft list -- needs much cleaning up.
        surface winds
        surface currents
        3D currents
        sea surface temperature
        ice data
        ...


Dynamic Model Information:

Model.available_times
Model.subset_info(query_params) => info about subset
  - X, Y, Z, T dimensions
  - Estimated File Size
"""

import dataclasses


# These are the pre-defined environmental parameters
# this list will need work!
ENVIRONMENTAL_PARAMETERS = {
    "surface winds"
    "surface currents"
    "3D currents"
    "sea surface temperature"
    "ice data"
}

# fixme: we should have a short identifier as well, e.g "hycom", etc.
@dataclasses.dataclass
class Metadata:
    identifier: str = ""
    name: str = ""
    bounding_box: tuple = ()
    bounding_poly: tuple = ()
    info_text: str = ""
    forecast_available: bool = True
    hindcast_available: bool = False
    environmental_parameters: list = dataclasses.field(default_factory=list)
    """
    class to hold the core meta data for a data source

    This could include validation, or ...

    Currently this has defaults for everything, but maybe it should require everything?
    """


class DataSource:
    """
    core functionality for all data sources
    """

    # Metadata required by all Data sources
    metadata = Metadata()

    def get_metadata(self):
        """
        Eeturns a dict of the "static" metadata for this data source
        """
        return dataclasses.asdict(self.metadata)

    def get_model_info(self):
        """
        Returns a dict of both the static and dynamic metadata

        e.g. available times

        -- will there be other info?
          - maybe model meta-data -- when it was run, etc.
          - or is all that in the resulting data files?
        """
        info = self.get_metadata()
        info["available_times"] = {
            "forecast:": self.get_available_times("forecast"),
            "hindcast:": self.get_available_times("hindcast"),
        }

    def get_available_times(self, cast_type):
        """
        returns the available times for this model as of right now

        This requires reaching out to the source
        """
        raise NotImplementedError
