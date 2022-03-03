"""
tests of the data models base class
"""

import pytest

from libgoods.data_model import DataSource


def test_DataSource_get_metadata():
    md = DataSource().get_metadata()

    assert md.keys() == {
        "identifier",
        "name",
        "bounding_box",
        "bounding_poly",
        "info_text",
        "forecast_available",
        "hindcast_available",
        "environmental_parameters",
    }
