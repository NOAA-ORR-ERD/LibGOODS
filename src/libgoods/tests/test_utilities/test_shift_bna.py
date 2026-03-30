import numpy as np

from libgoods.scripting import shift_bna
from libgoods.utilities.haz_files import ReadBNA

from .conftest import DATA_DIR, OUTPUT_DIR


def test_shift():
    infile = DATA_DIR / "lake_erie_islands.bna"
    outfile = OUTPUT_DIR / "lake_erie_islands_shifted.bna"

    outfile.unlink(missing_ok=True)

    shift_bna.shift_bna(infile, outfile, "0--360")

    polys = ReadBNA(outfile)
    for poly in polys:
        assert np.all(poly[0][:, 0] >= 0)
        assert np.all(poly[0][:, 0] < 360)
