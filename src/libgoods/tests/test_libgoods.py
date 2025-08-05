"""
tests for stuff in the main libgoods namespace

e.g. the stuff in __init__
"""
from pathlib import Path

from libgoods import Config


def test_config():
    """
    Not much here but we want to test what happens when we set a path
    """
    config = Config()
    config.archive_dir = "./"

    assert config.shoreline_dir is None
    assert isinstance(config.archive_dir, Path)



