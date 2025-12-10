# set up the data dirs: OUTPUT_DIR

from pathlib import Path

HERE = Path(__file__).parent
DATA_DIR = HERE / "data_files"

OUTPUT_DIR = HERE / "output"
# make sure it exists
OUTPUT_DIR.mkdir(exist_ok=True)
