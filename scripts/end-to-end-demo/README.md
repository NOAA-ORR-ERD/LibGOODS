# End-to-end demo

## Summary

The demo script `demo.py` demonstrates the end-to-end workflow of:

- Model query and serialization using `model_catalog`
- A sample PyGnome simulation using the model results saved from the previous step

## Requirements

The demo script requires the packages specified in `model_catalog.py` to be installed.

PyGnome is not installable via conda, pip, and cannot be installed via `pip+https` from the PyGnome repository,
so that must be installed manualy (See https://github.com/NOAA-ORR-ERD/PyGnome).

## Running the demo

```bash
bash -i ./end-to-end-demo.sh
```

The demo will call two Python scripts run in conda environments activated within the script.


## Problems

Models from `model_catalog` demos unsupported by gnome:
1. CBOFS_REGULAR_GRID
2. CBOFS
