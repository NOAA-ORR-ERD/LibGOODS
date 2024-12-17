
from .coops_fvcom import NGOFS2, LMHOFS
from .coops_roms import DBOFS, WCOFS, CBOFS
from .doppio import DOPPIO

ALL_MODELS = {"NGOFS2": NGOFS2,
              "LMHOFS": LMHOFS,
              "DBOFS": DBOFS,
              "WCOFS": WCOFS,
              "CBOFS": CBOFS,
              "DOPPIO": DOPPIO,
              }


def get_models():
    """
    To Do: add filtering, selection, etc?

    get the model objects for all models
    """
    return ALL_MODELS


