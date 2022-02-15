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
ENVIRONMENTAL_PARAMETERS = {'surface winds'
                            'surface currents'
                            '3D currents'
                            'sea surface temperature'
                            'ice data'}

# fixme: we should have a short identifier as well, e.g "hycom", etc.
@dataclasses.dataclass
class Metadata:
    name: str
    bounding_box: tuple
    bounds: tuple
    info_text: str
    forecast_available: bool
    hindcast_available: bool
    environmental_parameters: list
    """
    class to hold the core meta data for a data source

    this could include validation, or ...
    """



class DataSource:
    """
    core functionality for all data sources
    """
    # Metadata required by all Data sources
    metadata: Metadata = None

    def get_metadata(self):
        """
        returns a dict of the metadata for this data source
        """
        return dataclasses.asdict(self.metadata)

    def get_model_info(self):
        info = self.get_metadata()
        info['available_times'] = self.get_available_times()

    def get_available_times(self):
        """
        returns the available times for this model as of right now

        This requires reaching out to the source
        """
        raise NotImplementedError



