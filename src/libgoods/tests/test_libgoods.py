"""
tests for stuff in the main libgoods namespace

e.g. the stuff in __init__
"""


from pathlib import Path

from libgoods import Config, UnsetConfigError

import pytest

def test_config_path():
    """
    Not much here but we want to test what happens when we set a path
    """
    config = Config()
    config.archive_dir = "./"

    assert isinstance(config.archive_dir, Path)

def test_config_None():
    """
    Not much here but we want to test what happens when we set a path
    """
    config = Config()
    config.archive_dir = "./"

    # This is no longer raising an error but leaving test here in case we change our minds

    assert config.shoreline_dir is None

"""     with pytest.raises(UnsetConfigError):
        d = config.shoreline_dir """




