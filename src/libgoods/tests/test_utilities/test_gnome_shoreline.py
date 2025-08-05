
from libgoods.utilities.gnome_shoreline import GNOME_shoreline

from .conftest import DATA_DIR, OUTPUT_DIR


def test_init():
    """
    not testing much, but it should have some empty lists ..
    """
    gs = GNOME_shoreline()

    assert not gs.land_polys


def test_init_from_file():
    gs = GNOME_shoreline(DATA_DIR / "lake_erie_islands.bna")

    print(gs)

    assert len(gs.map_bounds) == 1
    assert len(gs.spillable_area) == 0
    assert len(gs.land_polys) == 10
    assert len(gs.other_polys) == 0


def test_read_bna():
    gs = GNOME_shoreline()
    gs.read_bna(DATA_DIR / "MapBounds_2Spillable2Islands2Lakes.bna")

    print(gs)

    assert len(gs.map_bounds) == 1
    assert len(gs.spillable_area) == 2
    assert len(gs.land_polys) == 2
    assert len(gs.other_polys) == 0


def test_write_bna():
    outfilename = OUTPUT_DIR / "temp_output.bna"
    outfilename.unlink(missing_ok=True)

    gs = GNOME_shoreline(DATA_DIR / "MapBounds_2Spillable2Islands2Lakes.bna")

    print(gs)

    gs.write_bna(outfilename)

    assert outfilename.is_file()

    # re-read it:
    gs2 = GNOME_shoreline(outfilename)

    assert gs.is_similar(gs2)
