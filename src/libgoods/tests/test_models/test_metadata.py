"""
tests of the metadata classes - these test construction but nothing else at present
"""

from pathlib import Path

import numpy as np

from libgoods.models import YAML_DIR
from libgoods.models.metadata import Metadata

# using ngofs2 as the prototype
yaml_file = YAML_DIR / "ngofs2.yaml"

HERE = Path(__file__).parent
OUTPUT_DIR = HERE / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def test_from_yaml():
    meta = Metadata.from_yaml(yaml_file)
    assert meta.identifier == "NGOFS2"
    assert meta.bounding_box == (
        262.1488342285156,
        21.80545997619629,
        274.262451171875,
        30.78022003173828,
    )


def test_init_from_wkt():
    """
    if you init it with WKT for the bounding polygon, you should get nested tuples (numpy array?)
    """

    # WKT = "POLYGON ((270.6807861328125 30.374494552612305, 271.00927734375 30.4280948638916, 271.0753173828125 30.43028450012207, 271.1471252441406 30.429607391357422), 270.6807861328125 30.374494552612305)"  # noqa

    WKT = """POLYGON ((270.6807861328125 30.374494552612305,
                       262.9354248046875 24.568058013916016,
                       268.0373229980469 29.816688537597656,
                       268.80035400390625 30.50692367553711,
                       270.6807861328125 30.374494552612305))"""

    meta = Metadata(bounding_poly=WKT)

    print(meta.bounding_poly)

    assert isinstance(meta.bounding_poly, tuple)
    for p in meta.bounding_poly:
        assert len(p) == 2
        assert isinstance(p, tuple)


def test_init_from_tuples():
    """
    if you init it with nested tuples, it should work.
    """

    bounding_poly = np.array([
        (270.6807861328125, 30.374494552612305),
        (262.9354248046875, 24.568058013916016),
        (268.0373229980469, 29.816688537597656),
        (268.80035400390625, 30.50692367553711),
        (270.6807861328125, 30.374494552612305),
    ])

    meta = Metadata(bounding_poly=bounding_poly)

    print(meta.bounding_poly)

    assert isinstance(meta.bounding_poly, tuple)
    for p in meta.bounding_poly:
        assert len(p) == 2
        assert isinstance(p, tuple)

    bounding_poly = (
        (270.6807861328125, 30.374494552612305),
        (262.9354248046875, 24.568058013916016),
        (268.0373229980469, 29.816688537597656),
        (268.80035400390625, 30.50692367553711),
        (270.6807861328125, 30.374494552612305),
    )


def test_as_pyson():
    meta = Metadata(
        identifier="AN_ID",
        name="An example model",
        long_name="An example model -- used to test and explaining the metadata required",
        html_desc=("<html> <b>An example model</b> -- "
                   "used to test and explaining the "
                   "metadata required </html>"),
        regional=True,
        bounding_box=(-20, 30, -45, 10),
        bounding_poly=(
            (270.6807861328125, 30.374494552612305),
            (262.9354248046875, 24.568058013916016),
            (268.0373229980469, 29.816688537597656),
            (268.80035400390625, 30.50692367553711),
            (270.6807861328125, 30.374494552612305),
        ),
        example_bbox=(-10, 20, -40, 5),
    )

    pyson = meta.as_pyson()

    meta2 = Metadata(**pyson)

    assert meta == meta2


def test_to_yaml():
    meta = Metadata(
        identifier="AN_ID",
        name="An example model",
        long_name="An example model -- used to test and explaining the metadata required",
        html_desc=("<html> <b>An example model</b> -- "
                   "used to test and explaining the "
                   "metadata required </html>"),
        regional=True,
        bounding_box=(-20, 30, -45, 10),
        bounding_poly=(
            (270.6807861328125, 30.374494552612305),
            (262.9354248046875, 24.568058013916016),
            (268.0373229980469, 29.816688537597656),
            (268.80035400390625, 30.50692367553711),
            (270.6807861328125, 30.374494552612305),
        ),
        example_bbox=(-10, 20, -40, 5),
    )

    outfile = OUTPUT_DIR / "test_metadata.yaml"

    meta.to_yaml(OUTPUT_DIR / "test_metadata.yaml")

    assert outfile.is_file()

    meta2 = Metadata.from_yaml(outfile)

    assert meta == meta2
