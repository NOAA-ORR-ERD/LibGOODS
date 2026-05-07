
from .base import BaseModel
from .metadata import Metadata


class DummyModel(BaseModel):
    """
    A Dummy model with all static info

    Useful for testing the API, the WebAPI, etc.
    """
    metadata = Metadata(
        identifier="DUMMY",
        name="Static Dummy Model",
        long_name="Dummy regional model with all static info for use in tests",
        html_desc="<!DOCTYPE html><html><body><p>Nothing to see here</p></body></html>",
        regional=True,
        bounding_box=((236.978, 37.427), (238.319, 38.2120)),
        # note -- these are from SFBOFS, but with most of the bounding poly removed, so may be wonky
        bounding_poly=((237.824, 38.043), (237.801, 38.054), (237.797, 38.055),
                       (237.786, 38.057), (237.774, 38.057), (237.766, 38.058),
                       (237.744, 38.052), (237.844, 38.025), (237.841, 38.025),
                       (237.835, 38.028), (237.832, 38.03), (237.824, 38.043)),
        example_bbox=((237.1, 37.9), (237.5, 38.1)),
        env_params=None,
        start="2026-01-01T00:00:00",
        end="2026-02-24T00:00:00",
        actual_start="2026-02-01T00:00:00",
        actual_end="2026-02-28T00:00:00",
    )
    # this should get overwritten by all subclasses
    access = None

    standard_names = {}

    # def __init__(self, is3d=True):
    #     # add the environmental_params to metadata
    #     self.is3d = is3d
    #     self.metadata.env_params = self.env_params

