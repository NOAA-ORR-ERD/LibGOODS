from pathlib import Path 

import numpy as np

from libgoods.utilities.haz_files import ReadBNA
from libgoods.scripting import shift_bna

import pytest

HERE = Path(__file__).parent

def test_shift():
    infile = HERE / "lake_erie_islands.bna"
    outfile = HERE / "lake_erie_islands_shifted.bna"

    outfile.unlink(missing_ok=True)

    shift_bna.shift_bna(infile, outfile, "0--360")

    polys = ReadBNA(outfile)
    for poly in polys:
        assert np.all(poly[0][:,0] >= 0)
        assert np.all(poly[0][:,0] < 360)



