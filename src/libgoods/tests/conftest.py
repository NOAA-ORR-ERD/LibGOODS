"""
Fixtures for libgoods tests
"""

from pathlib import Path

import pytest

HERE = Path(__file__).parent

@pytest.fixture
def TEST_FILES():
    return HERE / "example_data_files"

@pytest.fixture
def OUTPUT_DIR():
    return HERE / "output_dir"
