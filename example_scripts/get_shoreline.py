#Get shoreline around Kalgon island from AK cusp dataset
#You'll need to point to the path for the shapefiles for this to work
#I have't decided where they should go

from pathlib import Path

from libgoods import shoreline

shpfile_path = Path(__file__).parents[1] / 'shoreline_data'
shpfile = shpfile_path / "AK_CUSP" / "AK_CUSP_polygon_20240221.shp"
bound_box = (-152.8,60.05,-151.05,60.92)
ofn = Path('output','Kalgon.bna')

bna_polys,levs = shoreline.load_polys_and_clip(shpfile,bound_box)
shoreline.format_for_bna(ofn,bna_polys,levs,dl=0)
