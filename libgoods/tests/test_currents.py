"""
test the top level API
"""

import pytest

from libgoods import currents

def test_list_models_currents():
    model_info = currents.list_models('currents')

    # probably should test more, but this is something
    assert len(model_info) == 2


def test_list_models_winds():
    with pytest.raises(NotImplementedError):
        model_info = currents.list_models('winds')


def test_list_models_garbage():
    with pytest.raises(ValueError):
        model_info = currents.list_models('garbage')



