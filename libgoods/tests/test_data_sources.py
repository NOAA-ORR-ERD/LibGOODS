"""
test the top level API
"""

import pytest

from libgoods import data_sources

def test_list_models_currents():
    model_info = data_sources.list_models()

    # probably should test more, but this is something
    assert len(model_info) == 3

